# blog-auto-draft

사진 + 주제(md) + 첨부 글을 넣으면 Claude가 블로그 초안을 Markdown으로 써주는 프로젝트.

## 사용법

1. 글 폴더 만들기
   ```bash
   mkdir -p inputs/my-post/photos inputs/my-post/refs
   cp templates/topic.md inputs/my-post/topic.md
   ```
2. `topic.md` 작성, 사진은 `photos/`, 참고 글은 `refs/`에 넣기
3. 이 폴더에서 Claude Code를 열고 실행
   ```
   /blog-draft my-post    # 한 건만
   /blog-draft            # inputs/ 의 신규 건 전부
   ```
4. 진행 순서: 초안 작성 → Playwright로 Google → 네이버 → 로그인 → 블로그 글쓰기 → **임시저장**(발행은 안 함)
   - 로그인은 Playwright 크롬 창에서 직접 해야 합니다. "로그인 상태 유지"를 켜 두면 다음부터는 생략됩니다.
5. 임시저장에 성공한 건은 `done/<날짜>-<글이름>/` 으로 옮겨지고, `inputs/` 에는 새 건만 남습니다.

## 구조

```
.claude/skills/blog-draft/SKILL.md   초안 작성 + 네이버 임시저장 스킬
scripts/md_to_blocks.py              draft.md → 에디터 입력용 블록(JSON)
templates/topic.md                   주제 파일 템플릿
inputs/<글이름>/                      신규 입력 (topic.md, photos/, refs/)
drafts/<글이름>/                      작성 중 초안 (임시저장 실패 시 여기 남음)
done/<날짜>-<글이름>/                  완료 (input/, draft/)
```
