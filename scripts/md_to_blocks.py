"""draft.md 를 네이버 에디터 입력용 블록(JSON)으로 변환한다.

사용: python3 scripts/md_to_blocks.py drafts/<주제폴더>/draft.md
출력: {"title": ..., "category": "맛집"|"", "tags": [...], "align": "left"|"center",
       "blocks": [{"type": "heading"|"paragraph"|"image"|"quote"|"list"|"divider"|"place", ...}]}

- 문단 안의 줄바꿈은 그대로 살린다(한 줄 = 에디터 한 줄). 빈 줄은 문단 사이 빈 줄이 된다.
- 본문의 `---` 는 구분선, `[[장소: 검색어]]` 는 네이버 장소 지도가 된다.
  `[[장소: 검색어 | 주소 일부]]` 처럼 쓰면 검색 결과 중 그 문구가 들어간 곳만 고른다(상호가 흔할 때).
"""
import json
import re
import sys
from pathlib import Path

IMAGE_RE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)\s*$")
CAPTION_RE = re.compile(r"^\*(?P<text>[^*].*[^*]|[^*])\*\s*$")
PLACE_RE = re.compile(r"^\[\[장소:\s*(?P<query>[^|\]]+?)\s*(?:\|\s*(?P<match>[^\]]+?)\s*)?\]\]$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def strip_inline(text):
    # 에디터에는 마크다운이 렌더링되지 않으므로 인라인 문법을 걷어낸다
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.strip()


def parse_frontmatter(lines):
    meta = {}
    if lines and lines[0].strip() == "---":
        end = lines.index("---", 1) if "---" in lines[1:] else -1
        for line in lines[1:end]:
            if ":" in line:
                k, v = line.split(":", 1)
                v = re.sub(r"\s+#.*$", "", v).strip()
                if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                    v = v[1:-1]
                meta[k.strip()] = v
        lines = lines[end + 1:]
    return meta, lines


def main(path):
    path = Path(path).resolve()
    raw = COMMENT_RE.sub("", path.read_text(encoding="utf-8"))
    meta, lines = parse_frontmatter([l.rstrip() for l in raw.splitlines()])
    title = meta.get("title", "")
    tags = [t.strip().strip("'\"") for t in meta.get("tags", "").strip("[]").split(",") if t.strip()]
    align = "center" if meta.get("align", "").strip() in ("center", "가운데") else "left"
    category = meta.get("category", "").strip()

    blocks, para = [], []

    def flush():
        if para:
            blocks.append({"type": "paragraph", "lines": [strip_inline(l) for l in para]})
            para.clear()

    for line in lines:
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("# "):
            flush()
            title = title or s[2:].strip()  # 본문 H1 은 제목 칸으로 간다
        elif s.startswith("#"):
            flush()
            blocks.append({"type": "heading", "text": strip_inline(s.lstrip("#"))})
        elif s in ("---", "***", "___"):
            flush()
            blocks.append({"type": "divider"})
        elif m := PLACE_RE.match(s):
            flush()
            blocks.append({"type": "place", "query": m["query"], "match": m["match"] or ""})
        elif m := IMAGE_RE.match(s):
            flush()
            blocks.append({"type": "image", "path": str((path.parent / m["src"]).resolve()),
                           "alt": m["alt"], "caption": ""})
        elif (m := CAPTION_RE.match(s)) and blocks and blocks[-1]["type"] == "image" and not para:
            blocks[-1]["caption"] = m["text"].strip()
        elif s.startswith(">"):
            flush()
            blocks.append({"type": "quote", "text": strip_inline(s.lstrip("> "))})
        elif re.match(r"^([-*]|\d+\.)\s", s):
            flush()
            item = re.sub(r"^([-*]|\d+\.)\s", "", s)
            if blocks and blocks[-1]["type"] == "list":
                blocks[-1]["items"].append(strip_inline(item))
            else:
                blocks.append({"type": "list", "items": [strip_inline(item)]})
        else:
            para.append(s)
    flush()

    print(json.dumps({"title": title, "category": category, "tags": tags, "align": align, "blocks": blocks},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
