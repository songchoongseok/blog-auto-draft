# blog-auto-draft

주제(md) + 사진을 넣으면 Claude가 글을 써서 **네이버 블로그에 임시글로 저장**해 주는 프로젝트.
발행은 하지 않습니다. 임시글함에서 확인·수정한 뒤 직접 발행하면 됩니다.

## 사용법

1. 주제마다 `inputs/` 아래에 폴더를 하나씩 만들고, **`.md` 파일 1개 + 사진 n장**을 그 폴더에 함께 넣습니다.
   ```bash
   mkdir -p inputs/my-post
   cp templates/topic.md inputs/my-post/topic.md   # 파일 이름은 자유
   ```
   ```
   inputs/
   ├── 북한산-둘레길/   topic.md, 01.jpg, 02.jpg, ...
   └── 성수동-카페/     카페.md, a.heic, b.heic, ...
   ```
   - 참고할 글은 `.md` 안의 "참고 글"에 붙여 넣습니다.
2. 이 폴더에서 Claude Code를 열고 실행
   ```
   /blog-draft            # inputs/ 의 주제 폴더 전부 (폴더 N개 → 임시글 N개)
   /blog-draft my-post    # 특정 폴더만
   ```
3. Claude가 Playwright 브라우저로 Google → 네이버 → 블로그 글쓰기에 들어가 제목·본문·사진을 넣고 **임시저장**합니다.
   - 로그인은 Playwright 크롬 창에서 직접 해야 합니다. "로그인 상태 유지"를 켜 두면 다음부터는 생략됩니다.
   - 태그는 발행 창에 있어서 자동으로 넣지 않습니다. 추천 태그를 알려드리니 발행할 때 넣어 주세요.
4. 임시저장에 성공한 건은 `done/<날짜>-<주제폴더>/` 으로 옮겨지고, `inputs/` 에는 새 건만 남습니다.

## 구조

```
.claude/skills/blog-draft/SKILL.md   글 작성 + 네이버 임시저장 스킬
scripts/md_to_blocks.py              중간 원고(draft.md) → 에디터 입력용 블록(JSON)
templates/topic.md                   주제 파일 템플릿
inputs/<주제폴더>/                    신규 입력 (.md 1개 + 사진 n장)
drafts/<주제폴더>/                    중간 원고 — 네이버에 넣기 전 작업본, 임시저장 실패 시 여기 남음
done/<날짜>-<주제폴더>/               완료 (input/, draft/)
```
