# Cloud-Utils 프로젝트 개발 요구사항 및 계획

## 1. 프로젝트 개요
- **프로젝트명**: cloud-utils
- **목적**: 클라우드 서비스들을 Python에서 쉽게 사용할 수 있는 유틸리티 모듈 개발
- **현재 지원**: AWS (향후 다른 클라우드 제공자 확장 예정)
- **개발 언어**: Python 3.12

## 2. 지원하는 AWS 서비스
### 2.1 SQS (Simple Queue Service)
- **Sync 모듈**: 기본적인 큐 조작 (생성, 삭제, 메시지 송수신 등)
- **Async 모듈**: 비동기 큐 조작

### 2.2 OSS (OpenSearch Service)
- **Sync 모듈만**: 인덱스 관리, 문서 CRUD, 검색 등
- **라이브러리**: opensearch-py 사용

### 2.3 DynamoDB
- **Sync 모듈만**: 테이블 관리, 아이템 CRUD, 쿼리 등
- **라이브러리**: boto3 + boto3.dynamodb 사용

### 2.4 S3
- **Sync 모듈**: 버킷/객체 관리, 업로드/다운로드 등
- **Async 모듈**: 비동기 S3 작업

## 3. 기술 스택
- **기본 라이브러리**: boto3
- **OpenSearch**: opensearch-py
- **패키징**: hatching + uv
- **비동기**: asyncio + aioboto3 (SQS, S3용)

## 4. 프로젝트 구조
```
cloud-utils/
├── cloud_utils/
│   ├── aws/
│   │   ├── sqs/
│   │   │   ├── sync.py
│   │   │   └── async.py
│   │   ├── oss/
│   │   │   └── sync.py
│   │   ├── dynamodb/
│   │   │   └── sync.py
│   │   └── s3/
│   │       ├── sync.py
│   │       └── async.py
│   └── __init__.py
├── docs/
├── todo/
├── tests/
├── pyproject.toml
└── README.md
```

## 5. 개발 우선순위
1. **1단계**: 기본 Sync 모듈들 개발 (SQS, OSS, DynamoDB, S3)
2. **2단계**: Async 모듈들 개발 (SQS, S3)
3. **3단계**: 테스트 코드 작성
4. **4단계**: 문서화 및 예제 코드 작성

## 6. 각 모듈 기본 기능
### 6.1 SQS
- 큐 생성/삭제
- 메시지 송신/수신
- 큐 속성 조회/수정

### 6.2 OSS
- 인덱스 생성/삭제
- 문서 추가/수정/삭제
- 검색 쿼리 실행

### 6.3 DynamoDB
- 테이블 생성/삭제
- 아이템 CRUD
- 쿼리 및 스캔

### 6.4 S3
- 버킷 생성/삭제
- 객체 업로드/다운로드
- 객체 메타데이터 관리
