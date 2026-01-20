import logging

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

import frozen_support


class EmbeddingLoader:
    """
    EmbeddingLoader - 单例模式的Embedding模型加载器
    确保多次调用只加载一次模型
    """

    _instance = None
    _initialized = False

    def __new__(cls, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2"):
        """
        实现单例模式
        """
        if cls._instance is None:
            cls._instance = super(EmbeddingLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name_or_path=None):
        """
        初始化Embedding加载器

        Args:
            model_name_or_path: 预训练模型的名称或路径
        """
        # 防止重复初始化
        if self._initialized:
            return
        if not model_name_or_path:
            model_name_or_path = frozen_support.get_resource_path('domain/kb_domain/serv/VectorModel/BAAI/bge-small-zh-v1.5')
        self.model_name_or_path = model_name_or_path
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._initialized = True
        self.load_model()

    def load_model(self):
        """
        加载预训练的Embedding模型（只在首次调用时加载）
        """
        if self.tokenizer is not None and self.model is not None:
            logging.debug(f"模型 {self.model_name_or_path} 已经加载，无需重复加载")
            return

        logging.debug(f"正在加载模型: {self.model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        self.model = AutoModel.from_pretrained(self.model_name_or_path)
        self.model.to(self.device)
        self.model.eval()  # 设置为评估模式
        logging.debug(f"模型加载完成，设备: {self.device}")

    def encode(self, texts):
        """
        将文本编码为向量

        Args:
            texts: 输入文本，可以是单个字符串或字符串列表

        Returns:
            编码后的向量，numpy数组格式
        """
        if not self.model or not self.tokenizer:
            raise ValueError("模型尚未加载，请先调用load_model()方法")

        # 确保输入是列表格式
        if isinstance(texts, str):
            texts = [texts]

        # 对文本进行tokenization
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors='pt',
            max_length=512
        ).to(self.device)

        # 获取模型输出
        with torch.no_grad():
            model_output = self.model(**encoded_input)

            # 使用池化操作获取句子向量
            # 这里使用均值池化，也可以使用其他池化方式
            sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])

        # 转换为numpy数组并移动到CPU
        embeddings = sentence_embeddings.cpu().numpy()

        return embeddings

    def _mean_pooling(self, model_output, attention_mask):
        """
        使用attention mask进行均值池化
        """
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

        # 计算加权平均
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        mean_pooled = sum_embeddings / sum_mask
        return mean_pooled


