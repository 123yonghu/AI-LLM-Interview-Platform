"""
大语言模型评估服务
通过 DeepSeek API 对面试回答进行评分、点评和润色。
"""

import os
import time
from openai import OpenAI
import config


def build_evaluation_prompt(
    questions: list[str], transcript: str
) -> str:
    """构建发给 DeepSeek 的面试评估 prompt。"""
    questions_text = "\n".join(
        [f"第{i + 1}题: {q}" for i, q in enumerate(questions)]
    )

    return (
        "你现在是一位公安面试考官，针对下列问题及面试者的回复进行评估：\n\n"
        "【面试考题】\n"
        f"{questions_text}\n\n"
        "【考生的语音转写回复】\n"
        f"{transcript}\n\n"
        f"根据以下格式，进行相应的回答（注意，一共有{len(questions)}道题，"
        "你要分别根据下面的格式回答）：\n"
        "1. 评分\n"
        "2. 点评\n"
        "3. 原文经优化润色的结果，应在原文基础上改进，通过表格对照每行的修改。\n"
        "4. 主考官给出的专业回答，此时不必拘泥于我的回答原文\n"
        "【注意，因为我使用了语音转文字技术，因此忽略标点符号，错别字的错误】"
    )


def evaluate_interview(
    questions: list[str], transcript: str
) -> tuple[str, float]:
    """
    调用 DeepSeek 对面试回答进行评估。
    返回 (评估结果文本, 耗时秒数)。
    """
    t0 = time.time()

    client = OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
    )

    prompt = build_evaluation_prompt(questions, transcript)

    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional interviewer."},
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )

    result = response.choices[0].message.content
    cost = time.time() - t0
    print(f" -> [DeepSeek] 评估完成 ({cost:.2f}s)")
    return result, cost


def run_full_evaluation(
    audio_filepath: str,
    session_folder: str,
    questions: list[str],
    on_done,
    on_error,
) -> None:
    """
    完整的评估流水线：ASR → DeepSeek 评估 → 保存报告。
    在独立线程中执行，通过回调通知结果。
    """
    try:
        # 1. ASR
        from .asr_service import transcribe_audio

        transcript, asr_cost = transcribe_audio(audio_filepath)

        # 保存转写原文
        transcript_path = os.path.join(session_folder, "录音转文字.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        # 2. LLM 评估
        eval_result, ds_cost = evaluate_interview(questions, transcript)

        # 3. 保存评估报告
        eval_path = os.path.join(session_folder, "面试评估报告.txt")
        questions_text = "\n".join(
            [f"第{i + 1}题: {q}" for i, q in enumerate(questions)]
        )
        with open(eval_path, "w", encoding="utf-8") as f:
            f.write(f"============ 面试题干 ============\n{questions_text}\n\n")
            f.write(f"============ 语音转写原文 ============\n{transcript}\n\n")
            f.write(f"============ AI 评价报告 ============\n{eval_result}\n")

        total_cost = asr_cost + ds_cost
        print(f"【评估总耗时: {total_cost:.2f}s】")

        on_done(eval_result)

    except Exception as e:
        print(f"[评估错误] {e}")
        on_error(str(e))
