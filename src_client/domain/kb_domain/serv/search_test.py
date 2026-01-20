# 向量检索相关测试
import time

if __name__ == '__main__':
    # embedding = EmbeddingLoader()
    start_time = time.time()
    from domain.kb_domain.serv.VectorModel.VectorLoader import EmbeddingLoader
    print(f"{time.time()-start_time}:from domain.kb_domain.serv.VectorModel.VectorLoader import EmbeddingLoader")
    query_str = """
    民法典继承人所得遗产实际价值是什么
    """
    kb_id = '2510221222577362'
    print('-----------------------------------1--------------------------------')
    start_time = time.time()
    from domain.kb_domain.serv.ChatServ import search_docs_by_vector
    print(f"{time.time()-start_time}:from domain.kb_domain.serv.ChatServ import search_docs_by_vector")
    start_time = time.time()
    results = search_docs_by_vector(query_str, kb_id, )
    print(f"{time.time()-start_time}:search_docs_by_vector(query_str, kb_id, )")
    for res in results:
        print(res)

# 测试结果
"""
民法典继承人所得遗产实际价值是什么
max 取单片最大值
{'document_id': 2510211150409282, 'file_name': '法律小常识.bmp', 'combined_similarity': 0.727493}
{'document_id': 2510211150429293, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.686402}
{'document_id': 2510211150410700, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.686402}
{'document_id': 2510211150410231, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.686402}
{'document_id': 2510211150408544, 'file_name': '我国法律体系简介.jpg', 'combined_similarity': 0.665764}
{'document_id': 2510211150406691, 'file_name': '写起诉书需要的信息.docx', 'combined_similarity': 0.664236}
{'document_id': 2510211150407141, 'file_name': '实例合同.docx', 'combined_similarity': 0.664233}
{'document_id': 2510211150408842, 'file_name': '法律法规全集.psd', 'combined_similarity': 0.661654}
mean 同文档从筛选出的分片中取平均值
{'document_id': 2510211150409282, 'file_name': '法律小常识.bmp', 'combined_similarity': 0.727493}
{'document_id': 2510211150429293, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.67378}
{'document_id': 2510211150410700, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.67378}
{'document_id': 2510211150410231, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.67378}
{'document_id': 2510211150408544, 'file_name': '我国法律体系简介.jpg', 'combined_similarity': 0.665764}
{'document_id': 2510211150407141, 'file_name': '实例合同.docx', 'combined_similarity': 0.662313}
{'document_id': 2510211150408842, 'file_name': '法律法规全集.psd', 'combined_similarity': 0.661654}
{'document_id': 2510211150406691, 'file_name': '写起诉书需要的信息.docx', 'combined_similarity': 0.660617}
weighted_max 同文档每片加权后计算后取最大值
{'document_id': 2510211150409282, 'file_name': '法律小常识.bmp', 'combined_similarity': 0.727493}
{'document_id': 2510211150429293, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.683715}
{'document_id': 2510211150410700, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.683715}
{'document_id': 2510211150410231, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.683715}
{'document_id': 2510211150408544, 'file_name': '我国法律体系简介.jpg', 'combined_similarity': 0.665764}
{'document_id': 2510211150407141, 'file_name': '实例合同.docx', 'combined_similarity': 0.662793}
{'document_id': 2510211150408842, 'file_name': '法律法规全集.psd', 'combined_similarity': 0.661654}
{'document_id': 2510211150406691, 'file_name': '写起诉书需要的信息.docx', 'combined_similarity': 0.661522}
top_k_mean 同文档取最高的几片的平均值
{'document_id': 2510211150409282, 'file_name': '法律小常识.bmp', 'combined_similarity': 0.727493}
{'document_id': 2510211150429293, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.682278}
{'document_id': 2510211150410700, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.682278}
{'document_id': 2510211150410231, 'file_name': '昆明市名人故（旧）居保护暂行办法.docx', 'combined_similarity': 0.682278}
{'document_id': 2510211150408544, 'file_name': '我国法律体系简介.jpg', 'combined_similarity': 0.665764}
{'document_id': 2510211150407141, 'file_name': '实例合同.docx', 'combined_similarity': 0.662313}
{'document_id': 2510211150408842, 'file_name': '法律法规全集.psd', 'combined_similarity': 0.661654}
{'document_id': 2510211150406691, 'file_name': '写起诉书需要的信息.docx', 'combined_similarity': 0.660617}
"""
