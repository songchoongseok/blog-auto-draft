"""블록 JSON 을 네이버 에디터 입력용 Playwright 코드 조각으로 나눈다.

사용: python3 scripts/naver_segments.py <blocks.json> <출력 폴더>
      (출력 폴더는 Claude Code 작업 폴더 아래여야 browser_run_code_unsafe 의 filename 으로 읽힌다)

출력:
  00-title.js         팝업 정리 + 제목 입력 + 본문 시작(+ 정렬)
  NN-text.js          사진 사이의 글 구간(문단·소제목·목록·인용구·구분선·장소)
  NN-goto.js          본문 끝으로 이동 후 "사진 추가" 클릭 → 이어서 browser_file_upload
  NN-cap.js           업로드 완료 대기 + 캡션 입력
  99-publish-settings.js  발행 설정 창을 열어 카테고리·태그만 넣고 Esc로 닫는다(발행 버튼은 누르지 않는다)
  plan.json           실행 순서 [{step, kind, file | path}]
"""
import json
import re
import sys
from pathlib import Path

J = lambda s: json.dumps(s, ensure_ascii=False)

HEAD = "const f = page.frame('mainFrame');\n"

GOTO_END = HEAD + """{ const last = f.locator('.se-component').last();
  if (await last.evaluate(e => e.classList.contains('se-text'))) { await last.locator('.se-text-paragraph').last().click({force: true}); await page.keyboard.press('End'); }
  else { const b = await last.boundingBox(); await page.mouse.click(b.x + b.width / 2, b.y + b.height + 25); await page.waitForTimeout(300); } }
"""

RET = "return await f.evaluate(() => [...document.querySelectorAll('.se-component')].slice(-4).map(c => c.className.split(' ')[1] + ' | ' + c.innerText.slice(0, 40).replace(/\\n/g, '/')));"

ALIGN_CENTER = "await f.locator('button:has-text(\"정렬 열기\")').first().click(); await page.waitForTimeout(300); await f.locator('button.se-toolbar-option-icon-button:visible', {hasText: '가운데 정렬'}).first().click(); await page.waitForTimeout(200);"

HEADING = "await f.locator('button:has-text(\"문단 서식 변경\")').first().click(); await page.waitForTimeout(300); await f.locator('button.__se-sentry:visible', {hasText: '소제목'}).first().click(); await page.waitForTimeout(300);"

LIST_ON = "await f.locator('button:has-text(\"목록 열기\")').first().click(); await page.waitForTimeout(300); await f.locator('button.se-toolbar-option-icon-button:visible', {hasText: '기호목록'}).first().click(); await page.waitForTimeout(300);"


# keyboard.type 은 ✔️ 처럼 변형 선택자(FE0F)가 붙은 이모지를 "✔✔️"로 두 번 찍는다.
# 이모지 묶음만 insertText 로 넣으면 정상이다(문장 전체를 insertText 로 넣으면 일부가 사라진다).
EMOJI_RE = re.compile(
    "((?:[←-⯿〰〽㊗㊙\U0001F000-\U0001FAFF]"
    "[️⃣\U0001F3FB-\U0001F3FF]*‍?)+)"
)


def typed(text):
    out = []
    for i, part in enumerate(EMOJI_RE.split(text)):
        if part:
            out.append(f"await page.keyboard.{'insertText' if i % 2 else 'type'}({J(part)});")
    return " ".join(out)


def type_line(text):
    return f"{typed(text)} await page.keyboard.press('Enter');"


def place(query, match=""):
    # "육당헌 스타필드 수원"처럼 상호+위치 검색어는 결과가 없을 때가 있어서 뒤 단어를 하나씩 빼며 다시 찾는다.
    # match 가 있으면 결과 중 그 문구(주소 일부 등)가 들어간 항목만 고른다. "우동집"처럼 상호가 흔할 때 쓴다.
    # 끝까지 없으면 팝업만 닫는다. 결과 없이 끝난 실행에서 글쓰기 페이지가 새로 고침된 적이 있어,
    # 닫기는 장소 팝업 안의 버튼으로 한정한다.
    words = query.split()
    queries = [" ".join(words[:n]) for n in range(len(words), 0, -1)]
    return f"""await f.locator('button:has-text("장소 추가")').first().click(); await page.waitForTimeout(1200);
{{ let added = false; const want = {J(match)};
  for (const q of {J(queries)}) {{
    await f.locator('input[placeholder="장소명을 입력하세요."]').fill(q);
    await f.locator('button.se-place-search-button').click(); await page.waitForTimeout(2500);
    const items = f.locator('.se-place-map-search-result-item');
    let item = null;
    for (let i = 0; i < await items.count(); i++) {{ const t = await items.nth(i).innerText(); if (!want || t.includes(want)) {{ item = items.nth(i); break; }} }}
    if (item) {{ warn.push('장소(' + q + '): ' + (await item.innerText()).replace(/\\n/g, ' / ')); await item.scrollIntoViewIfNeeded(); await item.hover(); await page.waitForTimeout(300); await item.locator('button.se-place-add-button').click(); await page.waitForTimeout(600); await f.locator('.se-popup-placesMap .se-popup-button-confirm').first().click(); await page.waitForTimeout(1500); added = true; break; }}
  }}
  if (!added) {{ warn.push('장소 검색 결과 없음: ' + {J(query)} + (want ? ' (일치 조건: ' + want + ')' : '')); await f.locator('.se-popup-placesMap .se-popup-close-button').first().click(); await page.waitForTimeout(500); }} }}
{GOTO_END.replace(HEAD, '')}"""


def text_segment(blocks, align):
    out = [GOTO_END, "const warn = [];"]
    for b in blocks:
        t = b["type"]
        if t == "paragraph":
            if align == "center":
                out.append(ALIGN_CENTER)
            out += [type_line(l) for l in b["lines"]]
            out.append("await page.keyboard.press('Enter');")  # 문단 사이 빈 줄
        elif t == "heading":
            out += [HEADING, type_line(b["text"])]
        elif t == "list":
            out.append(LIST_ON)
            out += [type_line(i) for i in b["items"]]
            out.append("await page.keyboard.press('Enter');")  # 목록 빠져나오기
        elif t == "quote":
            out.append("await f.locator('button:has-text(\"인용구 추가\")').first().click(); await page.waitForTimeout(800);")
            out.append(typed(b['text']))
            out.append(GOTO_END.replace(HEAD, ""))
        elif t == "divider":
            out.append("await f.locator('button:has-text(\"구분선 추가\")').first().click(); await page.waitForTimeout(600);")
            out.append(GOTO_END.replace(HEAD, ""))
        elif t == "place":
            out.append(place(b["query"], b.get("match", "")))
    out.append(RET.replace("return await", "const comps = await").rstrip(";") + "; return {warn, comps};")
    return "\n".join(out)


def wrap(body):
    return "async (page) => {\n" + body + "\n}\n"


def publish_settings(category, tags):
    # 상단 "발행" 버튼은 설정 창만 연다. 창 안의 최종 "발행"(button[class^=confirm_btn])은 절대 누르지 않는다.
    # 카테고리를 고르면 주제도 자동으로 따라 바뀐다. 태그는 입력 후 Enter 하면 "#태그" 칩이 된다.
    return HEAD + f"""const warn = [];
await f.locator('button[class^=publish_btn]').click(); await page.waitForTimeout(1500);
const cat = {J(category)};
if (cat) {{
  await f.locator('button[class^=selectbox_button]').click(); await page.waitForTimeout(600);
  const items = f.locator('li[class^=item__]'); let picked = false;
  for (let i = 0; i < await items.count(); i++) {{ if ((await items.nth(i).innerText()).trim() === cat) {{ await items.nth(i).locator('button, label, input').first().click(); await page.waitForTimeout(600); picked = true; break; }} }}
  if (!picked) {{ warn.push('카테고리 없음: ' + cat + ' (있는 것: ' + (await items.allInnerTexts()).join(', ') + ')'); await f.locator('button[class^=selectbox_button]').click(); await page.waitForTimeout(300); }}
}}
const have = (await f.locator('[class^=tag__] [class^=text__]').allInnerTexts()).map(t => t.replace(/^#/, ''));
for (const t of {J(tags)}) {{
  if (have.includes(t)) continue;
  await f.locator('input[class^=tag_input]').click(); await page.keyboard.type(t); await page.keyboard.press('Enter'); await page.waitForTimeout(250);
}}
const result = {{ category: await f.locator('button[class^=selectbox_button]').innerText(), tags: await f.locator('[class^=tag__] [class^=text__]').allInnerTexts(), warn }};
await page.keyboard.press('Escape'); await page.waitForTimeout(600);
result.layerClosed = (await f.locator('div[class^=layer_popup][class*=is_show]').count()) === 0;
return result;"""


def main(src, dst):
    d = json.load(open(src, encoding="utf-8"))
    out = Path(dst)
    out.mkdir(parents=True, exist_ok=True)
    align = d.get("align", "left")

    title = HEAD + """const cancel = f.locator('.se-popup-button-cancel');
if (await cancel.isVisible().catch(() => false)) { await cancel.click(); await page.waitForTimeout(800); }
await f.locator('.se-documentTitle .se-text-paragraph').first().click();
""" + typed(d['title']) + "\n" + \
        "await f.locator('.se-component.se-text .se-text-paragraph').first().click();\n" + \
        "const count = await f.locator('button[class^=save_count_btn]').innerText();\nreturn {count};"
    (out / "00-title.js").write_text(wrap(title), encoding="utf-8")
    plan = [{"step": "00", "kind": "title", "file": "00-title.js"}]

    segs, cur = [], []
    for b in d["blocks"]:
        if b["type"] == "image":
            if cur:
                segs.append(("text", cur))
                cur = []
            segs.append(("image", b))
        else:
            cur.append(b)
    if cur:
        segs.append(("text", cur))

    for i, (kind, s) in enumerate(segs, 1):
        n = f"{i:02d}"
        if kind == "text":
            (out / f"{n}-text.js").write_text(wrap(text_segment(s, align)), encoding="utf-8")
            plan.append({"step": n, "kind": "text", "file": f"{n}-text.js"})
        else:
            goto = GOTO_END + "await f.locator('button:has-text(\"사진 추가\")').first().click();\nreturn 'clicked';"
            cap = HEAD + """const img = f.locator('.se-component.se-image').last();
for (let i = 0; i < 40; i++) { const src = await img.locator('img').first().getAttribute('src').catch(() => ''); if (src && src.includes('pstatic.net')) break; await page.waitForTimeout(500); }
await page.waitForTimeout(800);
"""
            if s["caption"]:
                cap += f"""await img.locator('img').first().click(); await page.waitForTimeout(400);
await img.locator('.se-caption .se-text-paragraph').click();
{typed(s['caption'])}
"""
            cap += RET
            (out / f"{n}-goto.js").write_text(wrap(goto), encoding="utf-8")
            (out / f"{n}-cap.js").write_text(wrap(cap), encoding="utf-8")
            plan.append({"step": n, "kind": "image", "goto": f"{n}-goto.js", "path": s["path"], "cap": f"{n}-cap.js"})

    (out / "99-publish-settings.js").write_text(
        wrap(publish_settings(d.get("category", ""), [t.lstrip("#").replace(" ", "") for t in d.get("tags", [])][:30])),
        encoding="utf-8")
    plan.append({"step": "99", "kind": "publish-settings", "file": "99-publish-settings.js"})

    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    for p in plan:
        print(p["step"], p["kind"], p.get("file") or p["path"].split("/")[-1])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
