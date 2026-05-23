import os
import sys

# Windows GBK → UTF-8 编码修复（必须在任何 I/O 之前执行）
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Agent 标识
# ============================================================
AGENT_NAME = "bijou"

# ============================================================
# DeepSeek API 配置（主模型）
# ============================================================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# ============================================================
# 阿里云 DashScope LLM 配置（备用模型）
# ============================================================
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-plus"

# ============================================================
# 长期记忆配置 (OpenClaw 架构)
# ============================================================
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory", "data")
MEMORY_WORKSPACE = os.path.join(MEMORY_DIR, "workspace")
MEMORY_INDEX_DB = os.path.join(MEMORY_DIR, "memory_index.db")
MEMORY_DISTILL_THRESHOLD = 10000
MEMORY_RETRIEVAL_TOP_K = 5
MEMORY_CHECKPOINT_DIR = os.path.join(MEMORY_DIR, "checkpoints")

# ============================================================
# Embedding 配置（记忆系统语义检索使用）
# ============================================================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_EMBEDDING_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_EMBEDDING_MODEL = "text-embedding-v4"
DASHSCOPE_EMBEDDING_BATCH_SIZE = 50

# ============================================================
# CosyVoice v3.5-plus TTS 配置（DashScope API）
# ============================================================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
COSYVOICE_VOICE_ID = os.getenv("COSYVOICE_VOICE_ID", "")

# ============================================================
# ASR 语音识别配置（DashScope Gummy-chat-v1 WebSocket API）
# ============================================================
# API key 复用上方的 DASHSCOPE_API_KEY，无需额外配置

# ============================================================
# ASR 热词表（提升"虞晚"等专有名词识别率）
# ============================================================
ASR_PHRASE_ID = os.getenv("ASR_PHRASE_ID", "")
