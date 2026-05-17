"""
AI 模拟面试助手 - 主应用入口
Flask Web 服务，提供面试练习的完整流程：题库导入 → 语音作答 → AI 评估。
"""

import os
import time
import threading
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

import config
from core import AppState, AudioRecorder
from services import process_pdf, speak, run_full_evaluation

# ─────────────────────────────────────────
# 初始化
# ─────────────────────────────────────────

app = Flask(__name__, template_folder=config.TEMPLATE_FOLDER)

# 文件上传大小限制
app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_SIZE

# 全局实例
state = AppState()
recorder = AudioRecorder()

# 确保数据目录存在
for _dir in [config.PDF_FOLDER, config.RECORD_FOLDER, config.PDF_TXT_FOLDER]:
    os.makedirs(_dir, exist_ok=True)

# 屏蔽 werkzeug 访问日志（仅保留错误）
logging.getLogger("werkzeug").setLevel(logging.ERROR)


# ─────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────

def _allowed_file(filename: str) -> bool:
    """校验上传文件扩展名是否在白名单内。"""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in config.ALLOWED_EXTENSIONS


def _handle_time_check(elapsed: int) -> int | None:
    """
    检查答题时限。返回剩余秒数，若超时则触发强制结束。
    返回 None 表示仍在正常时间范围内。
    """
    if elapsed >= config.TOTAL_TIME_LIMIT:
        speak("时间到，答题强制结束")
        _handle_end_practice()
        return config.TOTAL_TIME_LIMIT
    if elapsed >= config.TIME_WARNING_THRESHOLD and not state.warned_17min:
        state.warned_17min = True
        speak("你还有三分钟时间")
    return None


def _handle_end_practice() -> None:
    """结束答题并启动评估流水线。"""
    state.stop_practice()
    recorder.stop_recording(state.audio_filepath)
    speak("答题结束，正在为您生成评估报告，请稍候。")

    state.set_eval_running()

    run_full_evaluation(
        audio_filepath=state.audio_filepath,
        session_folder=state.session_folder,
        questions=state.questions,
        on_done=lambda result: state.set_eval_done(result, state.session_folder),
        on_error=lambda err: state.set_eval_error(err),
    )


# ─────────────────────────────────────────
# 路由
# ─────────────────────────────────────────

@app.route("/")
def index() -> str:
    """首页：渲染面试助手界面。"""
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def get_state() -> tuple:
    """返回当前应用状态快照（供前端轮询）。"""
    elapsed = state.get_elapsed()
    if state.is_practicing:
        _handle_time_check(elapsed)

    return jsonify(state.to_dict())


@app.route("/api/prepare", methods=["POST"])
def prepare() -> tuple:
    """上传 PDF 题库并进行解析（优先使用缓存）。"""
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "没有上传文件"}), 400
    if file.filename == "":
        return jsonify({"error": "文件名为空"}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": "只允许上传 PDF 文件"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(config.PDF_FOLDER, filename)
    file.save(filepath)

    state.reset()
    state.current_pdf_basename = os.path.splitext(filename)[0]
    state.eval_status = "idle"

    print(f"\n{'=' * 50}")
    print(f"[准备阶段] 接收到文件: {filename}")

    try:
        questions, cost = process_pdf(filepath)
        state.questions = questions
        print(f"【准备阶段总耗时: {cost:.2f}s】")
        print("=" * 50 + "\n")
        state.display_message = f"解析成功！已加载 {len(questions)} 道题目。"
        return jsonify({"status": "ok"})
    except Exception as e:
        state.display_message = f"准备阶段失败: {e}"
        return jsonify({"error": str(e)}), 500


@app.route("/api/start", methods=["POST"])
def start_practice() -> tuple:
    """开始答题练习。"""
    if not state.questions:
        return jsonify({"error": "暂无题目，请先上传 PDF"}), 400

    state.start_practice()

    # 创建会话文件夹
    session_id = time.strftime("%Y%m%d_%H%M%S")
    folder_name = f"{session_id}_{state.current_pdf_basename}"
    state.session_folder = os.path.join(config.RECORD_FOLDER, folder_name)
    os.makedirs(state.session_folder, exist_ok=True)
    state.audio_filepath = os.path.join(
        state.session_folder, "interview_record.wav"
    )

    recorder.start_recording()
    speak(f"面试开始。第一题：{state.questions[0]}")
    return jsonify({"status": "started"})


@app.route("/api/repeat", methods=["POST"])
def repeat_question() -> tuple:
    """重复播报当前题目。"""
    if state.is_practicing and 0 <= state.current_q_index < len(state.questions):
        speak(state.questions[state.current_q_index])
        return jsonify({"status": "repeated"})
    return jsonify({"error": "当前状态无法重复题干"}), 400


@app.route("/api/next", methods=["POST"])
def next_question() -> tuple:
    """进入下一题；若已无下一题，则结束答题。"""
    if not state.is_practicing:
        return jsonify({"error": "当前不在答题状态"}), 400

    if state.next_question():
        speak(f"下一题：{state.questions[state.current_q_index]}")
        return jsonify({"status": "next"})
    else:
        _handle_end_practice()
        return jsonify({"status": "ended"})


@app.route("/api/end", methods=["POST"])
def end_practice() -> tuple:
    """手动结束答题。"""
    if not state.is_practicing:
        return jsonify({"error": "当前不在答题状态"}), 400
    _handle_end_practice()
    return jsonify({"status": "ended"})


# ─────────────────────────────────────────
# 启动入口
# ─────────────────────────────────────────

if __name__ == "__main__":
    # 启动前配置校验
    missing_keys = config.validate_config()
    if missing_keys:
        print(
            "\n" + "=" * 50 + "\n"
            "⚠️  警告：缺少以下 API Key 配置：\n"
            + "\n".join(f"  - {k}" for k in missing_keys) +
            "\n请在 .env 文件中配置（参考 .env），"
            "否则相应功能将不可用。\n" + "=" * 50 + "\n"
        )

    print(f"服务启动中... 访问 http://{config.FLASK_HOST}:{config.FLASK_PORT}/")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )
