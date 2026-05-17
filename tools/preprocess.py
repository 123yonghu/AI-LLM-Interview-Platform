"""
PDF 题库批量预处理工具
递归处理 pdfs/ 目录下的所有 PDF，解析为题目 JSON 并缓存至 pdfs_txt/。
支持多进程并发，大幅提升批量处理效率。
"""

import os
import re
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import config
from services.pdf_service import extract_text_from_pdf


MAX_WORKERS: int = 10  # 最大并发进程数，可按需调整


def _process_one_pdf(filename: str) -> tuple[str, str, float]:
    """处理单个 PDF（供子进程调用）。"""
    from openai import OpenAI

    pdf_path = os.path.join(config.PDF_FOLDER, filename)
    basename = os.path.splitext(filename)[0]
    out_path = os.path.join(config.PDF_TXT_FOLDER, f"{basename}.txt")

    # 断点续传：已存在的跳过
    if os.path.exists(out_path):
        return basename, "skipped", 0.0

    t0 = time.time()

    # 提取文本
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return basename, "error: 空文本", 0.0

    # 调用 LLM 解析
    try:
        client = OpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url=config.DASHSCOPE_BASE_URL,
        )
        prompt = (
            "你是一个面试题整理助手。请从以下文本中提取所有的面试题目。\n"
            "要求：1. 过滤掉所有水印信息。2. 去除题型标识。"
            "3. 仅仅返回一个纯粹的JSON格式的字符串数组，"
            "不要包含任何markdown标记，不要解释。"
            '格式示例：["问题1...", "问题2..."]\n'
            f"待处理文本：{text}"
        )

        completion = client.chat.completions.create(
            model=config.QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        raw = completion.choices[0].message.content.strip()
        raw = re.sub(r"```json\n?|\n?```", "", raw).strip()
        parsed = json.loads(raw)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        cost = time.time() - t0
        return basename, "success", cost

    except json.JSONDecodeError:
        return basename, "error: JSON 解析失败", time.time() - t0
    except Exception as e:
        return basename, f"error: {e}", time.time() - t0


def main() -> None:
    """主入口：批量预处理所有 PDF。"""
    os.makedirs(config.PDF_FOLDER, exist_ok=True)
    os.makedirs(config.PDF_TXT_FOLDER, exist_ok=True)

    # 检查 API Key
    if not config.DASHSCOPE_API_KEY:
        print("❌ 错误：请在 .env 文件中配置 DASHSCOPE_API_KEY")
        return

    pdf_files = [f for f in os.listdir(config.PDF_FOLDER) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"在 '{config.PDF_FOLDER}' 中没有找到 PDF 文件。")
        return

    print(f"🔎 发现 {len(pdf_files)} 个 PDF，开始多进程并发处理...")
    print(f"⚙️  最大并发: {MAX_WORKERS} 进程")
    print("-" * 50)

    t_total = time.time()
    success = 0

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_process_one_pdf, f): f for f in pdf_files
        }
        for future in as_completed(futures):
            fname = futures[future]
            try:
                name, status, cost = future.result()
                if status == "success":
                    print(f"✅ [{name}] 完成 ({cost:.2f}s)")
                    success += 1
                elif status == "skipped":
                    print(f"⏩ [{name}] 已有缓存，跳过")
                    success += 1
                else:
                    print(f"❌ [{name}] 失败: {status}")
            except Exception as exc:
                print(f"💥 [{fname}] 严重异常: {exc}")

    print("-" * 50)
    print(f"🎉 全部完成！")
    print(f"总耗时: {time.time() - t_total:.2f}s")
    print(f"成功/总计: {success}/{len(pdf_files)}")
    print(f"输出目录: {os.path.abspath(config.PDF_TXT_FOLDER)}")


if __name__ == "__main__":
    main()
