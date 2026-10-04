# AI 코딩 지침 파일 엔지니어링

AI 코딩 도구를 위한 지침 파일을 어떻게 설계하고, 범위를 나누고, 검증하고, 유지보수할지를 다루는 책이다.

대상은 다음과 같은 저장소 지침이다.

- CLAUDE.md
- AGENTS.md
- GEMINI.md
- Cursor Rules
- GitHub Copilot custom instructions
- SKILL.md / Agent Skills
- Hooks
- instruction validator와 eval

이 프로젝트의 목표는 에이전트를 구현하는 것이 아니다.

> **사람이 작성하는 지침 파일을 소프트웨어 엔지니어링 대상으로 다루는 실전 가이드**를 만드는 것이 목표다.

## 책 읽기

완성 원고의 시작점:

[book/README.md](book/README.md)

현재 원고는 19장과 5개 부록으로 구성되어 있다.

### Part 1. 지침 파일은 왜 별도 엔지니어링 대상인가

- 프롬프트에서 저장소 지침으로
- 컨텍스트는 공짜가 아니다

### Part 2. 어디에 무엇을 써야 하는가

- CLAUDE.md
- AGENTS.md와 portability
- Path-scoped Rules

### Part 3. SKILL.md를 쓰는 법

- Skill 구조와 공개 표준
- description과 routing
- 실행 가능한 Skill 본문
- References와 Scripts

### Part 4. 자연어로 쓰지 말아야 할 규칙

- Hook, lint, CI, type으로 승격
- Claude Code Hooks

### Part 5. 실제 사례 해부

- pstack 사례
- 나쁜 지침 파일 리팩터링

### Part 6. 지침 파일도 테스트한다

- Trigger Eval
- Output Eval
- A/B와 Blinded Eval

### Part 7. 유지보수

- Skill Smell과 Instruction Debt
- 모델 업그레이드 감사
- 지침 파일 리뷰 프로세스

## 리서치

책의 근거층은 [research/instruction-files](research/instruction-files/)에 유지한다.

현재 리서치는 다음 영역을 포함한다.

- 제품 공식 문서와 공개 규격
- Claude, Codex, Cursor, Gemini, Copilot 비교
- pstack 실제 Skill/Rule 분석
- 공개 instruction corpus
- 최근 유명 Skill 저장소 규칙 패턴
- 운영형 Skill의 state, permission, handoff 패턴
- Trigger Eval / Scope Eval 프로토콜
- structural validator 설계
- bad → good 리팩터링 사례
- instruction review checklist

## 핵심 원칙

새로운 실패를 발견했다고 곧바로 root instruction에 한 줄을 추가하지 않는다.

먼저 묻는다.

1. 모든 작업에 필요한가.
2. 특정 path에서만 필요한가.
3. 특정 task의 procedure인가.
4. 기계적으로 판정할 수 있는가.
5. 이미 canonical source가 있는가.
6. 실제 behavior로 검증할 수 있는가.

책 전체는 이 여섯 질문을 구체화한다.

## 기준일

제품 문법과 공개 사례 조사 기준일은 2026-09-30이다.

제품별 syntax와 loading semantics는 빠르게 바뀌므로 실제 적용 시 공식 문서를 다시 확인한다.

## 공통 독서판

[공통 디자인 2026.10.04-preview.1 발행 파일](https://github.com/dhrod5457/ai-instruction-engineering-book/releases/tag/2026.10.04-preview.1) · [독서판 제작·검증 규칙](publication/common-reading/README.md). 기존 원고와 검토 상태를 보존한 새 디자인 판입니다.
