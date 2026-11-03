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
| `title` | 본문에서 추론 | 글 제목(가제) |
| `tone` | `친근한 존댓말` | 문체 |
| `audience` | `일반 독자` | 대상 독자 |
| `length` | `보통` | `짧게`(~1,000자) / `보통`(~2,500자) / `길게`(~5,000자) |
| `tags` | 추론 | 태그 목록 |
| `structure` | 자유 | 원하는 목차가 있으면 리스트로 |

---

## A. 중간 원고 작성 (drafts/, 네이버에 넣기 전 작업본)

`drafts/<주제폴더>/draft.md`가 이미 있으면(지난번 임시저장이 실패한 경우) 새로 쓰지 않고 그 원고를 그대로 B로 넘긴다. 사용자가 다시 쓰라고 하면 그때만 새로 쓴다.

1. **읽기**
   - `.md` 파일을 읽고 frontmatter와 본문(주제, 전하고 싶은 내용, 메모, 붙여 둔 참고 글)을 파악한다.
   - 폴더 안의 사진을 모두 Read 도구로 **직접 보고** 각 사진에 무엇이 찍혔는지 파악한다. 파일명 순서를 기본 순서로 본다. HEIC처럼 Read로 열리지 않는 형식은 `sips -s format jpeg <원본> --out <scratchpad 경로>`로 변환해서 본다.
   - 사진 촬영 시각이 흐름에 도움이 되면 `mdls -name kMDItemContentCreationDate <파일>`로 확인한다.

2. **구성 잡기**
   - 주제의 핵심 메시지 한 줄을 정한다.
   - 사진을 글 흐름 안에 배치할 위치를 정한다. 모든 사진을 쓸 필요는 없고, 흐름에 맞지 않거나 중복된 사진은 빼되 마지막 보고에 무엇을 뺐는지 알린다.
   - `.md`에 붙여 둔 참고 글은 그대로 베끼지 말고 요약·재서술해 녹인다. 직접 인용은 짧게, 출처를 밝힌다.

3. **쓰기** — `drafts/<주제폴더>/draft.md`
   - 사진은 `drafts/<주제폴더>/images/`로 복사하고(HEIC는 jpg로 변환) 상대 경로 `images/<파일명>`으로 넣는다.
   - 각 사진 바로 아래 줄에 한 줄 캡션을 `*캡션*` 형태로 단다.
   - 네이버 에디터로 옮길 것이므로 문법은 `#`/`##` 제목, 문단, `-` 목록, `>` 인용, 이미지+캡션만 쓴다. 표·코드블록·중첩 목록은 쓰지 않는다.
   - 형식:

     ```markdown
     ---
     title: <제목>
     date: <오늘 날짜 YYYY-MM-DD>
     tags: [..]
     status: draft
     ---

     # <제목>

     <도입부>

     ## <소제목>
     ...

     ![<사진 설명>](images/01.jpg)
     *<캡션>*
     ```

   - 사실 확인이 필요한 부분이나 사용자가 채워야 할 부분은 `<!-- TODO: ... -->` 주석으로 남긴다(네이버에는 올라가지 않는다). 사진·`.md`에 없는 구체적 사실(가격, 지명, 날짜 등)을 지어내지 않는다.

---

## B. 네이버 블로그 임시저장 (Playwright MCP)

`mcp__playwright__*` 도구를 쓴다. 도구가 로드되지 않았으면 ToolSearch로 먼저 로드한다. 페이지 구조는 바뀔 수 있으므로 **좌표나 ref를 외워 쓰지 말고 매 단계 `browser_snapshot`으로 요소를 찾아** 누른다. 스냅샷이 길면 `filename`으로 저장해 grep 한다.

### B-1. 에디터에 넣을 블록 만들기

```bash
python3 scripts/md_to_blocks.py drafts/<주제폴더>/draft.md
```

출력 JSON의 `title`, `tags`, `blocks`(heading / paragraph / list / quote / image)를 순서대로 입력한다. 이미지 `path`는 절대 경로다.

### B-2. Google → 네이버 → 로그인 확인

1. `browser_navigate`로 `https://www.google.com` 을 연다.
2. combobox "검색"에 `네이버`를 입력하고 Enter(`browser_type`, `submit: true`).
   - "비정상적인 트래픽"·reCAPTCHA 화면이 나오면 **풀지 말고** 사용자에게 Playwright 창에서 직접 풀어 달라고 하고, 검색 결과가 뜰 때까지 기다린다.
3. 검색 결과의 링크 "네이버 NAVER https://www.naver.com" 을 클릭한다.
4. 로그인 여부는 쿠키로 확인한다:
   ```js
   async (page) => (await page.context().cookies('https://www.naver.com')).some(c => c.name === 'NID_AUT')
   ```
   - `true` → B-3으로.
   - `false` → 메인의 링크 "NAVER 로그인"을 클릭하고 `page.bringToFront()`로 창을 앞으로 띄운다.
5. **ID·비밀번호는 Claude가 입력하지 않는다.** 계정 정보를 채팅으로 받아도 쓰지 않는다. 사용자에게 이렇게 알린다:
   > Playwright 크롬 창("Chrome이 자동화된 테스트 소프트웨어에 의해 제어되고 있습니다" 표시가 있는 창)에서 직접 로그인해 주세요. "로그인 상태 유지"를 체크하면 다음부터는 이 단계가 생략됩니다.

   그 다음 아래 코드로 `NID_AUT` 쿠키가 생길 때까지 최대 5분 기다린다. 시간이 지나도 안 생기면 사용자에게 다시 묻는다.
   ```js
   async (page) => { const t = Date.now(); while (Date.now() - t < 290000) { if ((await page.context().cookies('https://www.naver.com')).some(c => c.name === 'NID_AUT')) return true; await page.waitForTimeout(3000); } return false; }
   ```

### B-3. 블로그 → 글쓰기

1. naver.com 에서 링크 "블로그"를 클릭한다 → **새 탭**(section.blog.naver.com)으로 열린다. `browser_tabs` select로 그 탭을 고른다.
2. 블로그 홈의 링크 "글쓰기"를 클릭한다 → 또 **새 탭**(`blog.naver.com/<블로그ID>?Redirect=Write`)이 열린다. 그 탭을 고른다.
3. 4초쯤 기다린다. 에디터(스마트에디터 ONE)는 **`mainFrame` iframe 안**에 있다. 이후 모든 조작은 `const f = page.frame('mainFrame')` 기준이다.
4. 팝업이 있으면 정리한다(테스트 때는 없었음).
   - "작성 중인 글이 있습니다" → **취소**(이전 글을 불러오지 않는다).
   - 도움말·툴팁 → 닫기.
5. 시작 전 임시글 개수를 기록해 둔다: `f.locator('button[class^=save_count_btn]').innerText()`.

### B-4. 내용 입력

입력은 `browser_run_code_unsafe`로 블록 몇 개씩 묶어서 하고, 묶음마다 아래 확인 코드로 컴포넌트 순서를 점검한다.

```js
// 확인용: 에디터 컴포넌트 목록
async (page) => page.frame('mainFrame').evaluate(() => [...document.querySelectorAll('.se-component')].map(c => c.className.split(' ')[1] + ' | ' + c.innerText.slice(0, 40).replace(/\n/g, '/')))
```

검증된 조작법(문자열은 블록 JSON 값으로 바꿔 넣는다. 따옴표·역슬래시는 JS 문자열로 이스케이프):

| 블록 | 방법 | 결과 컴포넌트 |
|---|---|---|
| 제목 | `f.locator('.se-documentTitle .se-text-paragraph').first().click()` → `page.keyboard.type(title)` | `se-documentTitle` |
| 본문 시작 | `f.locator('.se-component.se-text .se-text-paragraph').first().click()` | |
| `paragraph` | `page.keyboard.type(text)` → `Enter` | `se-text` |
| `heading` | `f.locator('button:has-text("문단 서식 변경")').first().click()` → `f.locator('button.__se-sentry:visible', {hasText: '소제목'}).first().click()` → type → `Enter`(다음 줄은 자동으로 "본문"으로 돌아옴) | `se-sectionTitle` |
| `list` | `f.locator('button:has-text("목록 열기")').first().click()` → `f.locator('button.se-toolbar-option-icon-button:visible', {hasText: '기호목록'}).first().click()` → 항목마다 type + `Enter` → 끝에 `Enter` 한 번 더(목록 빠져나옴) | `se-text` 안의 `ul` |
| `image` | 아래 "사진" 절차 | `se-image` |
| `quote` | 커서를 마지막 본문 줄 끝에 둔 뒤 `f.locator('button:has-text("인용구 추가")').first().click()` → 800ms 대기 → type | `se-quotation` |

**사진**
1. 커서가 본문 마지막 줄에 있는 상태에서 `browser_click`으로 툴바 버튼 "사진 추가"를 누른다(run_code 안에서 `waitForEvent('filechooser')`를 쓰면 MCP가 먼저 가로채서 안 됨).
2. 파일 선택 모달이 뜨면 `browser_file_upload`에 `path`를 넘긴다. **업로드 허용 경로는 Claude Code를 연 작업 폴더 아래뿐**이다(scratchpad·/tmp 불가). `drafts/<주제폴더>/images/`의 절대 경로를 쓴다.
3. 3초 기다려 `se-image` 컴포넌트의 `img src`가 `blogfiles.pstatic.net`인지 확인한다. 첫 사진은 자동으로 "대표" 사진이 된다.
4. 오른쪽에 "라이브러리" 패널이 열리는데, 입력에는 지장이 없다.
5. 캡션이 있으면 **사진을 먼저 클릭해야** 캡션 칸이 보인다:
   ```js
   const img = f.locator('.se-component.se-image').last();
   await img.locator('img').first().click();
   await img.locator('.se-caption .se-text-paragraph').click();
   await page.keyboard.type(caption);
   ```
6. 사진 뒤에는 빈 `se-text`가 자동으로 생긴다. 이어서 쓰려면 `f.locator('.se-component.se-text').last().locator('.se-text-paragraph').last().click()` → `End`.

**인용구 다음에 이어 쓰기**: 인용구 뒤에는 본문 칸이 없다. 인용구 아래 빈 공간을 클릭하면 새 `se-text`가 생긴다.
```js
const box = await f.locator('.se-component.se-quotation').last().boundingBox();
await page.mouse.click(box.x + box.width / 2, box.y + box.height + 25);
```

**태그**: 태그 입력란은 에디터가 아니라 "발행" 설정 창에 있다. 실수로 발행될 위험이 있어 **태그는 넣지 않는다**. 보고에 추천 태그 목록을 적어 사용자가 발행할 때 넣게 한다.

다 넣은 뒤 `browser_take_screenshot`(`fullPage: true`)으로 화면을 직접 보고, 블록 JSON과 순서·개수가 맞는지 확인한다.

### B-5. 임시저장

1. **"저장" 버튼만** 누른다. **"발행" 버튼은 어떤 경우에도 누르지 않는다.**
   ```js
   await f.locator('button[class^=save_btn]').click();
   ```
2. 성공 조건 두 가지를 모두 확인한다.
   - 알림 "임시저장이 완료되었습니다."가 뜬다(`[class*=toast], [role=alert]` 등에서 텍스트 확인).
   - `button[class^=save_count_btn]` 숫자가 B-3-5에서 기록한 값보다 1 늘었다.
3. 실패하거나 확인이 안 되면 C로 가지 말고, 그 건은 `inputs/`, `drafts/`에 그대로 둔 채 이유를 보고한다(다음 실행 때 같은 초안으로 다시 시도된다).
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

`$dest`가 이미 있으면 `-2`, `-3`을 붙인다.

## 보고

처리한 건마다 채팅에 짧게:
- 결과: 임시저장 완료(→ `done/...` 경로) / 실패(이유, 남겨둔 위치)
- 제목 후보 2~3개
- 쓰지 않은 사진과 이유, 남긴 TODO 개수
- 발행할 때 넣을 추천 태그
