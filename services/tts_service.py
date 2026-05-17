"""
文本转语音 (TTS) 服务
使用 Edge TTS 生成自然逼真的中文语音，通过 pygame 播放。
"""

import os
import asyncio
import tempfile
import threading
import edge_tts
import pygame
import config


def speak(text: str) -> None:
    """
    异步语音播报文本。在独立线程中运行，不阻塞主线程。
    使用微软 Edge TTS 中文女声 (Xiaoxiao)。
    """

    def _run() -> None:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        async def _generate_and_play() -> None:
            try:
                communicate = edge_tts.Communicate(text, config.TTS_VOICE)
                await communicate.save(temp_path)

                pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.quit()
            except Exception as e:
                print(f"[TTS 错误]: {e}")
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

        asyncio.run(_generate_and_play())

    threading.Thread(target=_run, daemon=True).start()
