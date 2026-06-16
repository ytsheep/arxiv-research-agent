"""Generate deterministic local PDF evaluation cases."""

from __future__ import annotations

import json
import re
from pathlib import Path

import fitz


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = BACKEND_ROOT / "data" / "paper_library" / "papers"
OUTPUT_PATH = Path(__file__).resolve().parent / "cases" / "pdf_cases.jsonl"


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\ufffd", "")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    return " ".join(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def sample_snippets(pdf_path: Path, count: int = 10, token_count: int = 24) -> list[str]:
    doc = fitz.open(pdf_path)
    pages = [normalize_text(page.get_text("text", sort=True)) for page in doc]
    doc.close()

    eligible = [text.split() for text in pages if len(text.split()) >= token_count * 2]
    if not eligible:
        return []

    snippets = []
    for index in range(count):
        tokens = eligible[round(index * (len(eligible) - 1) / max(count - 1, 1))]
        position = 0.1 + (0.8 * index / max(count - 1, 1))
        offset = max(0, min(len(tokens) - token_count, int(len(tokens) * position)))
        snippet = " ".join(tokens[offset:offset + token_count])
        if snippet:
            snippets.append(snippet)
    return snippets


def build_cases() -> list[dict]:
    cases = []
    for paper_dir in sorted(PAPER_ROOT.iterdir()):
        pdf_path = paper_dir / "paper.pdf"
        parsed_path = paper_dir / "parsed.md"
        if not pdf_path.exists() or not parsed_path.exists():
            continue
        snippets = sample_snippets(pdf_path, count=10)
        if not snippets:
            continue
        for sample_index, snippet in enumerate(snippets, start=1):
            cases.append({
                "case_id": f"pdf_{len(cases) + 1:03d}",
                "paper_id": paper_dir.name,
                "sample_index": sample_index,
                "pdf_path": str(pdf_path.relative_to(BACKEND_ROOT)).replace("\\", "/"),
                "parsed_path": str(parsed_path.relative_to(BACKEND_ROOT)).replace("\\", "/"),
                "gold_snippets": [snippet],
                "min_snippet_matches": 1,
                "min_parsed_chars": 1000,
            })
    return cases


def main() -> None:
    cases = build_cases()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for case in cases:
            file.write(json.dumps(case, ensure_ascii=False) + "\n")
    print(f"Generated {len(cases)} PDF cases at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
