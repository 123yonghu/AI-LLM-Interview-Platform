"""
PDF 解析服务
负责从 PDF 文件中提取文本，并通过 LLM 解析为面试题目列表。
"""

import os
import re
import json
import time
import PyPDF2
from openai import OpenAI
import config


def extract_text_from_pdf(pdf_path: str) -> str:
    """从 PDF 文件中提取纯文本。"""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text


def parse_questions_from_text(text: str) -> list[str]:
    """
    使用通义千问从文本中提取面试题目。
    返回题目字符串列表。
    """
    client = OpenAI(
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_BASE_URL,
    )

    prompt = (
        "你是一个面试题整理助手。请从以下文本中提取所有的面试题目。\n"
        "要求：1. 过滤掉所有水印信息。2. 去除题型标识。"
        "3. 仅仅返回一个纯粹的JSON格式的字符串数组，不要包含任何markdown标记，不要解释。"
        '格式示例：["问题1...", "问题2..."]\n'
        f"待处理文本：{text}"
    )

    completion = client.chat.completions.create(
        model=config.QWEN_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    raw = completion.choices[0].message.content.strip()
    cleaned = re.sub(r"```json\n?|\n?```", "", raw).strip()
    return json.loads(cleaned)


def process_pdf(pdf_path: str, cache_dir: str | None = None) -> tuple[list[str], float]:
    """
    完整的 PDF 处理流程：
    1. 尝试从缓存目录加载
    2. 若无缓存，提取文本 + 调用 LLM 解析 + 写入缓存
    返回 (题目列表, 耗时秒数)。
    """
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    cache_dir = cache_dir or config.PDF_TXT_FOLDER
    cache_path = os.path.join(cache_dir, f"{basename}.txt")

    # 分支 A：缓存命中
    if os.path.exists(cache_path):
        t0 = time.time()
        with open(cache_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        cost = time.time() - t0
        print(f" -> [缓存] 从本地缓存加载 {len(questions)} 题 ({cost:.2f}s)")
        return questions, cost

    # 分支 B：解析 PDF + LLM
    t0 = time.time()
    text = extract_text_from_pdf(pdf_path)
    t_pdf = time.time()
    print(f" -> [PDF] 文本提取完成 ({t_pdf - t0:.2f}s)")

    if not text.strip():
        raise ValueError("未能从 PDF 中提取到有效文本。")

    questions = parse_questions_from_text(text)
    t_llm = time.time()
    print(f" -> [LLM] 题目解析完成 ({t_llm - t_pdf:.2f}s)")

    # 写入缓存
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
    print(f" -> [缓存] 已保存至 {cache_path}")

    cost = time.time() - t0
    return questions, cost
