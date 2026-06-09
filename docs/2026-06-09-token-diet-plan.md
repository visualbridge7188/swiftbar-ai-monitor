# 토큰 다이어트 및 MCP 로컬 격리 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 에이전트 환경의 토큰 누수를 차단하기 위해 9개 스킬을 비활성화/백업하고, stitch MCP를 삭제하며, 한국법률 및 통계 MCP 서버를 특정 로컬 프로젝트로 격리합니다.

**Architecture:** 로컬 프로젝트 `skill-rules.json` 수정, 스킬 디렉토리 격리 스크립트 실행, 그리고 타겟 경로에 `mcp_config.json`을 작성하는 3개의 태스크로 나누어 진행합니다.

**Tech Stack:** Bash, JSON/Node.js, Git

---

### Task 1: 스킬 자동 트리거 비활성화

**Files:**
- Modify: `/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/skills/skill-rules.json`

- [ ] **Step 1: `skill-rules.json` 백업 생성**
  Run: `cp "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/skills/skill-rules.json" "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/skills/skill-rules.json.bak"`
  Expected: `.bak` 복사본 생성 완료

- [ ] **Step 2: `skill-rules.json` 에서 해당 스킬 트리거 블록 삭제**
  `/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/skills/skill-rules.json` 파일에서 `nextjs-frontend-guidelines`, `vercel-react-best-practices`, `fastapi-backend-guidelines` 스키마 블록을 완전히 삭제합니다.
  
- [ ] **Step 3: JSON 파일 구문 유효성 검증**
  Run: `node -e "JSON.parse(require('fs').readFileSync('/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/skills/skill-rules.json', 'utf8'))"`
  Expected: 에러 없이 정상 실행 완료

- [ ] **Step 4: 변경 사항 커밋**
  Run:
  ```bash
  git add "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/skills/skill-rules.json"
  git commit -m "chore: disable automatic triggers for frontend/backend guidelines in skill-rules.json"
  ```

---

### Task 2: 스킬 디렉토리 격리 이동 (백업)

**Files:**
- Modify: `/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/`
- Modify: `/Users/parkjuncheol/.gemini/config/skills/`

- [ ] **Step 1: 로컬 프로젝트 내 백업 디렉토리 생성**
  Run: `mkdir -p "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/.backup_skills"`
  Expected: `.backup_skills` 디렉토리 생성 완료

- [ ] **Step 2: 로컬 다이어트 대상 스킬 폴더를 백업 폴더로 이동**
  로컬 `.codex/skills/` 디렉토리 하위의 `vercel-react-best-practices`, `nextjs-frontend-guidelines`, `fastapi-backend-guidelines` 폴더를 `.backup_skills/` 폴더로 이동합니다.
  Run:
  ```bash
  mv "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/vercel-react-best-practices" "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/.backup_skills/"
  mv "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/nextjs-frontend-guidelines" "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/.backup_skills/"
  mv "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/fastapi-backend-guidelines" "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/.backup_skills/"
  ```
  Expected: 폴더 이동 완료 및 로드 경로에서 이탈

- [ ] **Step 3: 전역 내 백업 디렉토리 생성**
  Run: `mkdir -p "/Users/parkjuncheol/.gemini/config/skills/.backup_skills"`
  Expected: `.backup_skills` 디렉토리 생성 완료

- [ ] **Step 4: 전역 다이어트 대상 스킬 폴더를 백업 폴더로 이동**
  `google-antigravity-sdk`, `chrome-extensions`, `to-issues`, `to-prd`, `show-me-the-prd`, `vercel-react-best-practices`, `nextjs-frontend-guidelines`, `fastapi-backend-guidelines`, `test-driven-development` 폴더를 전역 `.backup_skills/` 폴더로 이동합니다.
  Run:
  ```bash
  mv "/Users/parkjuncheol/.gemini/config/skills/google-antigravity-sdk" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/chrome-extensions" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/to-issues" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/to-prd" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/show-me-the-prd" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/vercel-react-best-practices" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/nextjs-frontend-guidelines" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/fastapi-backend-guidelines" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  mv "/Users/parkjuncheol/.gemini/config/skills/test-driven-development" "/Users/parkjuncheol/.gemini/config/skills/.backup_skills/"
  ```
  Expected: 9개 스킬 폴더 백업 이동 완료

- [ ] **Step 5: 변경 사항 Git 커밋**
  Run:
  ```bash
  git add "/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills/.backup_skills"
  git commit -m "chore: backup and disable target frontend/backend skills in project codex"
  ```

---

### Task 3: 특정 프로젝트 로컬 MCP 설정 파일 생성

**Files:**
- Create: `/Users/parkjuncheol/Local Sites/naver-blog-harness/posts/vet-branding-strategy/mcp_config.json`

- [ ] **Step 1: 로컬 프로젝트 타겟 디렉토리 생성 검증**
  Run: `mkdir -p "/Users/parkjuncheol/Local Sites/naver-blog-harness/posts/vet-branding-strategy"`
  Expected: 디렉토리 확인 또는 생성 완료

- [ ] **Step 2: `mcp_config.json` 로컬 파일 작성**
  아래 내용으로 `/Users/parkjuncheol/Local Sites/naver-blog-harness/posts/vet-branding-strategy/mcp_config.json` 파일을 작성합니다.
  ```json
  {
    "mcpServers": {
      "korean-law": {
        "command": "npx",
        "args": ["-y", "mcp-remote", "https://korean-law-mcp.fly.dev/mcp"]
      },
      "korean-stats": {
        "command": "npx",
        "args": ["-y", "mcp-remote", "https://korean-stats-mcp.fly.dev/mcp"]
      }
    }
  }
  ```
  Expected: 파일 생성 완료

- [ ] **Step 3: JSON 파일 구문 유효성 검증**
  Run: `node -e "JSON.parse(require('fs').readFileSync('/Users/parkjuncheol/Local Sites/naver-blog-harness/posts/vet-branding-strategy/mcp_config.json', 'utf8'))"`
  Expected: 에러 없이 정상 작동 완료
