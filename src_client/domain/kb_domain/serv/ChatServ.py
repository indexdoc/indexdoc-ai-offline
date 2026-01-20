import json
from collections import defaultdict
from typing import Dict, List, Any

from openai import OpenAI

import client_global
from domain.kb_domain.dao import ChatHistoryDao, DocumentDao

PROMPT = """
<指令>
    1. 角色定位：
       你是一名具备深厚领域知识和信息检索能力的 AI 助手，能够从提供的“已知信息”中精准提取，并以学术、专业的方式组织输出。
    2. 任务目标：
       - 回答用户的具体问题，或根据请求撰写报告、分析、总结等；
       - 尽量基于“已知信息”内容。
    3. 语言风格与深度
        - 语气：正式、学术化或行业白皮书风格；
        - 用词：专业术语准确，避免口语化表达；
        - 深度：
          - 若问题需宏观层面回答，需提供整体框架与逻辑脉络；
          - 若需微观层面探讨，需引入具体数据、案例或图表（可用文字描述）。
</指令>
"""


# 知识库对话
async def knowledge_base_chat(request, query, chat_id, knowledge_base_id, doc_id, model, temperature, max_tokens,
                              stream):
    # 获取历史记录
    history = ChatHistoryDao.get_all({'chat_id': chat_id})[:-6]

    # 匹配知识库文件
    if knowledge_base_id == '' and doc_id == '':
        docs = []
    elif doc_id != '':
        docs = [DocumentDao.get_by_id(doc_id)]
    else:
        search_result_list = search_docs_by_vector(query, knowledge_base_id)
        docs = []
        for search_result in search_result_list:
            # 根据查询分片的下标取出对应的文本内容
            docs.append(DocumentDao.get_doc_by_chunk_index(search_result['document_id'], search_result['chunk_index_list']))

    # 前端文件列表
    source_documents = []
    current_length = 0
    context_list = []
    for index, doc in enumerate(docs):
        temp_entry = {"文件名": doc['file_name'], "内容": doc['file_content']}
        temp_json = json.dumps(temp_entry)
        if current_length + len(temp_json) > 45000:
            # 超出长度且是第一个文件，截取部分
            if len(context_list) == 0 and len(docs) > 0:
                temp_entry = {"文件名": doc['file_name'], "内容": doc['file_content'][:45000]}
            else:
                # 如果加入新文档会超出长度限制，停止添加
                break
        context_list.append(temp_entry)
        current_length += len(temp_json)
        url = doc['location_path']
        text = f"""<a href="openfile://{url}">出处 [{index + 1}] {url}</a>"""
        source_documents.append(text)
    # 没有找到相关文档
    if len(source_documents) == 0:
        source_documents.append(
            f"未找到相关文档,该回答为大模型自身能力解答！")

    context = f'已知信息：{json.dumps(context_list)}'

    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": f"{context}"}
    ]
    messages.extend(
        {"role": 'user' if his['role_name'] == 'user' else 'assistant', "content": his['message']} for his in history)
    messages.append({"role": "user", "content": f"问题：{query}"})

    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url=client_global.ai_base_url,
        # 从环境变量中获取您的 API Key
        api_key=client_global.ai_api_key,
    )
    if stream:
        stream = client.chat.completions.create(
            # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            # 响应内容是否流式返回
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            token = chunk.choices[0].delta.content
            request.write(f"data: {json.dumps({'type': 'data', 'data': token}, ensure_ascii=False)}\n\n")
            await request.flush()
        request.write(f"data: {json.dumps({'type': 'docs', 'data': source_documents}, ensure_ascii=False)}\n\n")
        request.write(f"data: {json.dumps({'type': 'finish', 'data': ''}, ensure_ascii=False)}\n\n")
        await request.flush()


def search_docs_by_vector(query, knowledge_base_id,
                          # 分片权重值
                          chunk_weight: float = 0.7,
                          # 文件名权重值
                          filename_weight: float = 0.3,
                          # 分数计算方法
                          # max 取单片最大值,
                          # mean 同文档从筛选出的分片中取平均值,
                          # weighted_max 同文档每片加权后计算后取最大值,
                          # top_k_mean 同文档取最高的几片的平均值
                          chunk_agg_method: str = 'weighted_max',
                          # 对应top_k_mean方法的top数量
                          top_k_chunks: int = 3,
                          # 最低分，去掉低于改分数的文档
                          min_score: float = 0.6
                          ):
    from domain.kb_domain.serv.VectorModel.VectorLoader import EmbeddingLoader
    embedding = EmbeddingLoader()
    # query_vector = client_global.embedding_model.encode(query)
    query_vector = embedding.encode(query)
    # 1、获取切片的余弦值，使用数据库从大到小排序取前X个，存为一个list（docID，切片的序号，切片的向量，切片的余弦值）
    # 返回值示例
    # {'document_id': 2510211150409282, 'chunk_index': 0, 'chunk_vector': [...], 'cosine_similarity': 0.766421729917693}
    chunk_cosine_list = DocumentDao.get_chunk_cosine(query_vector, knowledge_base_id)

    # 2、获取文件名的余弦值，存为一个list（docid，文件名，文件名的余弦值）
    # 返回值示例
    # [{'document_id': 2510211150429293, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'cosine_similarity': 0.6601183583082879}]
    file_name_cosine_list = DocumentDao.get_file_name_cosine(query_vector, knowledge_base_id)

    # 3、设计算法，获取相似度最高的文件。
    return rank_documents_by_similarity(chunk_cosine_list, file_name_cosine_list, chunk_weight, filename_weight,
                                        chunk_agg_method, top_k_chunks, min_score)


def rank_documents_by_similarity(
        chunk_cosine_list: List[Dict[str, Any]],
        file_name_cosine_list: List[Dict[str, Any]],
        chunk_weight: float = 0.7,
        filename_weight: float = 0.3,
        chunk_agg_method: str = 'weighted_max',
        top_k_chunks: int = 3,
        min_score: float = 0.6
) -> List[Dict[str, Any]]:
    if not chunk_cosine_list and not file_name_cosine_list:
        return []

    # 归一化权重
    total_weight = chunk_weight + filename_weight
    if total_weight == 0:
        cw, fw = 0.5, 0.5
    else:
        cw = chunk_weight / total_weight
        fw = filename_weight / total_weight

    doc_to_file = {}
    for item in file_name_cosine_list:
        if 'document_id' in item:
            doc_to_file[item['document_id']] = item.get('file_name', '')
    for item in chunk_cosine_list:
        if 'document_id' in item and item['document_id'] not in doc_to_file:
            doc_to_file[item['document_id']] = item.get('file_name', '')

    # 按 document_id 聚合：相似度列表 + chunk_index 列表
    doc_chunks = defaultdict(list)  # 存 similarity
    doc_chunk_indices = defaultdict(list)  # 存 chunk_index

    for item in chunk_cosine_list:
        doc_id = item.get('document_id')
        if doc_id is None:
            continue
        sim = float(item.get('cosine_similarity', 0.0))
        idx = item.get('chunk_index', -1)  # 若无 chunk_index，默认 -1

        doc_chunks[doc_id].append(sim)
        doc_chunk_indices[doc_id].append(idx)

    # 聚合 chunk 相似度（用于 combined score）
    doc_chunk_score = {}
    for doc_id, scores in doc_chunks.items():
        if not scores:
            s = 0.0
        else:
            sorted_scores = sorted(scores, reverse=True)
            if chunk_agg_method == 'max':
                s = max(scores)
            elif chunk_agg_method == 'mean':
                s = sum(scores) / len(scores)
            elif chunk_agg_method == 'sum':
                s = sum(scores)
            elif chunk_agg_method == 'weighted_max':
                top_n = min(len(sorted_scores), top_k_chunks)
                weights = [0.5, 0.3, 0.2, 0.1, 0.05][:top_n]
                w_sum = sum(weights)
                if w_sum > 0:
                    weights = [w / w_sum for w in weights]
                s = sum(sc * w for sc, w in zip(sorted_scores[:top_n], weights))
            elif chunk_agg_method == 'top_k_mean':
                k = min(len(sorted_scores), top_k_chunks)
                s = sum(sorted_scores[:k]) / k
            else:
                s = max(scores)
        doc_chunk_score[doc_id] = s

    # 文件名相似度映射
    doc_filename_score = {
        item['document_id']: float(item.get('cosine_similarity', 0.0))
        for item in file_name_cosine_list
        if 'document_id' in item
    }

    # 合并所有 document_id
    all_doc_ids = set(doc_chunk_score.keys()) | set(doc_filename_score.keys())

    # 构建结果并过滤
    results = []
    for doc_id in all_doc_ids:
        chunk_sim = doc_chunk_score.get(doc_id, 0.0)
        filename_sim = doc_filename_score.get(doc_id, 0.0)
        combined = cw * chunk_sim + fw * filename_sim

        if combined < min_score:
            continue

        file_name = doc_to_file.get(doc_id, "unknown")
        chunk_indices = doc_chunk_indices.get(doc_id, [])

        results.append({
            'document_id': doc_id,
            'file_name': file_name,
            'combined_similarity': round(combined, 6),
            'chunk_index_list': chunk_indices  # 保留原始顺序的 chunk 索引
        })

    # 按综合得分降序排序
    results.sort(key=lambda x: x['combined_similarity'], reverse=True)
    return filter_documents_simple(results)

# 过滤文件列表，进行缩减
def filter_documents_simple(
        ranked_docs: List[Dict[str, Any]],
        min_docs: int = 5,
        max_docs: int = 10
) -> List[Dict[str, Any]]:
    """
    """
    if not ranked_docs:
        return []

    # 过滤0.75以上的文档
    filtered = [
        doc for doc in ranked_docs
        if doc['combined_similarity'] >= 0.75
    ]

    # 不足5个,返回所有文档(最多10个)
    if len(filtered) < min_docs:
        return ranked_docs[:max_docs]

    # 超过10个,截断
    return filtered[:max_docs]