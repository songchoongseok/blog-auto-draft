---
name: blog-draft
description: inputs/ 아래 주제 폴더(.md 1개 + 사진 n장)마다 글을 써서 Playwright로 네이버 블로그에 임시글로 저장하고(발행 안 함), 완료된 건을 done/ 으로 옮긴다. 하위 폴더가 여러 개면 전부 처리한다. 사용자가 블로그 글 작성, /blog-draft, "inputs 작업해줘", "네이버에 임시저장해줘" 등을 요청할 때 사용.
argument-hint: [주제폴더] (생략하면 inputs/ 의 주제 폴더 전부)
---

# 네이버 블로그 임시글 작성 (중간 원고 → 네이버 임시저장 → 완료 정리)

## 대상 고르기

- `inputs/` 아래 **하위 폴더 하나 = 주제 하나 = 네이버 임시글 하나**다.
- 기본은 `inputs/` 아래 하위 폴더 **전부**(`_example` 제외)를 이름순으로 처리한다. 사용자가 여러 주제를 모아둔 것이므로 몇 개든 묻지 않고 다 한다. 없으면 "신규 건 없음"이라고 알리고 끝낸다.
- 인자나 요청으로 특정 폴더를 지정하면 그 폴더만 처리한다.
- 각 건은 A → B → C 순서로 끝까지 처리한 뒤 다음 건으로 넘어간다. 한 건이 실패해도 멈추지 말고 남겨둔 채 다음 건을 진행하고, 마지막에 한꺼번에 보고한다.
- 네이버 로그인(B-2)은 첫 건에서 한 번만 확인하면 된다.

## 폴더 구조

```
inputs/<주제폴더>/        신규 입력: .md 파일 1개 + 사진 n장 (하위 폴더 없이 한 곳에)
drafts/<주제폴더>/        중간 원고 (draft.md, images/) — 임시저장 전까지 여기 남는다
done/<YYYY-MM-DD>-<주제폴더>/
├── input/               완료된 입력 (inputs/<주제폴더>/ 를 옮긴 것)
└── draft/               완료된 중간 원고 (drafts/<주제폴더>/ 를 옮긴 것)
```

- `.md` 파일 이름은 자유다(`topic.md`, `주제.md` 등). 폴더 안의 `.md`가 0개이거나 2개 이상이면 그 건은 건너뛰고 보고한다.
- 사진: `jpg/jpeg/png/heic/webp/gif` (대소문자 무관). 사진이 0장이어도 글은 쓴다.
- 그 밖의 파일(`.DS_Store` 등)은 무시한다.

`.md` 맨 위 frontmatter 항목(모두 선택, 없으면 기본값. frontmatter 자체가 없어도 된다):

| 키 | 기본값 | 의미 |
|---|---|---|
| `title` | 본문에서 추론 | 글 제목(가제). 아래 "제목" 규칙에 맞게 다듬는다 |
| `tone` | `친근한 존댓말` | 문체 |
| `audience` | `일반 독자` | 대상 독자 |
| `length` | `보통` | `짧게`(~1,000자) / `보통`·`중간`(1,500~2,500자) / `길게`(~4,000자) |
| `tags` | 추론 | 태그 목록 |
| `structure` | 자유 | 원하는 목차가 있으면 리스트로 |
| `place` | 없음 | 네이버 장소 검색어(예: `몽브레뉴 가평`). 있으면 기본정보 아래 장소 지도를 넣는다 |
| `align` | `left` | 본문 정렬. `center`면 가운데 정렬(감성 후기 스타일) |

---

## A. 중간 원고 작성 (drafts/, 네이버에 넣기 전 작업본)

`drafts/<주제폴더>/draft.md`가 이미 있으면(지난번 임시저장이 실패한 경우) 새로 쓰지 않고 그 원고를 그대로 B로 넘긴다. 사용자가 다시 쓰라고 하면 그때만 새로 쓴다.

1. **읽기**
   - `.md` 파일을 읽고 frontmatter와 본문(주제, 내 경험, 메모, 붙여 둔 참고 글)을 파악한다.
   - 폴더 안의 사진을 모두 **직접 보고** 각 사진에 무엇이 찍혔는지 파악한다. 원본이 크면 `sips -Z 700 <원본> --out <scratchpad>/NN.jpg`로 줄여서 본다(HEIC도 이걸로 변환된다). 메뉴판·안내문처럼 글씨가 중요한 사진은 `sips -Z 1900`으로 크게 보고 필요한 부분만 `sips -c`로 잘라 읽는다.
   - 촬영 시각이 흐름에 도움이 되면 `mdls -name kMDItemContentCreationDate <파일>`로 확인한다(UTC로 나오므로 한국 시간은 +9시간).

2. **구성 잡기** — 아래 "글쓰기 가이드"를 따른다.
   - 사진을 동선 순서로 묶어 섹션을 정한다. 흐름에 맞지 않거나 중복된 사진은 빼되 보고에 알린다.
   - **개인정보가 보이는 사진은 뺀다**: 차량 번호판이 읽히는 사진, 모르는 사람(특히 아이)이 크게·정면으로 찍힌 사진, 카드 번호·영수증 개인정보. 빼기 아까운 사진은 넣고 `<!-- TODO: N번 사진 얼굴 모자이크 -->`를 남긴다.
   - `.md`에 붙여 둔 참고 글은 그대로 베끼지 말고 요약·재서술해 녹인다. 직접 인용은 짧게, 출처를 밝힌다.

3. **쓰기** — `drafts/<주제폴더>/draft.md`
   - 사진은 `sips -Z 2000 -s format jpeg -s formatOptions 85 <원본> --out drafts/<주제폴더>/images/NN.jpg`로 줄여 복사하고 상대 경로 `images/NN.jpg`로 넣는다(업로드가 빨라지고 HEIC도 jpg가 된다).
   - 네이버 에디터로 옮길 수 있는 문법만 쓴다. `scripts/md_to_blocks.py`가 이렇게 바꾼다:

     | 원고 문법 | 에디터 |
     |---|---|
     | `# 제목` | 제목 칸(frontmatter `title`이 우선) |
     | `## 소제목` | 소제목 |
     | 연속된 줄 | 한 줄씩 그대로(줄바꿈 유지) |
     | 빈 줄 | 문단 사이 빈 줄 |
     | `- 항목` | 글머리 목록 |
     | `> 문장` | 인용구 |
     | `---` | 구분선 |
     | `[[장소: 검색어]]` | 네이버 장소 지도 |
     | `![설명](images/NN.jpg)` | 사진 |
     | 사진 바로 다음 줄 `*캡션*` | 사진 캡션(선택) |
     | `<!-- ... -->` | 올라가지 않음(TODO용) |

   - 표·코드블록·중첩 목록·굵게·링크 문법은 쓰지 않는다(에디터에서 렌더링되지 않는다).
   - 사실 확인이 필요한 부분이나 사용자가 채워야 할 부분은 `<!-- TODO: ... -->`로 남긴다. 사진·`.md`에 없는 구체적 사실(가격, 지명, 맛, 동행인, 날짜 등)을 **지어내지 않는다**. 사진 속 메뉴판·안내문에서 읽은 내용은 "방문 당시 기준"이라고 밝힌다.

### 글쓰기 가이드 (요즘 네이버 블로그 후기 스타일)

실제 상위 노출 후기 글을 분석한 결과와 업계 권장 사항을 정리한 것이다. **"정보를 빨리 찾게 해 주고, 직접 다녀온 사람의 생생한 말투"**가 핵심이다. 정돈된 에세이나 보도자료처럼 쓰면 "처음 쓰는 블로그"처럼 보인다.

**제목** (25~40자)
- `지역 + 업종 키워드 + 상호 + 특징 2~3개` 순서. 검색어가 앞에 온다.
- 예: `가평 대형카페 몽브레뉴 | 정원 산책하기 좋은 베이커리카페 (주차·메뉴·가격)`
- 같은 키워드를 두 번 이상 넣지 않는다. "최고", "완벽" 같은 과장은 쓰지 않는다.

**글 순서**
1. **인사 + 방문 계기** (2~4줄): "안녕하세요 :)" 같은 짧은 인사, 언제·왜 갔는지, 한 줄 결론(어떤 사람에게 추천인지).
2. **기본정보 블록** (도입 바로 뒤): 소제목 `기본정보` 아래 `✔️ 주소 :`, `✔️ 영업시간 :`, `✔️ 주차 :`, `✔️ 가격대 :`, `✔️ 특징 :`(애견동반·노키즈존 등)을 한 줄씩. 모르는 항목은 줄을 빼고 TODO로 남긴다. `place`가 있으면 그 아래 `[[장소: 검색어]]`.
3. **본문**: 실제 동선 순서(도착·주차 → 외관 → 주문·메뉴 → 자리·실내 → 야외·산책 → 기타 팁). 섹션마다 소제목 하나, 사진 2~4장, 사진마다 짧은 설명 2~4줄.
4. **좋았던 점 / 아쉬운 점**: 둘 다 쓴다. 아쉬운 점이 없으면 오히려 광고처럼 보인다(사람 많음, 가격대, 웨이팅 등 자료에 있는 것만).
5. **마무리**: `---` 구분선 뒤 소제목 `한 줄 정리`와 `✔️` 3~4줄(추천 대상, 방문 팁, 재방문 의사). 장소 지도를 위에 넣었으면 다시 넣지 않는다.

**문장과 줄바꿈** (모바일에서 읽기 좋게)
- 한 줄은 15~25자 안팎에서 끊는다. 의미 단위(쉼표, 접속사 앞)로 끊고, 한 문장이 두세 줄이 돼도 된다.
- 2~4줄마다 빈 줄을 넣는다. 한 덩어리에는 한 가지 이야기만.
- 사진 설명은 캡션보다 **사진 바로 위·아래 본문 줄**로 쓴다. 캡션은 꼭 필요할 때만 짧게.

**말투**
- 친근한 구어체: `~했어요`, `~더라고요`, `~이었는데요`, `~추천해요`. 문장 끝을 계속 같은 어미로 끝내지 않는다.
- 감정·감각 표현을 구체적으로: "좋았어요" 대신 무엇이 어떻게 좋았는지(넓이, 햇빛, 소리, 온도, 맛, 식감).
- 이모지는 정보 블록의 `✔️`, 섹션당 0~1개 정도(☕️ 🌿 🥐 🙂)만. `!!`, `ㅎㅎ`도 가끔만.
- AI 티 나는 표현 금지: "~할 수 있습니다", "다양한", "완벽한", "결론적으로", "~라고 할 수 있죠", "한마디로", 세 가지씩 나열하는 습관.
- 1인칭 경험("저는", "저희는")은 `.md`에 동행 정보가 있을 때만 구체화한다. 없으면 "둘이", "가족이" 같은 동행을 지어내지 않는다.

**분량과 사진**
- 본문 1,500~2,500자(`length` 기준), 사진 15~25장이 일반적이다. 사진이 많으면 글도 그만큼 섹션을 나눠 길어지게 한다.
- 키워드(지역·업종·상호)는 도입·기본정보·마무리에 자연스럽게 한 번씩만. 나열하지 않는다.

**경험 정보가 부족할 때**
- 맛·주문 메뉴·가격·동행·아쉬운 점 등 핵심 경험이 `.md`에 없으면, 그 자리에 TODO를 남기고 보고에 "이 정보를 `.md`의 '내 경험'에 적어 주면 더 자연스러워진다"고 알린다. 추측으로 채우지 않는다.

**원고 예시(구조 참고용)**

```markdown
---
title: 가평 대형카페 몽브레뉴 | 정원 산책하기 좋은 베이커리카페 (주차·메뉴·가격)
date: 2026-11-03
tags: [가평카페, 가평대형카페, 몽브레뉴]
place: 몽브레뉴 가평
---

안녕하세요 :)
주말에 가평 쪽으로 바람 쐬러 갔다가
정원이 넓다는 카페에 들러봤어요.

결론부터 말하면
천천히 걷는 거 좋아하시면 꼭 가보세요!

## 기본정보

✔️ 주소 : <자료에 있을 때만>
✔️ 주차 : 전용 주차장 있음
✔️ 가격대 : 음료 7,500~9,000원 (방문 당시 메뉴판)

[[장소: 몽브레뉴 가평]]

---

## 도착하자마자 보이는 건물

주차하고 올라가면
이렇게 큰 건물이 먼저 반겨줘요.

![외관](images/01.jpg)

...

---

## 한 줄 정리

✔️ 정원 산책 좋아하는 커플·가족에게 추천
✔️ 주말 낮엔 사람이 많으니 오전 방문 추천
✔️ 재방문 의사 있어요 🙂
```

---

## B. 네이버 블로그 임시저장 (Playwright MCP)

`mcp__playwright__*` 도구를 쓴다. 도구가 로드되지 않았으면 ToolSearch로 먼저 로드한다. 페이지 구조가 바뀌어 아래 방법이 안 되면 `browser_snapshot`(길면 `filename`으로 저장 후 grep)으로 요소를 다시 찾는다.

### B-1. 입력 코드 만들기

```bash
python3 scripts/md_to_blocks.py drafts/<주제폴더>/draft.md > <scratchpad>/blocks.json
python3 scripts/naver_segments.py <scratchpad>/blocks.json <작업폴더>/.playwright-mcp/seg-<주제폴더>
```

- 두 번째 출력 폴더는 **Claude Code 작업 폴더 아래**여야 한다(`browser_run_code_unsafe`의 `filename`과 `browser_file_upload`는 작업 폴더 밖 파일을 못 읽는다). `.playwright-mcp/`는 gitignore 대상이다.
- 출력되는 `plan.json`이 실행 순서다: `00-title.js` → 구간별 `NN-text.js` 또는 사진 3단계(`NN-goto.js` → `browser_file_upload(path)` → `NN-cap.js`).
- `filename`의 상대 경로는 Playwright MCP 루트(Claude Code를 처음 연 폴더) 기준이다. 헷갈리면 절대 경로를 쓴다.
- 같은 폴더에 다시 생성할 때는 지우지 말고 그냥 덮어쓴다(`rm`은 안전 검사에 막힐 수 있다).

### B-2. Google → 네이버 → 로그인 확인

1. `browser_navigate`로 `https://www.google.com` 을 연다.
2. 검색창에 `네이버`를 입력하고 검색 결과의 링크 "네이버 NAVER https://www.naver.com" 을 클릭한다. 한 번에:
   ```js
   async (page) => { const box = page.getByRole('combobox', { name: '검색' }); await box.fill('네이버'); await box.press('Enter'); await page.waitForLoadState('domcontentloaded'); const link = page.getByRole('link', { name: /네이버 NAVER https:\/\/www\.naver\.com/ }).first(); await link.waitFor({timeout: 10000}); await link.click(); await page.waitForURL(/naver\.com/); return (await page.context().cookies('https://www.naver.com')).some(c => c.name === 'NID_AUT'); }
   ```
   - "비정상적인 트래픽"·reCAPTCHA 화면이 나오면 **풀지 말고** 사용자에게 Playwright 창에서 직접 풀어 달라고 하고, 검색 결과가 뜰 때까지 기다린다.
3. 반환값(`NID_AUT` 쿠키 여부)이 `true`면 B-3으로. `false`면 메인의 링크 "NAVER 로그인"을 클릭하고 `page.bringToFront()`로 창을 앞으로 띄운다.
4. **ID·비밀번호는 Claude가 입력하지 않는다.** 계정 정보를 채팅으로 받아도 쓰지 않는다. 사용자에게 이렇게 알린다:
   > Playwright 크롬 창("Chrome이 자동화된 테스트 소프트웨어에 의해 제어되고 있습니다" 표시가 있는 창)에서 직접 로그인해 주세요. "로그인 상태 유지"를 체크하면 다음부터는 이 단계가 생략됩니다.

   그 다음 아래 코드로 `NID_AUT` 쿠키가 생길 때까지 최대 5분 기다린다. 시간이 지나도 안 생기면 사용자에게 다시 묻는다.
   ```js
   async (page) => { const t = Date.now(); while (Date.now() - t < 290000) { if ((await page.context().cookies('https://www.naver.com')).some(c => c.name === 'NID_AUT')) return true; await page.waitForTimeout(3000); } return false; }
   ```

### B-3. 블로그 → 글쓰기

1. 지난 실행에서 남은 탭이 있으면 먼저 닫는다(`browser_tabs` close). 글쓰기 탭을 떠날 때 "beforeunload" 확인 창이 뜨면 `browser_handle_dialog(accept: true)`.
2. naver.com 에서 "블로그" → 새 탭(블로그 홈) → "글쓰기" → 또 새 탭이 열린다. 한 번에:
   ```js
   async (page) => { const ctx = page.context(); const [blog] = await Promise.all([ctx.waitForEvent('page'), page.getByRole('link', { name: '블로그', exact: true }).first().click()]); await blog.waitForLoadState('domcontentloaded'); const [editor] = await Promise.all([ctx.waitForEvent('page'), blog.getByRole('link', { name: '글쓰기' }).first().click()]); await editor.waitForLoadState('domcontentloaded'); await editor.waitForTimeout(5000); return ctx.pages().map(p => p.url()); }
   ```
3. `browser_tabs` select로 **글쓰기 탭**(`blog.naver.com/<블로그ID>?Redirect=Write`)을 고른다. 이후 모든 코드는 이 탭에서 돈다. 에디터는 `mainFrame` iframe 안에 있다.
4. `00-title.js`를 실행한다. "작성 중인 글이 있습니다" 팝업을 **취소**하고 제목을 넣은 뒤, 시작 전 임시글 개수(`count`)를 돌려준다. 이 값을 기록해 둔다.

### B-4. 내용 입력

`plan.json` 순서대로 실행한다. 각 코드는 마지막 컴포넌트 4개를 돌려주므로 매번 의도대로 쌓였는지 본다.

- **글 구간**: `browser_run_code_unsafe(filename: ".../NN-text.js")`. 반환값의 `warn`에 장소 검색 결과가 찍힌다. **장소 결과가 원하는 가게가 아니면**(이름·지역이 다름) 그 지도 컴포넌트를 지우고 보고에 적는다.
- **사진 구간** — 세 호출을 한 메시지에 순서대로 보내도 된다:
  1. `NN-goto.js` → 파일 선택 모달이 뜬다(run_code 안에서 `waitForEvent('filechooser')`를 쓰면 MCP가 먼저 가로채서 안 된다).
  2. `browser_file_upload(paths: [path])` — 작업 폴더 아래 절대 경로만 된다.
  3. `NN-cap.js` → 업로드 완료(`img src`가 `blogfiles.pstatic.net`)를 기다린 뒤 캡션이 있으면 넣는다.
- 첫 사진은 자동으로 "대표" 사진이 된다. 사진을 올리면 오른쪽에 "라이브러리" 패널이 열리지만 입력에는 지장이 없다.
- 글쓰기 탭이 갑자기 닫히면 B-3부터 다시 한다(이미 넣은 내용은 자동저장에 남지만 불러오지 말고 새로 쓴다).

검증된 에디터 조작(코드 생성기가 쓰는 방법, 페이지가 바뀌었을 때 참고):

| 블록 | 방법 | 결과 컴포넌트 |
|---|---|---|
| 제목 | `.se-documentTitle .se-text-paragraph` 클릭 → type | `se-documentTitle` |
| 문단 줄 | type → `Enter` (줄마다) / 문단 끝에 `Enter` 한 번 더 | `se-text` |
| 이모지 | `keyboard.type`은 `✔️`·`☁️`처럼 FE0F가 붙은 이모지를 "✔✔️"로 두 번 찍는다. 이모지 부분만 `keyboard.insertText`로 넣는다(문장 전체를 `insertText`로 넣으면 일부가 사라진다) | |
| 소제목 | "문단 서식 변경" → `button.__se-sentry` "소제목" → type → `Enter`(자동으로 본문 복귀) | `se-sectionTitle` |
| 목록 | "목록 열기" → "기호목록" → 항목마다 type+`Enter` → `Enter` 한 번 더(빠져나옴) | `se-text` 안 `ul` |
| 인용구 | "인용구 추가" → 800ms → type → 아래 빈 곳 클릭으로 빠져나옴 | `se-quotation` |
| 구분선 | "구분선 추가" (뒤에 본문 칸 자동 생성) | `se-horizontalLine` |
| 장소 | "장소 추가" → `input[placeholder="장소명을 입력하세요."]` → "검색" → 결과에 **마우스를 올려야** 보이는 `.se-place-add-button` → `.se-popup-button-confirm` | `se-placesMap` |
| 정렬 | "정렬 열기" → "가운데 정렬" 등 | 문단 `align-center` |
| 사진 캡션 | 사진 `img`를 **먼저 클릭해야** `.se-caption .se-text-paragraph`가 보임 | |
| 끝으로 이동 | 마지막이 `se-text`면 그 마지막 줄 클릭+`End`, 아니면 마지막 컴포넌트 아래 25px 클릭 | |

**태그**: 태그 입력란은 에디터가 아니라 "발행" 설정 창에 있다. 실수로 발행될 위험이 있어 **태그는 넣지 않는다**. 보고에 추천 태그 목록을 적어 사용자가 발행할 때 넣게 한다.

**최종 점검**: 다 넣은 뒤 컴포넌트를 세어 원고와 맞춰 본다(제목, 소제목 목록, 사진 수, 빈 캡션 수, 장소 지도 유무). 화면 밖 사진은 지연 로딩이라 `src`가 `data:image/svg`로 보일 수 있다. `scrollIntoViewIfNeeded()` 후 다시 확인한다.

### B-5. 임시저장

1. **"저장" 버튼만** 누른다. **"발행" 버튼은 어떤 경우에도 누르지 않는다.**
   ```js
   async (page) => { const f = page.frame('mainFrame'); const cnt = f.locator('button[class^=save_count_btn]'); const before = await cnt.innerText(); await f.locator('button[class^=save_btn]').click(); let toast = ''; for (let i = 0; i < 20 && !toast.includes('임시저장'); i++) { await page.waitForTimeout(500); toast = await f.evaluate(() => [...document.querySelectorAll('[class*=toast], [class*=noti], [role=alert]')].filter(e => e.offsetParent).map(e => e.innerText).join(' | ')); } await page.waitForTimeout(1500); return {before, after: await cnt.innerText(), toast: toast.split(' | ')[0]}; }
   ```
2. 성공 조건 두 가지를 모두 확인한다.
   - 알림 "임시저장이 완료되었습니다."가 뜬다.
   - 임시글 숫자가 B-3-4에서 기록한 값보다 1 늘었다.
3. 실패하거나 확인이 안 되면 C로 가지 말고, 그 건은 `inputs/`, `drafts/`에 그대로 둔 채 이유를 보고한다(다음 실행 때 같은 원고로 다시 시도된다).
4. 여러 건을 처리할 때는 다음 건마다 B-3(블로그 홈 → 글쓰기)부터 다시 한다. 쓰던 글쓰기 탭은 닫는다.

---

## C. 완료 정리

B-5가 성공한 건만 옮긴다.

```bash
dest="done/$(date +%F)-<주제폴더>"
mkdir -p "$dest"
mv "inputs/<주제폴더>" "$dest/input"
mv "drafts/<주제폴더>" "$dest/draft"
```

`$dest`가 이미 있으면 `-2`, `-3`을 붙인다. `done/`은 gitignore 대상이라 GitHub에 올라가지 않는다.

입력 코드 폴더(`.playwright-mcp/seg-<주제폴더>`)는 작업 폴더 안이라 `rm -rf`가 안전 검사에 막힐 수 있다. 막히면 지우지 말고 보고에 남긴다.

## 보고

처리한 건마다 채팅에 짧게:
- 결과: 임시저장 완료(→ `done/...` 경로) / 실패(이유, 남겨둔 위치)
- 제목 후보 2~3개
- 쓰지 않은 사진과 이유, 남긴 TODO 목록
- `.md`에 더 적어 주면 좋은 경험 정보(맛, 주문 메뉴, 동행, 아쉬운 점 등)
- 발행할 때 넣을 추천 태그
