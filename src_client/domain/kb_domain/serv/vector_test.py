import datetime
import json

from domain.kb_domain.dao import DocumentDao
# from domain.kb_domain.serv.DocLoadServ import read_doc

if __name__ == '__main__':
    # document_id = '8418b08b-0471-4e63-af7f-6a5654e4329e'
    # read_doc(document_id)

    # document = DocumentDao.get_by_id('8418b08b-0471-4e63-af7f-6a5654e4329e')
    # document = read_doc(document)
    # print(document)
    # DocumentDao.update(document['document_id'], document)
    import time
    import logging
    import tornado_config
    _time_begin = time.time()
    from domain.kb_domain.serv.VectorModel.VectorLoader import EmbeddingLoader
    print(f'import time {time.time() - _time_begin}')
    _time_begin = time.time()
    embed = EmbeddingLoader()
    print(f'load model time {time.time() - _time_begin}')
    _time_begin = time.time()
    res = embed.encode('qweqweqw')
    print(f'encode time {time.time() - _time_begin}')
    _time_begin = time.time()
    embed = EmbeddingLoader()
    print(f'reload model time {time.time() - _time_begin}')
    logging.info(res)
