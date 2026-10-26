"""Grokkingの回答を複数条件で取得し、個人用JSONLに記録する。

例:
    uv run --python 3.12 python scripts/run_grokking_experiment.py \
        --models MODEL_ID_1 MODEL_ID_2 \
        --temperatures 0.2 0.8 --repeats 3

APIキーは app.config がプロジェクト直下の .env から読み込む。
結果は Git 管理外の learning_log/lecture-01/ に保存する。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import DEFAULT_MODEL, get_api_key

DEFAULT_QUESTION = "Grokkingとは何ですか？"
DEFAULT_TEMPERATURES = [0.2, 0.8]
OUTPUT_DIR = ROOT_DIR / "learning_log" / "lecture-01"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="モデル・temperatureごとに質問を繰り返し、回答とトークン数をJSONLに記録する"
    )
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--models",
        nargs="+",
        help="比較するモデルID。省略時は AIE_MODEL（未設定なら既定モデル）を使う",
    )
    parser.add_argument(
        "--temperatures",
        nargs="+",
        type=float,
        default=DEFAULT_TEMPERATURES,
        help="temperatureの値（0より大きく2以下）",
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument(
        "--output",
        type=Path,
        help="保存先JSONL。省略時は learning_log/lecture-01/ に日時付きで作成",
    )
    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats は1以上を指定してください")
    if not args.temperatures or any(not 0.0 < t <= 2.0 for t in args.temperatures):
        parser.error("--temperatures は0より大きく2以下の値を指定してください")
    if not args.question.strip():
        parser.error("--question を空にはできません")
    return args


def main() -> None:
    args = parse_args()
    models = args.models or [os.getenv("AIE_MODEL", DEFAULT_MODEL)]
    output = args.output or OUTPUT_DIR / (
        f"grokking-{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}.jsonl"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=get_api_key())
    total = len(models) * len(args.temperatures) * args.repeats
    print(f"{total} 回のAPI呼び出しを行い、結果を {output} に記録します。")

    completed = 0
    with output.open("x", encoding="utf-8") as result_file:
        for model in models:
            os.environ["AIE_MODEL"] = model
            selected_model = os.getenv("AIE_MODEL", DEFAULT_MODEL)
            for temperature in args.temperatures:
                for repeat in range(1, args.repeats + 1):
                    completed += 1
                    record = {
                        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                        "question": args.question,
                        "model": selected_model,
                        "temperature": temperature,
                        "repeat": repeat,
                    }
                    try:
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=args.question,
                            config=types.GenerateContentConfig(temperature=temperature),
                        )
                        usage = response.usage_metadata
                        record.update(
                            {
                                "answer": response.text or "",
                                "input_tokens": usage.prompt_token_count if usage else None,
                                "output_tokens": usage.candidates_token_count if usage else None,
                            }
                        )
                        status = "記録済み"
                    except Exception as exc:
                        # エラー本文はキーなどを含む可能性があるため保存せず、種類だけ記録する。
                        record["error_type"] = type(exc).__name__
                        status = f"失敗（{type(exc).__name__}）"

                    result_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    result_file.flush()
                    print(
                        f"[{completed}/{total}] model={selected_model}, temperature={temperature}, "
                        f"repeat={repeat}: {status}"
                    )

    print(f"完了: {output}")


if __name__ == "__main__":
    main()
