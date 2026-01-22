<div align="center">
  <strong>简体中文</strong> |  <a href="README_EN.md">English</a>
</div>

---
# 本地文档AI助手
本地文档AI助手，是一款轻量、高效的本地文档AI交互工具，以客户端的形式呈现，专注于解决「本地文档精准问答」需求，让你无需上传文档至第三方平台，即可基于自有文件内容向AI提问，快速提取关键信息、解读文档细节、总结核心内容。利用AI技术实现人与文档智能交互，通过自然对话方式向文档提问，精准获取相关信息与答案。

[![Python Version](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)  [![GitHub Stars](https://img.shields.io/github/stars/indexdoc/indexdoc-ai-offline?style=social)](https://github.com/indexdoc/indexdoc-ai-offline.git) 

## ✨ 核心功能

功能涵盖本地文件上传、基于选中文件的AI问答、问答历史的保存等。支持PDF、TXT、DOCX等多种常见文档格式上传，文件全程本地存储以保障隐私安全；上传多份文件后可自由选中单个文件或文件夹，AI将仅基于选中文件内容应答，避免无关干扰、提升精准度，同时可针对选中文件提出个性化问题，快速响应解读信息，整体聚焦核心功能、界面简洁、无需复杂配置、上手即用。

##  🚀快速开始

### 环境准备
- 推荐运行环境： Python 3.10+、Tornado 6.0+、pywebview 6.1+、duckdb
- 推荐配置：windows10+、 16GB 内存，固态硬盘

```bash
https://github.com/indexdoc/indexdoc-ai-offline.git
```

### 数据库文件目录
```bash
database/default.duck
```
### 启动服务
```bash
cd client_start.py  # 替换为client_start.py实际所在的文件夹路径
python.exe client_start.py

#代码默认开启调试模式
webview.start(debug=True) #debug=False 即可关闭调试模式
```

## 📝 使用示例
**点击左侧"关联本地目录"按钮可以选择本地的文件进行关联。点击右侧"开启新对话"可开启新对话。历史对话下方列表记录了用户的问答记录。**
![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/mainPage.png)

**在左侧选中文档(文件夹)之后，即可提问，ai模型会根据所提出的问题和所选中的文档进行准确合适的回答。**
![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/mainPage2.png)

**在左侧的搜索框中，可对已添加的文档进行搜索。**
![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/search.png)

**对目录右键后即可进行 打开目录、刷新、 移出知识库操作**

![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/right-clickTheFolder.png)

**对文件右键后即可进行 打开文件、刷新、操作**

![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/right-clickTheFile.png)

**文件加载时可点击正在加载后按钮停止加载**
![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/stopUpload.png)

**对ai模型的回答 可以进行 复制markdown格式文本、导出Word文档、导出pdf文档、复制纯文本的操作**
![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/copyChat.png)

**点击右侧历史记录 即可回显相应历史记录的对话内容。**
![主页2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/history.png)

### 常见问题
1. **文档添加后呈灰色字体并显示不支持**：所添加的文档如出现损坏、编码格式不正确等情况，添加后呈灰色字体并显示不支持。


## 📞 联系方式

- 作者：杭州智予数信息技术有限公司

- 邮箱：indexdoc@qq.com

- 官方网站：https://www.indexdoc.com/
