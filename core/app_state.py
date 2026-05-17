"""
全局应用状态管理
线程安全地管理面试流程中的所有状态变量。
"""

import time
import threading
from typing import List


class AppState:
    """面试应用全局状态容器（线程安全）。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.questions: List[str] = []
        self.current_q_index: int = -1
        self.is_practicing: bool = False
        self.start_time: float = 0.0
        self.warned_17min: bool = False
        self.eval_result: str = ""
        self.eval_status: str = "idle"  # idle / running / done / error
        self.display_message: str = "等待导入PDF..."
        self.current_pdf_basename: str = ""
        self.session_folder: str = ""
        self.audio_filepath: str = ""

    def reset(self) -> None:
        """重置为初始状态（保留 eval 相关字段）。"""
        with self._lock:
            self.questions = []
            self.current_q_index = -1
            self.is_practicing = False
            self.start_time = 0.0
            self.warned_17min = False

    def set_eval_running(self) -> None:
        """标记评估为运行中。"""
        with self._lock:
            self.eval_status = "running"
            self.display_message = "正在进行语音转写和深度评估，请稍候..."

    def set_eval_done(self, result: str, folder: str) -> None:
        """标记评估完成。"""
        with self._lock:
            self.eval_status = "done"
            self.eval_result = result
            self.display_message = (
                f"AI评估完成！报告已存入文件夹：\n{self.session_folder}"
            )

    def set_eval_error(self, error_msg: str) -> None:
        """标记评估出错。"""
        with self._lock:
            self.eval_status = "error"
            self.display_message = f"评估发生错误：\n{error_msg}"

    def get_elapsed(self) -> int:
        """获取当前练习已用时间（秒）。"""
        if self.is_practicing:
            return int(time.time() - self.start_time)
        return 0

    def start_practice(self) -> None:
        """开始练习。"""
        with self._lock:
            self.is_practicing = True
            self.start_time = time.time()
            self.current_q_index = 0
            self.warned_17min = False
            self.eval_status = "idle"
            self.eval_result = ""

    def stop_practice(self) -> None:
        """停止练习。"""
        with self._lock:
            self.is_practicing = False

    def next_question(self) -> bool:
        """移动到下一题；返回 True 表示仍有题，False 表示已无题。"""
        with self._lock:
            self.current_q_index += 1
            return self.current_q_index < len(self.questions)

    def to_dict(self) -> dict:
        """生成前端状态快照（线程安全）。"""
        with self._lock:
            return {
                "is_practicing": self.is_practicing,
                "elapsed_time": int(time.time() - self.start_time)
                if self.is_practicing
                else 0,
                "current_q_index": self.current_q_index,
                "total_q": len(self.questions),
                "questions": self.questions,
                "eval_status": self.eval_status,
                "eval_result": self.eval_result,
                "display_message": self.display_message,
            }
