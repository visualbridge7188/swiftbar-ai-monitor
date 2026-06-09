# 🚀 SwiftBar AI Status Monitor (한국어)

[English](README.md) | [한국어](README_KR.md)

---

**SwiftBar AI Status Monitor**는 [SwiftBar](https://github.com/swiftbar/SwiftBar)를 위한 macOS 메뉴바 플러그인으로, **Codex**, **Antigravity**, **Z AI**의 실시간 토큰 사용량, 할당 한도 및 리셋 시간을 모니터링합니다.

---

## 🔍 핵심 기능

1. **🎨 고해상도 그래픽 진행 바 (Pillow)**
   * 아스키 텍스트 대신 Pillow(PIL) 라이브러리를 사용해 메모리(RAM) 상에서 직접 고해상도 게이지 이미지를 동적으로 렌더링합니다.
   * 다크 모드와 라이트 모드 모두에 어울리도록 투명 트랙과 대비 디자인이 가미되어 메뉴바 드롭다운에 고급스럽게 매칭됩니다.

2. **⏱️ 7일 토큰 사용량 페이싱 (Pacing & 적정 사용선)**
   * 7일 속도 제한 창의 남은 시간과 비교하여 현재 토큰 사용 속도가 적정한지 자동으로 계산합니다.
   * 그래프에 권장 적정 사용량 지점을 세로선으로 표시하며, 속도가 너무 빠르면 마커가 **빨간색(Red)**, 안정적이면 **초록색(Green)**으로 변경됩니다.

3. **🤖 Antigravity 로컬 언어 서버 자동 탐색 (Local Probe)**
   * 맥에서 실행 중인 Antigravity 프로세스(`ps`) 및 청취 포트(`lsof`)를 탐색하여 보안 토큰(`--csrf_token`)을 자동 추출합니다.
   * 로컬 루프백 API 통신을 통해 **Claude**, **Gemini Pro**, **Gemini Flash** 모델의 잔여 할당량을 완벽히 개별 추적합니다 (자동완성, 라이트, 이미지 전용 모델은 자동 필터링).
   * 로컬 서버가 작동하지 않는 경우 CLI 명령어(`antigravity-usage`)나 가상 데이터(Mock)로 안전하게 자동 폴백(Fallback) 처리됩니다.

4. **⚡ Z AI 듀얼 한도 추적**
   * 한 번에 MCP 호출 횟수 한도(`TIME_LIMIT`)와 모델 토큰 한도(`TOKENS_LIMIT`)를 동시에 모니터링합니다.

---

## 📂 프로젝트 구조

```text
├── README.md               # 메인 영문 문서
├── README_KR.md            # 국문 번역 문서
├── ai_status.5m.py         # SwiftBar 플러그인 파이썬 스크립트 (5분 간격 실행)
├── .config.json            # Z AI API 키 보관용 숨김 설정 파일
├── docs/                   # 플러그인 상세 스펙 및 문서
└── tests/                  # 단위 테스트 코드 모음
```

---

## ⚙️ 설치 및 설정 방법

### 1. 요구사항
* **macOS** 및 [SwiftBar](https://github.com/swiftbar/SwiftBar) 설치 환경
* **Python 3** (Homebrew python 권장) 및 **Pillow** 패키지 설치
  ```bash
  pip3 install pillow
  ```

### 2. 설치 단계
1. [ai_status.5m.py](ai_status.5m.py) 스크립트 파일을 SwiftBar 플러그인 폴더에 복사합니다.
2. 스크립트 파일에 실행 권한을 부여합니다:
   ```bash
   chmod +x ai_status.5m.py
   ```
3. 플러그인과 동일한 경로에 `.config.json` 파일을 생성하여 본인의 Z AI API 키를 등록합니다:
   ```json
   {
       "Z_AI_API_KEY": "your-z-ai-api-key"
   }
   ```
4. SwiftBar 메뉴바에서 새로고침을 실행하거나 터미널에서 아래 명령을 실행합니다:
   ```bash
   open -g "swiftbar://refreshAll"
   ```

---

## 🧪 테스트 실행

아래 명령어로 스크립트 동작 및 가상 데이터 매핑 관련 전체 단위 테스트를 수행하여 무결성을 검증할 수 있습니다:

```bash
python3 -m unittest discover -s tests -v
```

성공 시 출력 예시:
```text
test_get_antigravity_cli_fallback (test_cli_fetch.TestCliFetch) ... ok
test_get_antigravity_local_success (test_cli_fetch.TestCliFetch) ... ok
test_get_codex (test_cli_fetch.TestCliFetch) ... ok
test_config_generation (test_config.TestConfig) ... ok
test_get_zai (test_http_fetch.TestHttpFetch) ... ok
test_render_output (test_ui_render.TestUIRender) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.012s

OK
```

---

## 📄 라이센스

본 프로젝트는 MIT 라이센스에 따라 수정 및 재배포가 자유롭습니다.
