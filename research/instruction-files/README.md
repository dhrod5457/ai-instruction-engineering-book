# AI 코딩 도구 지침 파일 작성법 리서치

수집 기준일: 2026-09-30

## 연구 목적

이 리서치의 목표는 에이전트를 설계하거나 오케스트레이션하는 방법을 설명하는 것이 아니다.

대상은 사람이 직접 작성하고 유지하는 다음과 같은 **지침 파일**이다.

- `CLAUDE.md`
- `.claude/rules/*.md`
- `SKILL.md`
- Claude Code Hooks 설정과 Hook 스크립트
- `AGENTS.md`
- `GEMINI.md`
- Cursor `.cursor/rules/*.mdc`
- GitHub Copilot `.github/copilot-instructions.md`
- GitHub Copilot `.github/instructions/*.instructions.md`

책에서 답하려는 질문은 다음과 같다.

1. 어떤 내용을 전역 지침에 써야 하는가.
2. 어떤 내용은 경로별 Rule로 분리해야 하는가.
3. 어떤 절차는 `SKILL.md`로 만들어야 하는가.
4. 어떤 규칙은 자연어로 쓰지 말고 Hook, lint, script, type, CI로 강제해야 하는가.
5. 지침을 얼마나 구체적으로 써야 하며, 언제 과도한 지시가 되는가.
6. Skill의 `description`을 어떻게 써야 정확히 호출되고 과잉 호출되지 않는가.
7. 지침 파일의 품질을 어떻게 검증하고 회귀 테스트할 것인가.
8. Claude, Codex, Cursor, Gemini, Copilot 사이에서 무엇이 공통이고 무엇이 제품 종속적인가.
9. 모델이 발전하면 기존 지침을 어떻게 다시 감사해야 하는가.

## 현재까지의 핵심 결론

### 1. 지침 파일의 첫 번째 설계 대상은 문장이 아니라 범위다

같은 문장이라도 항상 로드되는 파일에 둘지, 특정 경로에서만 로드할지, 필요할 때만 불러오는 Skill에 둘지에 따라 비용과 효과가 달라진다.

Anthropic은 루트 `CLAUDE.md`를 항상 필요한 프로젝트 정보에, path-scoped Rules를 특정 파일 범위의 제약에, Skills를 반복 가능한 절차에, Hooks를 결정론적으로 실행되어야 하는 동작에 쓰는 구분을 공식적으로 제시한다.

### 2. "많이 적을수록 잘 따른다"는 가정은 위험하다

Anthropic은 context window를 유한한 자원으로 보고 최소한의 고신호 토큰을 넣는 것을 권장한다. OpenAI 역시 2026년 9월 GPT-6 Astra 지침에서 오래된 `AGENTS.md`와 장황한 Skill 설명이 오히려 최신 모델을 과도하게 구속할 수 있다고 경고한다.

### 3. Skill의 description은 요약문이 아니라 라우팅 인터페이스다

Skill 본문보다 먼저 모든 Skill의 이름과 description이 모델에 노출된다. 따라서 description은 다음 두 가지를 정확히 말해야 한다.

- 무엇을 하는 Skill인가.
- 정확히 언제 사용해야 하는가.

인접한 요청까지 끌어들이는 광범위한 description은 false positive를 만든다.

### 4. 지침 파일은 문서이면서 실행 품질에 영향을 주는 소프트웨어 아티팩트다

2026년 연구는 실제 공개 `SKILL.md`에서 품질 문제가 매우 흔하다고 보고한다.

- 238개 실사용 Skill을 분석한 연구는 99% 이상에서 하나 이상의 "skill smell"을 발견했다.
- 138,133개 공개 Skill 연구는 91.8%에서 최소 하나의 재사용성 결함을 탐지했다.
- 별도의 WebDev Skill 벤치마크에서는 대상 Skill 주입이 모든 경우에 도움이 되지 않았으며, 일부 조건에서 성공률 감소와 큰 토큰 비용 증가가 관찰됐다.

따라서 지침 품질은 "읽어 보고 좋아 보이는가"가 아니라 실제 동작으로 평가해야 한다.

### 5. 반복 지침은 더 강한 구조로 승격해야 한다

pstack의 실제 작성 규칙은 반복되는 자연어 지시를 계속 추가하기보다 lint, metadata, runtime check, script 같은 구조로 옮기는 방향을 취한다.

이 원칙은 책의 중요한 기준으로 채택할 가치가 있다.

> 판단이 필요한 것은 지침으로 남기고, 기계적으로 판정 가능한 것은 가능한 한 기계가 판정하게 한다.

## 리서치 파일

- [01-core-authoring-principles.md](01-core-authoring-principles.md): 지침 파일 작성 원칙
- [02-claude-md-and-rules.md](02-claude-md-and-rules.md): CLAUDE.md와 Rules
- [03-skill-md-authoring.md](03-skill-md-authoring.md): SKILL.md 작성법
- [04-hooks-and-enforcement.md](04-hooks-and-enforcement.md): Hooks와 구조적 강제
- [05-pstack-case-study.md](05-pstack-case-study.md): pstack 지침 파일 사례 분석
- [06-cross-vendor-comparison.md](06-cross-vendor-comparison.md): Claude, Codex, Cursor, Gemini, Copilot 비교
- [07-evaluation-and-skill-smells.md](07-evaluation-and-skill-smells.md): 평가 방법과 Skill smell 연구
- [08-source-catalog.md](08-source-catalog.md): 1차 자료와 논문 목록
- [09-book-outline.md](09-book-outline.md): 책 목차 후보
- [10-anthropic-internal-skill-lessons.md](10-anthropic-internal-skill-lessons.md): Anthropic 내부 Skill 운영에서 추출한 작성 원칙
- [11-public-instruction-corpus.md](11-public-instruction-corpus.md): 공개 저장소 지침 파일 35개 1차 corpus
- [12-observed-patterns-and-smells.md](12-observed-patterns-and-smells.md): corpus에서 관찰한 작성 패턴과 instruction smell
- [13-real-world-validation-patterns.md](13-real-world-validation-patterns.md): 실제 저장소의 validator와 trigger eval 운영 방식
- [14-real-world-hook-patterns.md](14-real-world-hook-patterns.md): 실제 저장소의 Hook enforcement 및 테스트 패턴
- [15-instruction-debt-history.md](15-instruction-debt-history.md): 공개 저장소 commit history로 추적한 Instruction Debt
- [16-nested-scope-case-studies.md](16-nested-scope-case-studies.md): nested AGENTS.md와 path scope 실제 사례
- [17-experiment-protocol.md](17-experiment-protocol.md): Skill routing, scope, instruction debt 자체 실험 프로토콜
- [18-trigger-eval-corpus.md](18-trigger-eval-corpus.md): feature/bugfix/refactor/review/none 80개 trigger corpus
- [19-scope-eval-fixture.md](19-scope-eval-fixture.md): monolithic root vs nested/path-scoped instruction 비교 fixture 설계
- [20-evidence-gap-matrix.md](20-evidence-gap-matrix.md): 책의 핵심 주장별 근거 수준과 남은 실험 공백
- [21-cross-host-skill-pilot-adapters.md](21-cross-host-skill-pilot-adapters.md): Claude/Codex/Cursor/Gemini/Copilot Skill runtime·관측 차이
- [22-popular-skills-rules-2026-q3.md](22-popular-skills-rules-2026-q3.md): 최근 3개월 유명 Skill 8개 저장소의 실제 규칙·변경 이력 비교
- [23-operational-skill-rule-patterns.md](23-operational-skill-rule-patterns.md): 브라우저·배포·DB·리뷰·보안 등 업무형 Skill의 상태·권한·handoff 규칙
- [24-popular-skill-rule-matrix.md](24-popular-skill-rule-matrix.md): 대표 Skill 20개의 규칙 패턴 질적 비교 matrix
- [25-official-vendor-skill-maintenance.md](25-official-vendor-skill-maintenance.md): Firebase·Expo·Supabase·Cloudflare·Firecrawl·Stitch의 최신성·eval 격리·router 압축 사례
- [26-popular-skills-saturation-and-governance.md](26-popular-skills-saturation-and-governance.md): GitHub·Stripe·MongoDB·HashiCorp까지 확장한 governance 패턴과 자료 수집 포화점 판단
- [27-corpus-ten-axis-reclassification.md](27-corpus-ten-axis-reclassification.md): 기존 35개 corpus를 Trigger~Maintenance 10축으로 재분류
- [28-bad-good-refactoring-casebook.md](28-bad-good-refactoring-casebook.md): root bloat·broad trigger·state collision·stale CLI 등 bad→good composite 사례
- [29-structural-validator-spec.md](29-structural-validator-spec.md): structural validator가 검사할 것과 semantic eval로 넘길 것의 경계
- [30-instruction-review-checklist.md](30-instruction-review-checklist.md): CLAUDE/AGENTS/Rule/Skill/Hook 유형별 실전 리뷰 체크리스트
- [31-product-edge-source-deep-dive.md](31-product-edge-source-deep-dive.md): Claude prompt-audit, Cursor Rule validation, Codex skill-creator, Gemini authoring, Copilot precedence 엣지 사례
- [32-link-only-source-audit.md](32-link-only-source-audit.md): 전체 연구 문서의 link-only source 전수 감사, historical/current/experiment-only 재분류
- [../experiments/trigger-routing/v0.1/README.md](../experiments/trigger-routing/v0.1/README.md): trigger routing calibration pilot fixture
- [../experiments/trigger-routing/v0.1/RUNBOOK.md](../experiments/trigger-routing/v0.1/RUNBOOK.md): host별 trigger pilot 실행 절차

## 출처 우선순위

이 리서치는 다음 순서로 근거를 취한다.

1. 제품 공식 문서와 공식 블로그
2. 공개 표준 명세
3. 공식 저장소의 실제 지침 파일
4. 학술 논문 및 preprint
5. 커뮤니티 글은 보조 사례로만 사용

특히 제품별 문법은 빠르게 변하므로 책 본문에는 "원리"와 "현재 제품 문법"을 분리해서 서술하는 것을 권장한다.
