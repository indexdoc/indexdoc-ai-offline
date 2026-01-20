import os

from domain.kb_domain.serv.DocLoad.LoaderFactory import LoaderFactory
from domain.kb_domain.serv.DocLoadServ import doc_spliter
from domain.kb_domain.serv.VectorModel.VectorLoader import EmbeddingLoader

if __name__ == '__main__':
    # path = 'D:\资产资源盘活相关政策汇编'
    path = 'E:\测试目录\错误\新建文件夹'
    for root, dirs, files in os.walk(path):
        for file in files:
            loader = LoaderFactory.from_file(os.path.join(root, file))
            # 读取成功 合成内容
            content = '\n'.join(loader.rtn['file_content'])
            # 开始分片
            file_content_chunks = doc_spliter(content)
            # 分片向量化
            embedding = EmbeddingLoader()
            file_content_chunks_vector = embedding.encode(file_content_chunks)
            # 文件名向量化
            # 写入内容

