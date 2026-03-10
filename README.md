# Scrapling API

[Scrapling](https://github.com/D4Vinci/Scrapling) 라이브러리 기반의 Docker 웹 스크래핑 REST API 서비스.

HTTP 요청 하나로 정적/동적/스텔스 웹 스크래핑과 서버사이드 콘텐츠 추출(CSS, XPath, Regex)을 수행합니다.

## 빠른 시작

```bash
docker compose up --build -d
curl http://localhost:8000/health
```

## API 엔드포인트

### GET `/health`

헬스체크.

```json
{"status": "ok"}
```

### POST `/fetch` — 정적 HTTP 스크래핑

JS 렌더링이 불필요한 페이지용. 가장 빠름.

```bash
curl -X POST http://localhost:8000/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "extract": {
      "css": ["h1::text", "a::attr(href)"],
      "xpath": ["//title/text()"],
      "return_html": true
    }
  }'
```

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `url` | string | *필수* | 스크래핑 대상 URL |
| `method` | string | `GET` | HTTP 메서드 (GET/POST/PUT/DELETE) |
| `headers` | object | — | 요청 헤더 |
| `cookies` | object | — | 쿠키 |
| `proxy` | string | — | 프록시 URL |
| `timeout` | integer | `30` | 타임아웃 (초, 최대 120) |
| `impersonate` | string | — | TLS 핑거프린트 (예: `chrome`) |
| `follow_redirects` | boolean | `true` | 리다이렉트 추적 |
| `params` | object | — | 쿼리 파라미터 |
| `body` | object | — | POST 요청 본문 |
| `json_body` | object | — | JSON POST 요청 본문 |
| `extract` | object | — | 콘텐츠 추출 설정 |

### POST `/dynamic` — 동적 페이지 스크래핑

Playwright Chromium 기반. JS 렌더링이 필요한 SPA 페이지용.

```bash
curl -X POST http://localhost:8000/dynamic \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "headless": true,
    "network_idle": true,
    "extract": {"css": ["h1::text"]}
  }'
```

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `url` | string | *필수* | 스크래핑 대상 URL |
| `headless` | boolean | `true` | 헤드리스 모드 |
| `disable_resources` | boolean | `false` | 이미지/CSS 로딩 차단 |
| `network_idle` | boolean | `true` | 네트워크 유휴 대기 |
| `timeout` | integer | `30` | 타임아웃 (초, 최대 120) |
| `wait_selector` | string | — | 특정 요소 대기 (CSS 셀렉터) |
| `wait_selector_state` | string | `attached` | 대기 상태 (attached/visible) |
| `cookies` | object | — | 쿠키 |
| `proxy` | string | — | 프록시 URL |
| `extract` | object | — | 콘텐츠 추출 설정 |

### POST `/stealth` — 안티봇 우회 스크래핑

Camoufox(수정된 Firefox) 기반. Cloudflare 등 봇 방어 우회용.

```bash
curl -X POST http://localhost:8000/stealth \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "headless": true,
    "solve_cloudflare": true,
    "extract": {"css": ["h1::text"]}
  }'
```

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `url` | string | *필수* | 스크래핑 대상 URL |
| `headless` | boolean | `true` | 헤드리스 모드 |
| `timeout` | integer | `60` | 타임아웃 (초, 최대 180) |
| `wait_selector` | string | — | 특정 요소 대기 |
| `wait_selector_state` | string | `attached` | 대기 상태 |
| `cookies` | object | — | 쿠키 |
| `proxy` | string | — | 프록시 URL |
| `solve_cloudflare` | boolean | `false` | Cloudflare 챌린지 자동 해결 |
| `humanize` | boolean | `false` | 사람 같은 커서 이동 |
| `block_webrtc` | boolean | `false` | WebRTC 차단 |
| `allow_webgl` | boolean | `false` | WebGL 허용 |
| `disable_ads` | boolean | `false` | 광고 차단 |
| `os_randomize` | boolean | `false` | OS 핑거프린트 랜덤화 |
| `geoip` | boolean | `false` | 지역 위치 스푸핑 |
| `disable_resources` | boolean | `false` | 리소스 로딩 차단 |
| `network_idle` | boolean | `false` | 네트워크 유휴 대기 |
| `extract` | object | — | 콘텐츠 추출 설정 |

### 콘텐츠 추출 (`extract`)

모든 엔드포인트에서 `extract` 필드를 지정하면 서버에서 데이터를 추출하여 반환합니다.

```json
{
  "extract": {
    "css": ["h1::text", "a::attr(href)", ".content"],
    "xpath": ["//title/text()"],
    "regex": ["\\d{4}-\\d{2}-\\d{2}"],
    "return_html": true
  }
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `css` | string[] | CSS 셀렉터 목록 |
| `xpath` | string[] | XPath 표현식 목록 |
| `regex` | string[] | 정규식 패턴 목록 |
| `return_html` | boolean | 전체 HTML도 함께 반환할지 여부 |

> `extract`를 지정하지 않으면 전체 HTML이 `html` 필드에 반환됩니다.

### 응답 형식

```json
{
  "status": 200,
  "reason": "OK",
  "url": "https://example.com/final",
  "headers": {"content-type": "text/html"},
  "cookies": {},
  "html": "<html>...</html>",
  "extracted": {
    "css": {"h1::text": ["제목"]},
    "xpath": {"//title/text()": ["페이지 제목"]},
    "regex": {"\\d{4}-\\d{2}-\\d{2}": ["2024-01-01"]}
  },
  "elapsed_ms": 1234
}
```

## 환경 변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `API_KEY` | *(없음)* | 설정 시 `X-API-Key` 헤더 인증 활성화 |
| `API_TIMEOUT_MAX` | `120` | fetch/dynamic 최대 타임아웃 (초) |
| `API_STEALTH_TIMEOUT_MAX` | `180` | stealth 최대 타임아웃 (초) |
| `API_MAX_CONCURRENT` | `10` | 동시 브라우저 요청 수 제한 |

### API 키 인증

`API_KEY` 환경 변수를 설정하면 모든 요청에 `X-API-Key` 헤더가 필요합니다.

```bash
# docker-compose.yml에서 설정
environment:
  - API_KEY=your-secret-key

# 요청 시
curl -X POST http://localhost:8000/fetch \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 에러 코드

| 코드 | 상황 |
|---|---|
| 401 | API 키 인증 실패 |
| 422 | 잘못된 요청 파라미터 |
| 429 | 동시 브라우저 요청 수 초과 |
| 502 | 대상 서버 연결 실패 |
| 504 | 요청 타임아웃 |

## 라이선스

MIT
