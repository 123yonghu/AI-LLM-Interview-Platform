"""
应用配置管理模块
所有配置从环境变量读取，避免硬编码敏感信息。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ========== 项目根目录 ==========
BASE_DIR = Path(__file__).resolve().parent

# ========== API Key（必须从环境变量读取）==========
DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

# ========== 目录配置 ==========
PDF_FOLDER = str(BASE_DIR / "pdfs")
RECORD_FOLDER = str(BASE_DIR / "records")
PDF_TXT_FOLDER = str(BASE_DIR / "pdfs_txt")
TEMPLATE_FOLDER = str(BASE_DIR / "templates")

# ========== Flask 配置 ==========
FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# ========== 安全配置 ==========
# PDF 文件上传大小上限（字节），默认 20MB
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
MAX_UPLOAD_SIZE: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS: set = {"pdf"}

# ========== 面试配置 ==========
# 总答题时间上限（秒），20 分钟
TOTAL_TIME_LIMIT: int = 1200
# 剩余时间提醒阈值（秒），3 分钟
TIME_WARNING_THRESHOLD: int = 1020

# ========== 音频录制配置 ==========
AUDIO_CHUNK: int = 1024
AUDIO_FORMAT: int = 8  # paInt16，需在 recorder 中导入 pyaudio 后确定
AUDIO_CHANNELS: int = 1
AUDIO_RATE: int = 16000

# ========== ASR 配置 ==========
ASR_MODEL: str = "fun-asr-realtime-2026-02-28"
ASR_LANGUAGE_HINTS: list = ["zh", "en"]

# ========== LLM 配置 ==========
QWEN_MODEL: str = "qwen-turbo"
DEEPSEEK_MODEL: str = "deepseek-v4-pro"
DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

# ========== TTS 配置 ==========
TTS_VOICE: str = "zh-CN-XiaoxiaoNeural"


def validate_config() -> list[str]:
    """启动时校验必要的配置项，返回缺失项的列表。"""
    missing = []
    if not DASHSCOPE_API_KEY:
        missing.append("DASHSCOPE_API_KEY")
    if not DEEPSEEK_API_KEY:
        missing.append("DEEPSEEK_API_KEY")
    return missing
