"""语音识别 —— DashScope gummy-chat-v1（monkey-patch SDK transcription字段）"""
import re
import time
import logging
import tempfile
import os
import asyncio
import dashscope
from dashscope.audio.asr import Recognition
from dashscope.audio.asr.recognition import RecognitionCallback, RecognitionResult

logger = logging.getLogger("asr")

# 音近"虞晚"的常见误识别字符对，ASR 后处理用
_YU = "鱼于余俞渔愉瑜娱育雨语与玉"
_WAN = "丸完玩顽万婉湾碗皖"
_YUWAN_RE = re.compile(f"[{_YU}][{_WAN}]")

from config import DASHSCOPE_API_KEY, ASR_PHRASE_ID
dashscope.api_key = DASHSCOPE_API_KEY

# Monkey-patch: SDK 检查 "sentence" 字段，但 gummy-chat-v1 返回 "transcription"
_original_call = Recognition.call


def _patched_call(self, file, phrase_id=None, **kwargs):
    # 临时覆盖 __launch_request 来解析 transcription
    original_launch = self._Recognition__launch_request

    def patched_launch():
        responses = original_launch()
        for part in responses:
            # 把 transcription 映射为 sentence，让 SDK 正常解析
            if hasattr(part, 'output') and part.output and "transcription" in part.output:
                part.output["sentence"] = part.output.pop("transcription")
            yield part

    self._Recognition__launch_request = patched_launch
    try:
        return _original_call(self, file, phrase_id, **kwargs)
    finally:
        self._Recognition__launch_request = original_launch


Recognition.call = _patched_call


class _DummyCB(RecognitionCallback):
    def on_open(self): pass
    def on_event(self, result): pass
    def on_close(self): pass
    def on_error(self, result): pass


async def transcribe(audio_bytes: bytes) -> str:
    """音频 → 识别文本"""
    t0 = time.time()
    logger.info("ASR请求 | size=%d", len(audio_bytes))

    fd, path = tempfile.mkstemp(suffix=".wav")
    try:
        os.write(fd, audio_bytes)
        os.close(fd)

        rec = Recognition(
            model="paraformer-realtime-v2",
            format="wav",
            sample_rate=16000,
            language_hints=["zh"],
            callback=_DummyCB(),
        )
        phrase_id = ASR_PHRASE_ID or None
        logger.info("ASR phrase_id=%s", phrase_id)
        result = await asyncio.get_running_loop().run_in_executor(
            None, rec.call, path, phrase_id
        )

        if result.status_code != 200:
            logger.error("ASR失败 | status=%d | %s", result.status_code, result.message)
            raise RuntimeError(f"ASR failed: {result.message}")

        text = ""
        sentences = result.get_sentence()
        if sentences:
            if isinstance(sentences, list):
                text = "".join(s.get("text", "") for s in sentences if isinstance(s, dict))
            elif isinstance(sentences, dict):
                text = sentences.get("text", "")

        elapsed = (time.time() - t0) * 1000
        text = _YUWAN_RE.sub("虞晚", text)
        logger.info("ASR完成 | %dms | text=%s", int(elapsed), text[:80] if text else "(空)")
        return text

    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
