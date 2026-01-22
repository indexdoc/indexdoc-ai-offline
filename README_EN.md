<div align="center">
  <strong>English</strong> | <a href="README.md">简体中文</a>
</div>

---
# Local Document AI Assistant
Local Document AI Assistant is a lightweight and efficient local document AI interaction tool presented as a client application. It focuses on solving the need for **accurate Q&A on local documents**, allowing you to ask AI questions based on your own file content without uploading documents to third-party platforms. It enables quick extraction of key information, interpretation of document details, and summarization of core content. Leveraging AI technology to realize intelligent interaction between humans and documents, you can ask questions about documents through natural dialogue and accurately obtain relevant information and answers.

[![Python Version](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)  [![GitHub Stars](https://img.shields.io/github/stars/indexdoc/indexdoc-ai-offline?style=social)](https://github.com/indexdoc/indexdoc-ai-offline.git) 

## ✨ Core Features

The features include local file upload, AI Q&A based on selected files, and saving of Q&A history. It supports uploading multiple common document formats such as PDF, TXT, and DOCX, with files stored locally throughout the process to ensure privacy and security. After uploading multiple files, you can freely select a single file or folder, and the AI will only respond based on the content of the selected files—avoiding irrelevant interference and improving accuracy. At the same time, you can ask personalized questions about the selected files for quick interpretation of information. The tool focuses on core functions with a clean interface, no complex configuration required, and is ready to use out of the box.

## 🚀 Quick Start

### Environment Preparation
- Recommended running environment: Python 3.10+, Tornado 6.0+, pywebview 6.1+, duckdb
- Recommended configuration: Windows 10+, 16GB RAM, solid-state drive (SSD)

```bash
https://github.com/indexdoc/indexdoc-ai-offline.git
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
![Main Page](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/mainPage.png)

**After selecting documents (folders) on the left, you can ask questions, and the AI model will provide accurate and appropriate answers based on the questions and the selected documents.**
![Main Page 2](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/mainPage2.png)

**In the search box on the left, you can search for added documents.**
![Search](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/search.png)

**Right-click a directory to perform operations such as "Open Directory", "Refresh", and "Remove from Knowledge Base"**

![Right-click Folder](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/right-clickTheFolder.png)

**Right-click a file to perform operations such as "Open File" and "Refresh"**

![Right-click File](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/right-clickTheFile.png)

**You can click the button during file loading to stop the loading process**
![Stop Upload](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/stopUpload.png)

**For the AI model's answers, you can perform operations such as copying Markdown-formatted text, exporting to Word document, exporting to PDF document, and copying plain text**
![Copy Chat](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/copyChat.png)

**Click historical records on the right to display the corresponding historical conversation content.**
![History](https://github.com/indexdoc/indexdoc-ai-offline/raw/master/history.png)

### Frequently Asked Questions
1. **Documents appear in gray font and marked as "unsupported" after addition**: If the added documents are corrupted or have incorrect encoding formats, they will appear in gray font and marked as "unsupported" after addition.

## 📞 Contact Information

- Author: Hangzhou Zhiyu Shu Information Technology Co., Ltd.
- Email: indexdoc@qq.com
- Official Website: https://www.indexdoc.com/
