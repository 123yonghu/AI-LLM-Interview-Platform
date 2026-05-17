<div align="center">

# 🤖 AI 模拟面试助手

**基于大语言模型的公务员面试智能训练平台**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-V4-purple.svg)](https://deepseek.com)
[![DashScope](https://img.shields.io/badge/DashScope-ASR-orange.svg)](https://dashscope.aliyun.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

导入 PDF 真题 → AI 语音播题 → 麦克风作答 → 智能评分点评

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [技术架构](#-技术架构) · [使用流程](#-使用流程)

</div>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📄 **PDF 题库导入** | 上传 PDF 面试真题，AI 自动提取题目，支持本地缓存秒开 |
| 🔊 **TTS 语音播题** | 微软 Edge TTS 中文女声（晓晓），自然逼真，模拟真实考场 |
| 🎙️ **全程录音** | PyAudio 持续录音作答，完整记录答题过程 |
| 📝 **ASR 语音转写** | 阿里云 DashScope 实时语音识别，中文 + 英文混合支持 |
| 📊 **AI 深度评估** | DeepSeek 模拟考官，提供 **评分 / 点评 / 润色建议 / 参考答案** |
| ⏱️ **计时控制** | 20 分钟总时限，17 分钟语音提醒，超时自动结束并评估 |

## 📸 界面预览

### 答题界面
<img width="703" height="667" alt="Snipaste_2026-05-17_13-46-41" src="https://github.com/user-attachments/assets/8ba1fcb9-52d6-4a43-b43b-d8e90e867e6d" />


## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Tailwind CSS)                    │
│              templates/index.html                        │
├─────────────────────────────────────────────────────────┤
│                  Flask Web 服务 (app.py)                  │
│              路由 / 状态管理 / API 接口                    │
├──────────┬──────────┬──────────┬────────────────────────┤
│  core/   │services/ │services/ │      services/         │
│ 状态管理  │ PDF 解析  │ ASR 转写  │  TTS 播报 / LLM 评估   │
│ 音频录制  │ 题目提取  │ 语音识别  │  DeepSeek 评分点评      │
├──────────┴──────────┴──────────┴────────────────────────┤
│         通义千问 (Qwen)  ·  DeepSeek  ·  DashScope       │
└─────────────────────────────────────────────────────────┘
```

```
ai_test/
├── app.py                      # 主应用入口（Flask Web 服务）
├── config.py                   # 全局配置管理（从 .env 读取）
├── requirements.txt            # Python 依赖清单
├── .env.example                # 环境变量配置模板
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
- Windows 系统（音频录制依赖 PyAudio）

### 2. 克隆并安装

```bash
git clone https://github.com/123yonghu/AI-LLM-Interview-Platform.git
cd AI-LLM-Interview-Platform

# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 复制配置模板
cp .env.example .env            # Linux/Mac
copy .env.example .env          # Windows

# 编辑 .env，填入你的 API Key
```

需要配置两个 API Key：

| API | 用途 | 获取地址 |
|-----|------|---------|
| `DASHSCOPE_API_KEY` | 通义千问（题目解析）+ 语音识别 | [DashScope 控制台](https://dashscope.console.aliyun.com/) |
| `DEEPSEEK_API_KEY` | AI 面试评估（评分/点评） | [DeepSeek 平台](https://platform.deepseek.com/) |

> ⚠️ `.env` 文件已被 `.gitignore` 忽略，不会被提交到版本控制。

### 4. 启动

```bash
python app.py
```

浏览器访问 `http://127.0.0.1:5000/` 即可使用。

## 📖 使用流程

```
📄 导入 PDF 真题  →  ▶ 开始答题  →  🎙 语音作答  →  ⏹ 结束答题  →  📊 AI 评估
     (AI 提取题目)     (TTS 播题)     (全程录音)     (自动/手动)     (评分+点评)
```

1. **导入题库** — 点击「📄 导入 PDF 题库」，上传面试真题 PDF
2. **开始答题** — 点击「▶ 开始答题」，系统语音播报第 1 题并开始录音
3. **作答过程** — 点击「🔁 重复题干」重听 / 「⏭ 下一题」跳题 / 「⏹ 结束答题」交卷
4. **查看报告** — 系统自动进行语音转写 + AI 评估，生成完整点评报告

## 📁 输出文件

每次练习在 `records/` 下生成独立文件夹：

```
records/20260101_120000_题库名称/
├── interview_record.wav    # 答题全程录音
├── 录音转文字.txt           # ASR 语音转写原文
└── 面试评估报告.txt         # AI 评估（评分/点评/润色/参考答案）
```

## 🔒 安全设计

| 措施 | 说明 |
|------|------|
| 🔑 API Key 隔离 | 所有密钥从 `.env` 读取，代码中零硬编码 |
| 🏠 仅本机监听 | 默认 `127.0.0.1`，不对外暴露端口 |
| 📏 上传限制 | PDF 上传上限 20MB，仅允许 `.pdf` 扩展名 |
| 📁 路径安全 | `secure_filename()` 防止目录穿越 |
| 🚫 Debug 关闭 | 生产环境默认关闭 Flask 调试模式 |

## ⚙️ 配置项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `DASHSCOPE_API_KEY` | *(必填)* | 阿里云 DashScope API Key |
| `DEEPSEEK_API_KEY` | *(必填)* | DeepSeek API Key |
| `FLASK_HOST` | `127.0.0.1` | 监听地址 |
| `FLASK_PORT` | `5000` | 监听端口 |
| `FLASK_DEBUG` | `false` | 调试模式 |
| `MAX_UPLOAD_SIZE_MB` | `20` | 上传大小上限 (MB) |

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | Flask + Tailwind CSS |
| 大语言模型 | 通义千问 (Qwen-Turbo) · DeepSeek-V4 |
| 语音识别 | 阿里云 DashScope (fun-asr-realtime) |
| 语音合成 | 微软 Edge TTS (zh-CN-XiaoxiaoNeural) |
| 音频处理 | PyAudio + wave |
| PDF 解析 | PyPDF2 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**用 AI 赋能面试备考，让每一次练习都有收获** ⭐

如果这个项目对你有帮助，欢迎 Star 支持一下！

</div>
