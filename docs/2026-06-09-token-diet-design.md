# 📋 디자인 스펙: 토큰 누수 차단을 위한 스킬 다이어트 및 MCP 로컬 격리

* **작성일**: 2026-06-09
* **상태**: 승인 완료 (User Approved)
* **목표**: 에이전트 구동 시 불필요한 시스템 프롬프트(스킬)와 전역 MCP 도구 명세 주입을 방지하여 매 대화마다 발생하는 토큰 소모량을 대폭 절감하고 효율성을 개선합니다.

---

## 1. 스킬 다이어트 및 비활성화

불필요하거나 현재 사용하지 않는 스킬을 에이전트 활성화 규칙에서 완전 제외하고 백업 격리합니다.

### 1) 프로젝트 로컬 트리거 비활성화
* **파일**: [skill-rules.json](file:///Users/parkjuncheol/Local%20Sites/AI%20Agent/hugh.kim/skills/skill-rules.json)
* **작업**: `nextjs-frontend-guidelines`, `vercel-react-best-practices`, `fastapi-backend-guidelines` 스킬에 해당하는 JSON 설정 블록을 영구 제거하여 컨텍스트 자동 주입을 차단합니다.

### 2) 스킬 디렉토리 격리 (백업)
* **대상 스킬**:
  1. `google-antigravity-sdk`
  2. `chrome-extensions`
  3. `to-issues`
  4. `to-prd`
  5. `show-me-the-prd`
  6. `vercel-react-best-practices`
  7. `nextjs-frontend-guidelines`
  8. `fastapi-backend-guidelines`
  9. `test-driven-development`
* **백업 위치**: 
  * 프로젝트 로컬: `/Users/parkjuncheol/Local Sites/AI Agent/hugh.kim/.codex/skills` 하위에 `.backup_skills/` 폴더를 생성하고 해당 스킬 디렉토리를 이 폴더로 이동합니다.
  * 전역 스킬: `/Users/parkjuncheol/.gemini/config/skills/` 하위에 동일한 백업 폴더를 구성하여 이동합니다.

---

## 2. MCP 다이어트 및 로컬 격리

전역에 로드된 MCP 서버 중 `stitch`는 완전히 비활성화하며, `korean-law` 및 `korean-stats`는 전역 로드 대상에서 제외하고 필요한 로컬 프로젝트 하위에 격리 구성합니다.

### 1) 특정 프로젝트 로컬 격리
* **대상 프로젝트 경로**: `/Users/parkjuncheol/Local Sites/naver-blog-harness/posts/vet-branding-strategy`
* **생성 파일**: `mcp_config.json`
* **내용**:
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

### 2) 전역 비활성화 가이드
* **동작**: 유저에게 Codex 및 Gemini 앱 전역 설정에서 `stitch`, `korean-law`, `korean-stats`를 삭제하도록 안내를 제공합니다.
