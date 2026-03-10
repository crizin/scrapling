# Scrapling API

Scrapling 라이브러리를 래핑한 Docker 기반 웹 스크래핑 REST API 서비스.

## 프로젝트 구조

- `app/main.py` — FastAPI 앱 진입점. 미들웨어(인증, 동시성, 타임아웃), 헬스체크, 라우터 등록
- `app/config.py` — pydantic-settings 기반 환경변수 설정 (`API_` prefix)
- `app/routers/` — fetch(정적HTTP), dynamic(Playwright), stealth(Camoufox) 엔드포인트
- `app/schemas/` — Pydantic 요청/응답 모델
- `app/services/scraper.py` — Scrapling fetcher 래퍼 + CSS/XPath/Regex 추출 로직

## Scrapling 라이브러리 API 참고

- `AsyncFetcher` — 클래스 메서드 `.get()`, `.post()`, `.put()`, `.delete()` (인스턴스 생성 없음)
- `DynamicFetcher.async_fetch(url, **kwargs)` — Playwright 기반 클래스 메서드
- `StealthyFetcher.async_fetch(url, **kwargs)` — Camoufox 기반 클래스 메서드
- Response 객체는 Selector를 상속하므로 `.css()`, `.xpath()` 직접 호출 가능
- HTML 원문은 `response.body.decode(response.encoding)`으로 획득

## 개발 명령어

```bash
# Docker 빌드 및 실행
docker compose up --build

# 헬스체크
curl http://localhost:8000/health

# 정적 스크래핑 테스트
curl -X POST http://localhost:8000/fetch -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "extract": {"css": ["h1::text"]}}'
```

## 주의사항

- `page_action`, `init_script`는 보안상 의도적으로 제외
- `adaptive`, `auto_save`, Session 클래스는 stateless API 특성상 제외
- 브라우저 엔드포인트(`/dynamic`, `/stealth`)는 `asyncio.Semaphore`로 동시성 제한 (기본 10)
