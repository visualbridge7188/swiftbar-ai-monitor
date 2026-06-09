# 🔄 Codex Loopy Harness & Karpathy Guidelines

> **검증 우선(Verification-first) 및 안드레 카파시의 개발 원칙이 융합된 경량 에이전트 하니스 템플릿**
> *"도구는 구조보다 약하고, 구조는 검증 구조보다 약하다. 에이전트의 완료 주장을 맹신하지 말고 결과로 검증하라."*

---

## 1. 🔍 프로젝트 개요

이 프로젝트는 AI 에이전트(Claude Code / Antigravity 등)가 코딩을 수행할 때 발생할 수 있는 실수와 리소스 낭비를 방지하기 위한 **개발 운영 체제(Work OS) 템플릿**입니다. 안드레 카파시의 4대 핵심 개발 원칙과 문서 기반의 강력한 검증 게이트(Hooks)를 결합하여 안정적이고 효율적인 코드 생산을 목표로 합니다.

---

## 2. 📂 디렉토리 구조 및 핵심 설정 파일

```text
├── CLAUDE.md              # Claude Code 전용 프롬프트 및 빌드/테스트 명령 정의
├── AGENTS.md              # 카파시 개발 원칙 + 하니스 핵심 운영 검증 규칙 (시스템 룰 자동 로드)
├── settings.json          # 에이전트 권한 및 훅(Hooks) 트리거 목록 정의
├── skills/                # 자주 사용되는 자동화 기능 가이드라인 및 도구 라이브러리
├── hooks/                 # 파일 수정, 커맨드 실행 전후에 자동 실행되는 보안/포맷 검증 게이트
├── rules/                 # 코딩 표준 정의 (프론트엔드/백엔드/QA 가이드라인)
├── scripts/               # 설정 동기화(sync.sh) 및 세션 적용(apply.sh) 등의 유틸 스크립트
└── docs/                  # 하니스 설계 문서 및 프로젝트 계획/검증용 마크다운 산출물
```

### ⚙️ 핵심 설정 파일의 역할 (삭제/병합 금지)
* **`CLAUDE.md`**: IDE/에이전트가 로드될 때 가장 먼저 읽는 설정 파일입니다. 핵심 명령어 단축키와 코딩 스타일을 규정합니다.
* **`AGENTS.md`**: 에이전트의 작동 철학을 주입하는 핵심 지침서입니다. 카파시의 원칙(Surgical Changes, Simplicity First 등)과 하니스의 Fail-Closed 원칙을 포함하여 프롬프트로 강제 주입됩니다.

---

## 3. 🎯 핵심 운영 원칙

### I. 카파시 개발 원칙 (Karpathy Guidelines)
1. **Think Before Coding (생각 먼저, 코딩은 나중에)**: 확실하지 않은 사항은 임의로 가정하지 않고 질문하며, 트레이드오프를 사용자에게 먼저 제시합니다.
2. **Simplicity First (단순성 우선)**: 요구사항 이외의 speculative 코딩(확장성 대비 등)은 철저히 배제하고 최소한의 코드로 구현합니다.
3. **Surgical Changes (수술적 변경)**: 수정이 필요한 라인만 최소한으로 손대며, 주변 코드를 불필요하게 리팩토링하여 예기치 못한 버그를 유도하지 않습니다.
4. **Goal-Driven Execution (목표 지향 실행)**: 성공적인 테스트/검증 기준을 먼저 정의하고 이를 통과할 때까지 루프를 수행합니다.

### II. 하니스 Fail-Closed 규칙
* 테스트 또는 빌드가 실패하거나, 필수 검증 스크립트가 실행되지 않은 경우 작업 완료로 인정하지 않습니다.
* 파일 접근 권한 및 바운더리 검사를 통과하지 못한 작업은 강제로 차단됩니다.

---

## 4. 🚀 시작하기

### 1) 프로젝트 이식
새로운 프로젝트 워크스페이스에 이 템플릿의 내용물을 복사합니다:
```bash
cp -r /path/to/codex-loopy-harness/* /your-project-directory/
```

### 2) 훅 및 설정 반영
이식된 스크립트들과 훅이 정상적으로 동작하도록 실행 권한을 부여하고 세션에 동기화합니다:
```bash
bash scripts/sync.sh
bash scripts/apply.sh
```

---

## 🛠️ 추가 도구: SwiftBar AI Status Monitor

이 레포지토리에는 macOS 메뉴바 유틸리티인 **SwiftBar**를 통해 사용 중인 AI 개발 도구(Codex, Antigravity, Z AI)의 실시간 사용량과 남은 할당량을 모니터링할 수 있는 플러그인 스크립트가 포함되어 있습니다.

### 📌 주요 기능
1. **Pillow(PIL) 동적 이미지 그래프**: 아스키 아트 대신 고해상도의 네이티브 그래픽 진행 바를 메모리(RAM) 상에서 직접 그려 표출합니다.
2. **7일 토큰 사용량 페이싱 (Pacing)**:
   * 7일 권장 속도 대비 현재 사용량이 많은지 적은지 자동으로 판별합니다.
   * 적정 사용률 임계선을 세로 막대로 표시하며, 예산을 초과하면 마커가 **빨간색(Red)**, 정상 유지 시 **초록색(Green)**으로 자동 변경됩니다.
3. **Antigravity 로컬 언어 서버 자동 탐색**:
   * 로컬에서 실행 중인 Antigravity 프로세스(`ps`)와 청취 포트(`lsof`)를 탐색하여 보안 토큰(`--csrf_token`)을 자동 추출합니다.
   * 로컬 루프백 API 통신을 통해 **Claude, Gemini Pro, Gemini Flash** 모델의 잔여 할당량을 완벽히 개별 모니터링합니다. (서버 미작동 시 CLI 또는 가상 데이터 자동 폴백 지원)
4. **Z AI 듀얼 할당량 모니터링**:
   * API 통신을 통해 MCP 호출 횟수(`TIME_LIMIT`)와 모델 토큰 잔량(`TOKENS_LIMIT`)을 둘 다 정밀 추적합니다.

### ⚙️ 설치 및 설정 방법
1. **플러그인 파일 복사**:
   [swiftbar_plugins/ai_status.5m.py](file:///Users/parkjuncheol/Local%20Sites/AI%20Agent/hugh.kim/swiftbar_plugins/ai_status.5m.py) 파일을 본인의 SwiftBar 플러그인 디렉토리에 복사합니다.
2. **Python 인터프리터 경로 구성**:
   스크립트 첫 행의 Shebang이 Pillow 라이브러리가 설치되어 있는 Homebrew Python 경로(`#!/opt/homebrew/bin/python3` 등)를 가리키도록 설정합니다.
3. **Z AI API Key 등록**:
   플러그인과 동일한 경로에 `.config.json` 파일을 생성하여 API 키를 등록합니다:
   ```json
   {
       "Z_AI_API_KEY": "your_actual_api_key_here"
   }
   ```
4. **SwiftBar 리로드**:
   SwiftBar 앱을 실행하거나, 터미널에서 `open -g "swiftbar://refreshAll"`을 실행하여 리로드합니다.

---

## 📄 라이센스

본 템플릿은 MIT 라이센스를 따르며, 자유롭게 수정 및 배포가 가능합니다.