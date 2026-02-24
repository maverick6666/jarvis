# JARVIS - 시스템 아키텍처 설계

## 1. 전체 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Web App  │  │ Mobile   │  │ Desktop  │  │  Voice   │    │
│  │ (React)   │  │  (RN)    │  │(Electron)│  │(Whisper) │    │
│  └─────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│        └──────────────┴─────────────┴─────────────┘          │
│                           │ REST / WebSocket                 │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                      API Gateway                              │
│              (인증, 레이트리밋, 라우팅)                        │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                     Core Services                             │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Input      │  │  Cluster    │  │  Search     │          │
│  │   Engine     │  │  Engine     │  │  Engine     │          │
│  │             │  │             │  │             │          │
│  │ - 토픽추출   │  │ - 자동분류   │  │ - 시맨틱    │          │
│  │ - 정규화     │  │ - 계층관리   │  │ - 키워드    │          │
│  │ - 분리       │  │ - 세분화     │  │ - 회상형    │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                   │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐          │
│  │ Enrichment  │  │  Opinion    │  │  Learning   │          │
│  │ Engine      │  │  Engine     │  │  Engine     │          │
│  │             │  │             │  │             │          │
│  │ - 웹검색    │  │ - 구체화     │  │ - 취향학습  │          │
│  │ - API연동   │  │ - 피드백     │  │ - 프로필    │          │
│  │ - 정보수집  │  │ - 레벨조절   │  │ - 추천      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                               │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                     Data Layer                                │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ PostgreSQL  │  │  Vector DB  │  │   Redis     │          │
│  │             │  │ (Qdrant/    │  │             │          │
│  │ - Entries   │  │  Pinecone)  │  │ - Cache     │          │
│  │ - Clusters  │  │             │  │ - Session   │          │
│  │ - Users     │  │ - Embeddings│  │ - Rate Limit│          │
│  │ - Topics    │  │ - Search    │  │             │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                  External Services                            │
│                                                               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│  │OpenAI│ │Claude│ │TMDB  │ │Naver │ │Google│              │
│  │ API  │ │ API  │ │ API  │ │ API  │ │Search│              │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 기술 스택 (권장)

### Backend
| 구성 요소 | 기술 | 선택 이유 |
|----------|------|----------|
| 언어 | Python 3.12+ | AI/ML 생태계, LangChain 호환 |
| 프레임워크 | FastAPI | 비동기 지원, 자동 API 문서, 타입 힌트 |
| ORM | SQLAlchemy 2.0 | 비동기 지원, 타입 안전 |
| 태스크 큐 | Celery + Redis | 웹 검색/임베딩 생성 비동기 처리 |
| AI 오케스트레이션 | LangChain / LangGraph | 복잡한 AI 파이프라인 관리 |

### Database
| 구성 요소 | 기술 | 선택 이유 |
|----------|------|----------|
| 메인 DB | PostgreSQL 16 | JSONB 지원, 확장성, pgvector 가능 |
| 벡터 DB | Qdrant (셀프호스팅) 또는 Pinecone (클라우드) | 시맨틱 검색 특화 |
| 캐시 | Redis | 세션, 캐시, 큐 |
| 검색 보조 | Elasticsearch (선택) | 풀텍스트 검색 보조 |

### Frontend
| 구성 요소 | 기술 | 선택 이유 |
|----------|------|----------|
| 프레임워크 | Next.js 15 (App Router) | SSR, 라우팅, React 생태계 |
| 언어 | TypeScript | 타입 안전 |
| 상태관리 | Zustand | 경량, 직관적 |
| UI | Tailwind CSS + shadcn/ui | 빠른 개발, 일관된 디자인 |
| 에디터 | Tiptap 또는 Slate | 리치 텍스트 문서 표시 |

### AI / ML
| 구성 요소 | 기술 | 선택 이유 |
|----------|------|----------|
| LLM | Claude API (주) / GPT-4 (보조) | 토픽 추출, 감상 구체화 |
| 임베딩 | OpenAI text-embedding-3-large | 고품질 임베딩 |
| 음성 (Phase 2) | Whisper API | 음성 입력 지원 |
| 이미지 (Phase 2) | Claude Vision / GPT-4V | 스크린샷 분석 |

### 인프라
| 구성 요소 | 기술 | 선택 이유 |
|----------|------|----------|
| 컨테이너 | Docker + Docker Compose | 로컬 개발 환경 통일 |
| 배포 | Railway 또는 AWS (ECS) | 초기 간편 배포 → 확장 |
| CI/CD | GitHub Actions | 자동 테스트 + 배포 |
| 모니터링 | Sentry + Prometheus | 에러 추적 + 메트릭 |

---

## 3. API 설계

### 3.1 핵심 엔드포인트

```
# 입력
POST   /api/v1/entries              # 새 기록 입력
GET    /api/v1/entries              # 기록 목록 조회
GET    /api/v1/entries/:id          # 기록 상세 조회
PATCH  /api/v1/entries/:id          # 기록 수정
DELETE /api/v1/entries/:id          # 기록 삭제

# 클러스터
GET    /api/v1/clusters             # 클러스터 트리 조회
GET    /api/v1/clusters/:id         # 클러스터 상세 + 소속 기록
PATCH  /api/v1/clusters/:id         # 클러스터 이름/구조 수정
POST   /api/v1/clusters/merge       # 클러스터 병합
POST   /api/v1/clusters/split       # 클러스터 분리

# 검색
POST   /api/v1/search               # 통합 검색 (시맨틱 + 키워드)
GET    /api/v1/search/suggest        # 검색 자동완성

# 감상평
PATCH  /api/v1/entries/:id/opinion   # 감상평 수정
POST   /api/v1/entries/:id/confirm   # AI 구체화 확인/거부

# 타임라인
GET    /api/v1/timeline              # 타임라인 뷰

# 사용자
GET    /api/v1/profile               # 취향 프로필 조회
GET    /api/v1/stats                 # 통계 대시보드
```

### 3.2 입력 API 상세

```json
// POST /api/v1/entries
// Request
{
  "raw_input": "레전드라는 영화봄 톰하디 개멋있음 그리고 저녁에 을지로 크로플 먹음",
  "context": {
    "timestamp": "2026-02-24T18:30:00+09:00",
    "location": null,
    "source": "web"
  }
}

// Response (처리 시작)
{
  "status": "processing",
  "job_id": "job_abc123",
  "estimated_topics": 2
}

// WebSocket 이벤트 (처리 완료)
{
  "event": "entry_processed",
  "job_id": "job_abc123",
  "entries": [
    {
      "id": "entry_001",
      "type": "MOVIE",
      "title": "레전드 (2015)",
      "cluster": { "id": "cls_01", "path": "엔터테인먼트 > 영화 > 느와르" },
      "enriched_data": {
        "director": "브라이언 헬겔랜드",
        "cast": ["톰 하디"],
        "genre": ["범죄", "드라마"],
        "plot": "1960년대 런던을 지배한...",
        "poster_url": "https://...",
        "rating": { "imdb": 6.9 }
      },
      "opinion": {
        "raw": "톰하디 개멋있음",
        "expanded": "톰 하디의 슈트핏과 1인 2역 연기가 인상적이었다.",
        "confirmed": null
      },
      "tags": ["느와르", "톰하디", "슈트핏", "범죄영화", "실화"]
    },
    {
      "id": "entry_002",
      "type": "FOOD",
      "title": "을지로 크로플",
      "cluster": { "id": "cls_02", "path": "라이프 > 맛집" },
      "enriched_data": {
        "area": "을지로",
        "food_type": "크로플",
        "search_results": [...]
      },
      "opinion": {
        "raw": "먹음",
        "expanded": null,
        "confirmed": null
      },
      "tags": ["을지로", "크로플", "카페"]
    }
  ]
}
```

### 3.3 검색 API 상세

```json
// POST /api/v1/search
// Request
{
  "query": "슈트핏 멋있는 느와르 영화",
  "filters": {
    "type": null,
    "date_range": null,
    "cluster_id": null
  },
  "limit": 10
}

// Response
{
  "results": [
    {
      "entry": { "id": "entry_001", "title": "레전드 (2015)", ... },
      "relevance_score": 0.95,
      "match_reasons": ["시맨틱: 느와르+슈트핏", "태그: 느와르, 슈트핏"],
      "narrative": "2026년 2월 24일에 영화 '레전드'를 보셨습니다. '톰하디 개멋있음'이라고 하셨고, 슈트핏과 느와르 분위기가 인상적이셨던 것 같아요."
    }
  ],
  "suggestions": [
    { "title": "대부 (1972)", "reason": "비슷한 장르" },
    { "title": "굿펠라즈 (1990)", "reason": "비슷한 장르" }
  ]
}
```

---

## 4. 데이터베이스 스키마

### 4.1 PostgreSQL

```sql
-- 사용자
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 클러스터
CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    parent_id UUID REFERENCES clusters(id),
    depth INTEGER DEFAULT 0,
    auto_generated BOOLEAN DEFAULT true,
    description TEXT,
    entry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 기록 (Entry)
CREATE TABLE entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    cluster_id UUID REFERENCES clusters(id),

    -- 원본
    raw_input TEXT NOT NULL,
    entry_type VARCHAR(50) NOT NULL,  -- MOVIE, FOOD, BOOK, TECH, etc.
    title VARCHAR(500),

    -- 보강 정보
    enriched_data JSONB DEFAULT '{}',

    -- 감상
    opinion_raw TEXT,
    opinion_expanded TEXT,
    opinion_confirmed BOOLEAN,

    -- 태그
    tags TEXT[] DEFAULT '{}',

    -- 메타
    source VARCHAR(50) DEFAULT 'web',
    event_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 토픽
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID REFERENCES entries(id),
    name VARCHAR(200) NOT NULL,
    topic_type VARCHAR(50),  -- PERSON, WORK, PLACE, CONCEPT, EMOTION
    confidence FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}'
);

-- 토픽 관계
CREATE TABLE topic_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_a_id UUID REFERENCES topics(id),
    topic_b_id UUID REFERENCES topics(id),
    relation_type VARCHAR(50),  -- RELATED, PART_OF, SIMILAR
    strength FLOAT DEFAULT 0.0
);

-- 사용자 피드백
CREATE TABLE opinion_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID REFERENCES entries(id),
    feedback_type VARCHAR(20),  -- CONFIRM, REJECT, EDIT
    edited_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_entries_user ON entries(user_id);
CREATE INDEX idx_entries_cluster ON entries(cluster_id);
CREATE INDEX idx_entries_type ON entries(entry_type);
CREATE INDEX idx_entries_tags ON entries USING GIN(tags);
CREATE INDEX idx_entries_created ON entries(created_at DESC);
CREATE INDEX idx_clusters_parent ON clusters(parent_id);
CREATE INDEX idx_topics_entry ON topics(entry_id);
```

---

## 5. 프로젝트 디렉토리 구조 (권장)

```
jarvis/
├── docs/                          # 문서
│   ├── PLANNING.md                # 기획서
│   ├── FEATURE_SPEC.md            # 기능 스펙
│   └── ARCHITECTURE.md            # 아키텍처 (이 문서)
│
├── backend/                       # Python Backend
│   ├── app/
│   │   ├── main.py                # FastAPI 앱 엔트리포인트
│   │   ├── config.py              # 설정
│   │   │
│   │   ├── api/                   # API 라우터
│   │   │   ├── entries.py
│   │   │   ├── clusters.py
│   │   │   ├── search.py
│   │   │   └── timeline.py
│   │   │
│   │   ├── engines/               # 핵심 엔진
│   │   │   ├── input_engine.py    # 토픽 추출, 텍스트 파싱
│   │   │   ├── cluster_engine.py  # 클러스터링
│   │   │   ├── enrichment_engine.py  # 웹 검색 보강
│   │   │   ├── opinion_engine.py  # 감상평 구체화
│   │   │   ├── search_engine.py   # 시맨틱 검색
│   │   │   └── learning_engine.py # 사용자 학습
│   │   │
│   │   ├── models/                # DB 모델
│   │   │   ├── entry.py
│   │   │   ├── cluster.py
│   │   │   ├── topic.py
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/               # Pydantic 스키마
│   │   │   ├── entry.py
│   │   │   ├── cluster.py
│   │   │   └── search.py
│   │   │
│   │   └── services/              # 외부 서비스 연동
│   │       ├── llm_service.py     # LLM API
│   │       ├── embedding_service.py  # 임베딩 생성
│   │       ├── web_search.py      # 웹 검색
│   │       └── tmdb_service.py    # TMDB API
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                      # Next.js Frontend
│   ├── src/
│   │   ├── app/                   # App Router 페이지
│   │   │   ├── page.tsx           # 메인 입력 화면
│   │   │   ├── search/
│   │   │   ├── timeline/
│   │   │   └── clusters/
│   │   │
│   │   ├── components/            # React 컴포넌트
│   │   │   ├── InputArea.tsx      # 메인 입력 영역
│   │   │   ├── TopicCard.tsx      # 토픽 카드
│   │   │   ├── ClusterTree.tsx    # 클러스터 트리
│   │   │   ├── SearchBar.tsx      # 검색
│   │   │   ├── Timeline.tsx       # 타임라인
│   │   │   └── OpinionFeedback.tsx # 감상평 피드백
│   │   │
│   │   ├── hooks/                 # Custom Hooks
│   │   ├── stores/                # Zustand Stores
│   │   └── lib/                   # 유틸리티
│   │
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml             # 로컬 개발 환경
├── .env.example                   # 환경변수 예시
└── README.md
```

---

## 6. MVP 개발 로드맵

### Sprint 1 (1-2주): 기반 구축
- [ ] 프로젝트 초기 설정 (Docker, DB, FastAPI, Next.js)
- [ ] DB 스키마 생성 & 마이그레이션
- [ ] 기본 CRUD API
- [ ] 기본 웹 UI (입력 화면)

### Sprint 2 (2-3주): 입력 엔진
- [ ] LLM 기반 토픽 추출
- [ ] 복합 토픽 분리
- [ ] 기본 클러스터링 (수동 매칭)
- [ ] 입력 → 처리 → 결과 표시 플로우

### Sprint 3 (2-3주): 보강 & 구체화
- [ ] 웹 검색 연동 (영화, 맛집)
- [ ] 정보 보강 파이프라인
- [ ] AI 감상평 구체화
- [ ] 피드백 루프 (맞아/아니야/수정)

### Sprint 4 (2-3주): 검색 & 시맨틱
- [ ] 임베딩 생성 & 벡터 DB 연동
- [ ] 시맨틱 검색 구현
- [ ] 회상형 검색 & 내러티브 생성
- [ ] 검색 UI

### Sprint 5 (1-2주): 마무리
- [ ] 타임라인 뷰
- [ ] 클러스터 시각화
- [ ] 자동 클러스터 세분화
- [ ] 버그 수정 & 최적화
