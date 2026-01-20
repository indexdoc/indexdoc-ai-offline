import client_global
from domain.kb_domain.serv.DocLoad.LoaderFactory import LoaderFactory

import logging
import numpy as np
from typing import List
import re
import gc
import sys

# 文件加载并进行切片及向量化
def load_doc(document, max_chunk_cnt= 100):
    """
    文件加载、分片、向量化处理

    Args:
        document: 文档字典对象

    Returns:
        document: 处理后的文档字典对象
        :param max_chunk_cnt:
    """
    try:
        loader = LoaderFactory.from_file(document['location_path'])
        if loader.rtn['load_status']:
            # 读取成功，合成内容
            content = '\n'.join(loader.rtn['file_content'])
            document['file_content'] = content

            # 获取文件大小（用于动态调整策略）
            content_length = len(content)

            # 智能分片
            file_content_chunks = doc_spliter(content, content_length)
            logging.debug(f"文件 {document['location_path']} 开始向量化")
            # 批量向量化分片内容
            file_content_chunks_vector = client_global.embedding_model.encode(file_content_chunks[0:max_chunk_cnt])

            # 文件名向量化
            file_name_vector = client_global.embedding_model.encode(
                document['file_name']
            )
            logging.debug(f"✅ 文件 {document['location_path']} 向量化完成")
            # 写入内容
            document['file_name_vector'] = file_name_vector
            document['file_content_chunks'] = file_content_chunks
            document['file_content_chunks_vector'] = file_content_chunks_vector
            document['kb_load_state'] = '完成'

            # 清理内存
            del file_content_chunks_vector
            gc.collect()

        else:
            document['kb_load_state'] = '加载失败'

    except Exception as e:
        logging.error(f"向量化错误: {e}", exc_info=True)
        document['kb_load_state'] = '不支持'

    return document


def batch_vectorize_chunks(chunks: List[str], model, batch_size=32):
    """
    批量向量化文本片段，避免内存溢出

    Args:
        chunks: 文本片段列表
        model: 向量化模型
        batch_size: 每批处理的数量

    Returns:
        向量化结果的numpy数组
    """
    if not chunks:
        return np.array([])

    embeddings_list = []
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        try:
            # 向量化当前批次
            batch_embeddings = model.encode(
                batch,
                batch_size=min(batch_size, len(batch))
            )
            embeddings_list.append(batch_embeddings)

            # 每处理10个批次清理一次内存
            if (i // batch_size) % 10 == 0 and i > 0:
                gc.collect()

        except Exception as e:
            logging.error(f"批次 {i // batch_size} 向量化失败: {e}")
            # 失败时用零向量填充
            batch_embeddings = np.zeros((len(batch), model.get_sentence_embedding_dimension()))
            embeddings_list.append(batch_embeddings)

    # 合并所有批次的结果
    return np.vstack(embeddings_list)


def doc_spliter(text: str, text_length: int = None) -> List[str]:
    """
    智能文档分片，根据文档大小动态调整策略

    Args:
        text: 输入的长文档文本
        text_length: 文本长度（可选，用于优化性能）

    Returns:
        分割后的文本片段列表
    """
    if text_length is None:
        text_length = len(text)

    # 根据文档大小动态调整参数
    if text_length < 5000:  # 小文档 (<5KB)
        max_length = 512
        overlap = 50
        max_chunks = 50
    elif text_length < 50000:  # 中等文档 (<50KB)
        max_length = 800
        overlap = 80
        max_chunks = 150
    elif text_length < 200000:  # 大文档 (<200KB)
        max_length = 1024
        overlap = 100
        max_chunks = 300
    elif text_length < 1000000:  # 超大文档 (<1MB)
        max_length = 1536
        overlap = 150
        max_chunks = 500
    else:  # 巨型文档 (>1MB)
        max_length = 2048
        overlap = 200
        max_chunks = 800

    # 如果文本很短，直接返回
    if text_length <= max_length:
        return [text]

    # 按段落优先分片
    chunks = split_by_paragraphs(text, max_length, overlap)

    # 如果分片数量过多，进行二次优化
    if len(chunks) > max_chunks:
        chunks = optimize_chunks(chunks, max_chunks, max_length * 1.5)

    return chunks


def split_by_paragraphs(text: str, max_length: int, overlap: int) -> List[str]:
    """
    基于段落的智能分片

    Args:
        text: 输入文本
        max_length: 每个片段的最大长度
        overlap: 片段之间的重叠长度

    Returns:
        分割后的文本片段列表
    """
    # 按段落分割（优先双换行，其次单换行）
    paragraphs = text.split('\n\n')
    if len(paragraphs) <= 1:
        paragraphs = text.split('\n')

    # 过滤空段落
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return [text]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # 如果单个段落就超长，需要切分
        if len(para) > max_length:
            # 先保存当前累积的chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # 切分超长段落
            sub_chunks = split_long_paragraph(para, max_length, overlap)
            chunks.extend(sub_chunks)

        # 如果加上当前段落会超长
        elif len(current_chunk) + len(para) + 2 > max_length:  # +2 for \n\n
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para

        # 否则累积到当前chunk
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    # 保存最后一个chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    # 添加重叠
    if overlap > 0 and len(chunks) > 1:
        chunks = add_overlap(chunks, overlap)

    return chunks


def split_long_paragraph(para: str, max_length: int, overlap: int) -> List[str]:
    """
    切分超长段落（按句子）

    Args:
        para: 超长段落
        max_length: 最大长度
        overlap: 重叠长度

    Returns:
        切分后的片段列表
    """
    # 按句子分割，保留标点
    sentences = re.split(r'([.!?。！？;；]+)', para)

    # 重组句子和标点
    sents = []
    for i in range(0, len(sentences) - 1, 2):
        sent = sentences[i]
        if i + 1 < len(sentences):
            sent += sentences[i + 1]
        if sent.strip():
            sents.append(sent.strip())

    # 如果没有明显的句子分隔符，按字符强制切分
    if len(sents) == 0:
        return force_split_by_chars(para, max_length, overlap)

    # 按句子组合成chunks
    chunks = []
    current = ""

    for sent in sents:
        # 单个句子就超长，强制切分
        if len(sent) > max_length:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(force_split_by_chars(sent, max_length, overlap))

        # 加上当前句子会超长
        elif len(current) + len(sent) > max_length:
            if current:
                chunks.append(current.strip())
            current = sent

        # 累积句子
        else:
            current += sent

    if current:
        chunks.append(current.strip())

    return chunks


def force_split_by_chars(text: str, max_length: int, overlap: int) -> List[str]:
    """
    按字符强制切分文本

    Args:
        text: 输入文本
        max_length: 最大长度
        overlap: 重叠长度

    Returns:
        切分后的片段列表
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + max_length, text_len)
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        # 移动起始位置（考虑重叠）
        start = end - overlap if end < text_len else text_len

    return chunks


def add_overlap(chunks: List[str], overlap: int) -> List[str]:
    """
    为分片添加重叠部分

    Args:
        chunks: 原始分片列表
        overlap: 重叠长度

    Returns:
        添加重叠后的分片列表
    """
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    result = [chunks[0]]

    for i in range(1, len(chunks)):
        # 获取前一个chunk的末尾部分
        prev_chunk = chunks[i - 1]
        overlap_text = prev_chunk[-overlap:] if len(prev_chunk) >= overlap else prev_chunk

        # 将重叠部分添加到当前chunk前面
        new_chunk = overlap_text + " " + chunks[i]
        result.append(new_chunk)

    return result


def optimize_chunks(chunks: List[str], max_chunks: int, target_length: float) -> List[str]:
    """
    当分片数量过多时，进行优化合并

    Args:
        chunks: 原始分片列表
        max_chunks: 最大允许分片数
        target_length: 目标分片长度

    Returns:
        优化后的分片列表
    """
    # 策略1: 合并相邻的短片段
    merged = []
    current = ""

    for chunk in chunks:
        if len(current) + len(chunk) <= target_length:
            if current:
                current += "\n" + chunk
            else:
                current = chunk
        else:
            if current:
                merged.append(current)
            current = chunk

    if current:
        merged.append(current)

    # 如果合并后还是太多，使用抽样策略
    # if len(merged) > max_chunks:
    #     logging.warning(f"合并后分片数 {len(merged)} 仍超限，使用抽样策略")
    #
    #     # 保留开头、结尾和均匀采样的中间部分
    #     head_count = max_chunks // 4
    #     tail_count = max_chunks // 4
    #     middle_count = max_chunks - head_count - tail_count
    #
    #     head = merged[:head_count]
    #     tail = merged[-tail_count:]
    #
    #     # 从中间均匀采样
    #     middle_indices = np.linspace(
    #         head_count,
    #         len(merged) - tail_count - 1,
    #         middle_count,
    #         dtype=int
    #     )
    #     middle = [merged[i] for i in middle_indices]
    #
    #     merged = head + middle + tail

    return merged