"""
语音识别 (ASR) 服务
通过阿里云 DashScope 将音频文件转写为文本。
"""

import time
from http import HTTPStatus
import dashscope
from dashscope.audio.asr import Recognition
import config


def transcribe_audio(audio_filepath: str) -> tuple[str, float]:
    """
    将音频文件转写为文本。
    返回 (转写文本, 耗时秒数)。
    """
    t0 = time.time()

    recognition = Recognition(
        model=config.ASR_MODEL,
        format="wav",
        sample_rate=config.AUDIO_RATE,
        language_hints=config.ASR_LANGUAGE_HINTS,
        callback=None,
    )

    result = recognition.call(audio_filepath)

    transcript_text = ""
    if result.status_code == HTTPStatus.OK:
        sentences = result.get_sentence()
        if isinstance(sentences, list):
            for sentence in sentences:
                if isinstance(sentence, dict) and "text" in sentence:
                    transcript_text += sentence["text"]
                elif isinstance(sentence, str):
                    transcript_text += sentence
        elif isinstance(sentences, str):
            transcript_text = sentences
        else:
            transcript_text = str(sentences)
    else:
        raise RuntimeError(f"语音转写失败: {result.message}")

    if not transcript_text.strip():
        transcript_text = "[未检测到有效语音输入]"

    cost = time.time() - t0
    print(f" -> [ASR] 语音识别完成 ({cost:.2f}s)")
    return transcript_text, cost
