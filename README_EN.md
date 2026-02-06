<div align="center">
  <div style="font-size: 15px; line-height: 2; padding: 4px 0; letter-spacing: 0.5px;">
    <strong style="color: #24292f;">English</strong>
    | <a href="README.md" style="color: #0969da; text-decoration: none;">简体中文</a>
    <!-- | <a href="https://你的Demo在线地址" target="_blank" style="color: #165DFF; font-weight: 600; text-decoration: none;">✨ onlineDemo</a> -->
  </div>
</div>
  <div style="font-size: 14px; color: #57606a; padding: 2px 0;text-align: left;">
    <span style="background: #f6f8fa; padding: 2px 8px; border-radius: 4px; font-size: 13px;">Core Repos</span><br/>
    <a href="https://github.com/indexdoc/indexdoc-batch-generator" target="_blank" style="color: #0969da; text-decoration: none; margin: 0 6px;">indexdoc-batch-generator（Batch Document Assistant）</a><br/>
    <a href="https://github.com/indexdoc/indexdoc-model-to-code" target="_blank" style="color: #0969da; text-decoration: none; margin: 0 6px;">indexdoc-model-to-code（Code Generator / CodeAsst）</a><br/>
    <a href="https://github.com/indexdoc/indexdoc-converter" target="_blank" style="color: #0969da; text-decoration: none; margin: 0 6px;">indexdoc-converter（File Converter）</a><br/>
    <a href="https://github.com/indexdoc/indexdoc-editor" target="_blank" style="color: #0969da; text-decoration: none; margin: 0 6px;">indexdoc-editor（Markdown Editor）</a><br/>
    <a href="https://github.com/indexdoc/indexdoc-vector" target="_blank" style="color: #0969da; text-decoration: none; margin: 0 6px;">indexdoc-vector（Vector Database）</a><br/>
  </div>

---
# Local Document AI Assistant
Local Document AI Assistant is a lightweight and efficient local document AI interaction tool presented as a client application. It focuses on solving the need for **accurate Q&A on local documents**, allowing you to ask AI questions based on your own file content without uploading documents to third-party platforms. It enables quick extraction of key information, interpretation of document details, and summarization of core content. Leveraging AI technology to realize intelligent interaction between humans and documents, you can ask questions about documents through natural dialogue and accurately obtain relevant information and answers.

[![Python Version](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)  [![GitHub Stars](https://img.shields.io/github/stars/indexdoc/indexdoc-ai-offline?style=social)](https://github.com/indexdoc/indexdoc-ai-offline.git) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Core Features

The features include local file upload, AI Q&A based on selected files, and saving of Q&A history. It supports uploading multiple common document formats such as PDF, TXT, and DOCX, with files stored locally throughout the process to ensure privacy and security. After uploading multiple files, you can freely select a single file or folder, and the AI will only respond based on the content of the selected files—avoiding irrelevant interference and improving accuracy. At the same time, you can ask personalized questions about the selected files for quick interpretation of information. The tool focuses on core functions with a clean interface, no complex configuration required, and is ready to use out of the box.

## 🚀 Quick Start

### Environment Preparation
- Recommended running environment: Python 3.10+, Tornado 6.0+, pywebview 6.1+, duckdb
- Recommended configuration: Windows 10+, 16GB RAM, solid-state drive (SSD)

```bash
https://github.com/indexdoc/indexdoc-ai-offline.git
```
```bash
# Install dependencies quickly
pip install -r requirements.txt

# Use Alibaba Cloud PyPI mirror (faster installation)
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```
### Database File Directory
```bash
database/default.duck
```
### Start the Service
```bash
cd client_start.py  # Replace with the actual folder path where client_start.py is located
python.exe client_start.py

# The code enables debug mode by default
webview.start(debug=True) # Set debug=False to turn off debug mode
```

## 📝 Usage Example
**Click the "Associate Local Directory" button on the left to select local files for association. Click "Start New Conversation" on the right to initiate a new dialogue. The list below the historical conversation records the user's Q&A history.**
![Main Page](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/mainPage.png)

**After selecting documents (folders) on the left, you can ask questions, and the AI model will provide accurate and appropriate answers based on the questions and the selected documents.**
![Main Page 2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/mainPage2.png)

**In the search box on the left, you can search for added documents.**
![Search](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/search.png)

**Right-click a directory to perform operations such as "Open Directory", "Refresh", and "Remove from Knowledge Base"**

![Right-click Folder](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/right-clickTheFolder.png)

**Right-click a file to perform operations such as "Open File" and "Refresh"**

![Right-click File](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/right-clickTheFile.png)

**You can click the button during file loading to stop the loading process**
![Stop Upload](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/stopUpload.png)

**For the AI model's answers, you can perform operations such as copying Markdown-formatted text, exporting to Word document, exporting to PDF document, and copying plain text**
![Copy Chat](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/copyChat.png)

**Click historical records on the right to display the corresponding historical conversation content.**
![History](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/README/history.png)

### Frequently Asked Questions
1. **Documents appear in gray font and marked as "unsupported" after addition**: If the added documents are corrupted or have incorrect encoding formats, they will appear in gray font and marked as "unsupported" after addition.

## 📞 Contact Information

- Author: Hangzhou Zhiyu Shu Information Technology Co., Ltd.
- Email: indexdoc@qq.com
- Official Website: https://www.indexdoc.com/
