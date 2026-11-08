# blog-auto-draft

주제(md) + 사진을 넣으면 Claude가 글을 써서 **네이버 블로그에 임시글로 저장**해 주는 프로젝트.
발행은 하지 않습니다. 임시글함에서 확인·수정한 뒤 직접 발행하면 됩니다.

## 사용법

1. `inputs/`에 준비된 **`topic.md`를 채우고, 사진 n장을 같은 `inputs/`에 바로** 넣습니다(하위 폴더 없음, 한 번에 한 건).
   ```
   inputs/
   ├── topic.md
   ├── IMG_0001.jpg
   └── IMG_0002.heic ...
   ```
   - `topic.md`가 없으면 `cp templates/topic.md inputs/topic.md`
   - 참고할 글은 `topic.md` 안의 "참고 글"에 붙여 넣습니다.
2. 이 폴더에서 Claude Code를 열고 실행
   ```
   /blog-draft
   ```
3. Claude가 Playwright 브라우저로 Google → 네이버 → 블로그 글쓰기에 들어가 제목·본문·사진을 넣고 **임시저장**합니다.
   - 로그인은 Playwright 크롬 창에서 직접 해야 합니다. "로그인 상태 유지"를 켜 두면 다음부터는 생략됩니다.
   - 먼저 `inputs/result.md`(글 + 사진 위치)를 보여 드리고, 확인 후 "작성해줘"라고 하면 네이버에 넣습니다.
   - 발행 설정 창을 열어 카테고리·태그까지 넣고 닫은 뒤 임시저장합니다(발행 버튼은 누르지 않음).
4. 임시저장에 성공하면 `done/<제목>/` 한 폴더에 topic.md·원본 사진·draft.md가 모이고, `inputs/`에는 다음 건용 빈 `topic.md`가 다시 준비됩니다.

## 구조

```
.claude/skills/blog-draft/SKILL.md   글 작성 + 네이버 임시저장 스킬
scripts/md_to_blocks.py              중간 원고(draft.md) → 에디터 입력용 블록(JSON)
scripts/naver_segments.py            블록(JSON) → 에디터 입력용 Playwright 코드 조각
templates/topic.md                   주제 파일 템플릿
inputs/                              신규 입력 (topic.md 1개 + 사진 n장)
drafts/                              중간 원고 — 네이버에 넣기 전 작업본, 임시저장 실패 시 여기 남음
done/<제목>/                          완료 (topic.md, 원본 사진, draft.md)
```
