"""
音频录制模块
基于 PyAudio 实现麦克风录音，线程安全。
"""

import wave
import threading
import pyaudio
import config


class AudioRecorder:
    """音频录制器，在后台线程中持续录制麦克风输入。"""

    def __init__(self) -> None:
        self.chunk: int = config.AUDIO_CHUNK
        self.format: int = pyaudio.paInt16
        self.channels: int = config.AUDIO_CHANNELS
        self.rate: int = config.AUDIO_RATE
        self._p: pyaudio.PyAudio = pyaudio.PyAudio()
        self._frames: list = []
        self._is_recording: bool = False
        self._stream = None

    def start_recording(self) -> None:
        """启动录音。"""
        self._frames = []
        self._is_recording = True
        self._stream = self._p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        def _record_loop() -> None:
            while self._is_recording:
                try:
                    data = self._stream.read(self.chunk)
                    self._frames.append(data)
                except Exception:
                    break

        threading.Thread(target=_record_loop, daemon=True).start()

    def stop_recording(self, filepath: str) -> str:
        """停止录音并将音频保存到 filepath（WAV 格式）。"""
        self._is_recording = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        wf = wave.open(filepath, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self._p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(self._frames))
        wf.close()
        return filepath
