# 🤖 AI 模拟面试助手

基于大语言模型的**公务员面试智能训练平台**，专为公安岗位面试设计。支持 PDF 题库导入、TTS 语音播题、全程录音作答、ASR 语音转写，以及 DeepSeek AI 考官的深度点评与评分。

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📄 **PDF 题库导入** | 上传 PDF 面试真题，自动调用通义千问提取题目，支持本地缓存秒开 |
| 🔊 **TTS 语音播题** | 使用微软 Edge TTS 中文女声（晓晓），自然逼真，模拟真实考场 |
| 🎙️ **全程录音** | PyAudio 持续录音作答，支持每道题独立时间戳记录 |
| 📝 **ASR 语音转写** | 阿里云 DashScope 实时语音识别，中文 + 英文混合支持 |
| 📊 **AI 深度评估** | DeepSeek-V4 模拟公安面试考官，提供评分/点评/润色/标准答案 |
| ⏱️ **计时控制** | 20 分钟总时限，17 分钟语音提醒，超时自动结束 |

## 🏗️ 项目架构

```
ai_test/
├── app.py                      # 主应用入口（Flask Web 服务）
├── config.py                   # 全局配置管理（从 .env 读取）
├── requirements.txt            # Python 依赖清单
├── .env.example                # 环境变量配置模板
├── .gitignore                  # Git 忽略规则
├── README.md
│
├── core/                       # 核心模块
│   ├── app_state.py            # 应用状态管理（线程安全）
│   └── audio_recorder.py       # 音频录制器
│
├── services/                   # 服务层
│   ├── pdf_service.py          # PDF 文本提取 + LLM 题目解析
│   ├── asr_service.py          # DashScope 语音识别
│   ├── tts_service.py          # Edge TTS 语音合成
│   └── llm_service.py          # DeepSeek 面试评估
│
├── templates/
│   └── index.html              # 前端界面（Tailwind CSS）
│
├── tools/
│   └── preprocess.py           # PDF 批量预处理（多进程加速）
│
├── pdfs/                       # [运行时] 上传的 PDF 题库
├── pdfs_txt/                   # [运行时] 解析后的题目缓存（JSON）
└── records/                    # [运行时] 答题录音与评估报告
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- 麦克风设备
- Windows 系统（音频录制依赖 PyAudio + win32）

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

> **注意**: PyAudio 在 Windows 上可能需要额外安装 `pipwin`，或从 [PyAudio 官网](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) 下载 wheel 安装。

### 3. 配置 API Key

```bash
# 复制配置模板
copy .env .env

# 编辑 .env，填入你的真实 API Key
```

```ini
# .env 文件内容
DASHSCOPE_API_KEY=sk-xxxxxxxx    # 阿里云 DashScope（通义千问 + 语音识别）
DEEPSEEK_API_KEY=sk-xxxxxxxx     # DeepSeek（面试评估）
```

> ⚠️ **安全提示**: `.env` 文件已被 `.gitignore` 忽略，不会被提交到版本控制。请勿将 API Key 写入代码中！

### 4. 准备题库

将面试真题 PDF 放入 `pdfs/` 文件夹。

**批量预处理（可选）**：提前解析所有 PDF 并缓存，后续秒开：

```bash
python tools/preprocess.py
```

> 预处理会创建 `pdfs_txt/` 目录存放解析后的题目 JSON，主程序运行时会自动读取缓存。

### 5. 启动应用

```bash
python app.py
```

浏览器将自动打开 `http://127.0.0.1:5000/`。

## 📖 使用流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  导入 PDF    │ ──▶ │  开始答题    │ ──▶ │  结束/超时   │
│ (提取题目)   │     │ (听题+录音)  │     │ (自动评估)   │
└──────────────┘     └──────────────┘     └──────────────┘
```

1. **导入题库**：点击「📄 导入 PDF 题库」，选择面试真题 PDF
2. **开始答题**：点击「▶ 开始答题」，系统播报第 1 题并开始录音
3. **作答过程中**：
   - 点击「🔁 重复题干」重新播报当前题目
   - 点击「⏭ 下一题」进入下一题
   - 点击「⏹ 结束答题」手动结束
4. **评估报告**：答题结束后自动进行语音转写 + AI 评估，结果保存在 `records/` 中

## 📁 输出文件说明

每次练习会在 `records/` 下生成以时间戳命名的文件夹：

```
records/20260101_120000_题库名称/
├── interview_record.wav    # 答题全程录音
├── 录音转文字.txt           # ASR 语音转写原文
└── 面试评估报告.txt         # AI 评估结果（评分/点评/润色/标准答案）
```

## 🔒 安全说明

| 措施 | 说明 |
|------|------|
| 🔑 **API Key 隔离** | 所有密钥从 `.env` 文件读取，不硬编码在代码中 |
| 🚫 **Debug 模式关闭** | 默认 `FLASK_DEBUG=false`，生产环境不会暴露调试控制台 |
| 🏠 **仅本机监听** | 默认 `FLASK_HOST=127.0.0.1`，不对外暴露端口 |
| 📏 **上传大小限制** | PDF 上传上限默认 20MB，防止资源耗尽 |
| 🛡️ **文件类型白名单** | 仅允许 `.pdf` 扩展名上传，防止恶意文件 |
| 📁 **路径安全** | 使用 `secure_filename()` 防止目录穿越攻击 |

## ⚙️ 配置项说明

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `DASHSCOPE_API_KEY` | (必填) | 阿里云 DashScope API Key |
| `DEEPSEEK_API_KEY` | (必填) | DeepSeek API Key |
| `FLASK_HOST` | `127.0.0.1` | Flask 监听地址 |
| `FLASK_PORT` | `5000` | Flask 监听端口 |
| `FLASK_DEBUG` | `false` | 调试模式开关 |
| `MAX_UPLOAD_SIZE_MB` | `20` | PDF 上传大小上限 |

## 🛠️ 技术栈

- **Web**: Flask + Tailwind CSS
- **LLM**: 通义千问 (Qwen-Turbo) + DeepSeek-V4
- **ASR**: 阿里云 DashScope (fun-asr-realtime)
- **TTS**: 微软 Edge TTS (zh-CN-XiaoxiaoNeural)
- **音频**: PyAudio + wave
- **PDF**: PyPDF2

## 📄 License

仅限个人学习与练习使用。

---

*Made with ❤️ for Interview Preparation*
