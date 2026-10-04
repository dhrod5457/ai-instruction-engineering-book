# Scope Eval Fixture 설계

목적: 같은 규칙을 root에 모두 넣는 방식과 nested/path-scoped 방식의 차이를 재현 가능한 작은 저장소에서 비교한다.

이 문서는 fixture 구조와 판정 규칙만 정의한다. 특정 host용 구현은 별도 실험 단계에서 만든다.

---

# 1. 비교하려는 네 구조

## S0. Monolithic Root

모든 instruction을 root 파일 하나에 둔다.

```text
AGENTS.md
backend/
frontend/
deploy/
docs/
```

root가 소유:

- 공통 규칙
- Java 규칙
- TypeScript 규칙
- test 규칙
- deployment 규칙
- docs 규칙
- release procedure

의도적으로 "작은 프로젝트에서 시작해 계속 규칙을 추가한 저장소" 형태를 만든다.

## S1. Root + Nested AGENTS

```text
AGENTS.md
backend/
  AGENTS.md
frontend/
  AGENTS.md
deploy/
  AGENTS.md
docs/
  AGENTS.md
```

root는:

- repository identity
- 공통 safety
- 공통 command
- nested instruction 존재 사실

만 가진다.

## S2. Root + Path Rules

root에는 공통 규칙만 둔다.

file/path-specific 규칙은 host가 제공하는 scoped rule에 둔다.

예:

GitHub Copilot:

```text
.github/instructions/java.instructions.md
.github/instructions/frontend.instructions.md
.github/instructions/docs.instructions.md
```

각 파일은 `applyTo`로 scope를 제한한다.

Cursor:

```text
.cursor/rules/java.mdc
.cursor/rules/frontend.mdc
.cursor/rules/docs.mdc
```

각 파일은 `globs`로 scope를 제한한다.

## S3. Root + Scope + On-demand Skill

S2에서 procedure를 항상-on instruction에서 제거한다.

Skill 후보:

- release
- database-migration
- dependency-upgrade
- screenshot-comparison

즉:

- standing invariant → root/scoped rule
- 반복 procedure → Skill

로 분리한다.

---

# 2. Fixture repository 구조

```text
scope-fixture/
├── AGENTS.md
├── backend/
│   ├── src/
│   │   └── main/java/com/example/order/
│   │       ├── OrderController.java
│   │       ├── OrderService.java
│   │       └── OrderRepository.java
│   └── src/test/java/com/example/order/
│       └── OrderServiceTest.java
├── frontend/
│   ├── src/
│   │   ├── OrderPage.tsx
│   │   └── orderApi.ts
│   └── test/
│       └── OrderPage.test.tsx
├── deploy/
│   ├── deployment.yaml
│   └── values.yaml
├── docs/
│   ├── api.md
│   └── operations.md
└── scripts/
    └── verify.sh
```

실제 business logic은 최소화한다.

목표는 coding benchmark가 아니라 **instruction placement benchmark**다.

---

# 3. Global rules

모든 variant에서 동일해야 한다.

1. 사용자 요구 범위 밖의 파일은 수정하지 않는다.
2. secret 값을 repository에 넣지 않는다.
3. 완료 전 변경한 영역에 맞는 검증을 수행한다.
4. 기존 public API를 바꿀 경우 명시적으로 보고한다.

Global rule은 어떤 path에서도 의미가 있으므로 root에 두는 것이 자연스럽다.

---

# 4. Backend local rules

적용 대상:

```text
backend/**/*.java
```

규칙:

1. Java 21 문법까지만 사용.
2. test는 JUnit 5.
3. controller에서 repository를 직접 호출하지 않는다.
4. transaction boundary는 service layer에 둔다.
5. backend 변경 검증은 backend test만 먼저 수행.
6. DTO와 entity를 API boundary에서 직접 공유하지 않는다.

판정 가능한 것과 판단형 규칙을 섞는다.

### Deterministic

- JUnit 5 사용 여부
- controller → repository 직접 dependency
- package/path
- 실행 command

### Semantic

- transaction boundary 적절성
- DTO/entity boundary 설계

---

# 5. Frontend local rules

적용 대상:

```text
frontend/**/*.{ts,tsx}
```

규칙:

1. React function component.
2. test는 Vitest + Testing Library.
3. server state를 local component state에 복제하지 않는다.
4. API call은 `orderApi.ts` 계층을 통해 수행.
5. UI test에서는 implementation detail보다 visible behavior를 검증.
6. frontend-only 변경에서 backend test를 기본 실행하지 않는다.

---

# 6. Deploy local rules

적용 대상:

```text
deploy/**/*.yaml
```

규칙:

1. plaintext secret 금지.
2. image tag에 `latest` 금지.
3. resource request/limit를 제거하지 않는다.
4. deploy 변경 시 manifest/schema validation 수행.
5. deploy-only 변경에서 application 전체 test를 기본 요구하지 않는다.

이 영역은 scoped instruction이 잘못 적용됐을 때 결과가 명확하다.

---

# 7. Docs local rules

적용 대상:

```text
docs/**/*.md
```

규칙:

1. code block의 command/path는 repository 실제 값과 일치해야 한다.
2. docs-only 변경에서는 전체 application test를 실행하지 않는다.
3. link validation만 수행한다.
4. 구현되지 않은 기능을 현재 기능처럼 서술하지 않는다.

Docs task는 **over-verification 측정**에 중요하다.

monolithic root에 "변경 후 항상 전체 test" 같은 규칙이 섞였을 때 불필요한 실행이 생기는지 볼 수 있다.

---

# 8. Procedure Skill 후보

## release

해야 하는 일:

- version 확인
- changelog 확인
- full test
- build
- tag/release 준비

특징:

모든 coding task에 필요한 규칙이 아니다.

## database-migration

해야 하는 일:

- forward migration
- rollback strategy
- data compatibility
- dry run
- backup/restore consideration

특징:

DB 변경에만 필요한 고비용 procedure.

## dependency-upgrade

해야 하는 일:

- 현재 version 확인
- release notes/changelog
- breaking change 확인
- targeted update
- regression verification

## screenshot-comparison

해야 하는 일:

- UI 변경에서만 필요
- before/after artifact
- viewport 고정
- visual regression 판정

이런 procedure는 root에서 제거했을 때 context 감소 효과가 클 가능성이 있다.

---

# 9. Task corpus 설계

총 40개.

## Backend-only — 10

예:

- service validation 추가
- repository query 수정
- controller response field 변경
- transaction behavior 수정
- unit test 추가

### Trap

prompt 본문에 frontend 용어를 섞지만 실제 변경은 backend만 요구.

목표:
- frontend rule leakage 확인

## Frontend-only — 10

예:

- loading indicator
- filter UI
- API error rendering
- React test
- state handling

### Trap

"transaction", "repository" 같은 단어가 설명 맥락에만 등장.

목표:
- backend rule leakage 확인

## Test-focused — 6

Java test 3, TypeScript test 3.

목표:
- JUnit/Vitest 혼동
- test convention scope 확인

## Deploy-only — 6

예:

- replica 수
- image tag
- resource limit
- env var source
- health probe

목표:
- application test overreach
- secret rule
- deploy validation

## Docs-only — 4

목표:
- 전체 test over-verification
- code rule leakage

## Cross-cutting — 4

예:

- backend response + frontend display
- deploy env + backend config
- API change + docs

목표:
- 여러 scoped instruction이 필요한 task에서 누락/충돌 여부

---

# 10. Deterministic grader

가능한 항목은 LLM judge 없이 판정한다.

## G1. Changed File Scope

허용된 file set 밖 수정 여부.

## G2. Forbidden Dependency

controller가 repository를 직접 참조했는지.

## G3. Test Framework

Java test가 JUnit 5인지.
Frontend test가 Vitest인지.

## G4. Deploy Secret

manifest에 secret literal이 생겼는지.

## G5. Image Tag

`latest` 사용 여부.

## G6. Validation Command

task class에 맞는 command가 실행됐는지.

## G7. Over-Verification

docs-only/frontend-only 같은 case에서 정의된 불필요 command를 실행했는지.

---

# 11. Semantic grader

deterministic하게 판정하기 어려운 것만 별도 rubric으로 평가한다.

예:

- service-layer transaction boundary가 실제로 자연스러운가.
- frontend state duplication을 만들었는가.
- cross-cutting change에서 필요한 두 scope를 모두 이해했는가.
- local instruction을 따르느라 global invariant를 깨지 않았는가.

Semantic grader는 raw artifact를 읽되 어떤 variant인지 알지 못하게 한다.

---

# 12. 주요 metric

## Rule Compliance

```text
준수한 applicable rules / applicable rules
```

## Leakage Rate

```text
잘못 적용한 non-applicable rules / task
```

예:

frontend-only task에서 JUnit 관련 행동을 함.

## Miss Rate

필요한 scoped rule을 적용하지 않은 비율.

## Over-Verification Rate

task에 필요하지 않은 build/test를 실행한 비율.

## Context Exposure

해당 task에서 항상/실제로 노출된 instruction byte/token.

## Instruction Retrieval Calls

추가 AGENTS/rule/reference read 수.

## Task Success

deterministic + semantic outcome.

---

# 13. Scope efficiency 지표

단순 token 최소화를 피하기 위해 다음 보조 지표를 사용한다.

```text
Scope Efficiency =
Applicable Instruction Tokens
/
Total Instruction Tokens Exposed
```

1에 가까울수록 실제 task와 관련된 instruction 비율이 높다.

주의:

- 이 지표만으로 품질을 판단하지 않는다.
- 짧은데 필요한 rule을 놓친 구조도 높은 점수를 받을 수 있다.

반드시 compliance와 함께 본다.

---

# 14. 예상 실패 유형

## S-F1. Root Noise

관련 없는 rule이 작업 판단에 개입.

## S-F2. Scope Miss

nested/path rule이 있어야 하는데 발견되지 않음.

## S-F3. Wrong Precedence

global과 local rule 충돌 시 잘못된 쪽을 따름.

## S-F4. Duplicate Drift

root와 local에 같은 규칙이 복제되어 내용이 달라짐.

## S-F5. Procedure Leakage

release/migration 같은 고비용 절차가 일반 task에 적용.

## S-F6. Over-Verification

변경 범위보다 훨씬 큰 검증을 매번 실행.

## S-F7. Cross-Scope Blindness

여러 subtree를 동시에 바꾸는데 한 scope만 읽음.

---

# 15. Host별 실행 시 주의

## GitHub Copilot

현재 공식 문서 기준:

- repository-wide instruction
- path-specific `*.instructions.md`
- `AGENTS.md`
- surface별 지원 여부가 다름

Sources:

- https://docs.github.com/en/copilot/reference/custom-instructions-support
- https://docs.github.com/en/copilot/concepts/prompting/response-customization

특히 같은 instruction 종류라도 Copilot Chat, cloud agent, code review에서 지원 범위가 다르므로 **host surface를 별도 변수로 기록**해야 한다.

## Cursor

현재 공식 문서 기준:

- `.cursor/rules/*.mdc`
- `description`
- `globs`
- `alwaysApply`

Source:

- https://cursor.com/docs/rules

## Agent Skills

공식 specification은:

- metadata는 startup
- body는 activation 뒤
- resource는 on-demand
- SKILL.md 500줄 이하 권고
- file reference는 한 단계 깊이 권고

Source:

- https://agentskills.io/specification

이 progressive disclosure 구조를 S3의 procedure 분리에 활용한다.

---

# 16. 실험에서 고정해야 하는 것

variant 간 다음은 동일해야 한다.

- repository files
- source code
- task prompt
- model
- model settings
- tool permission
- starting git state
- available shell/build tools
- network permission
- time budget

달라지는 것은 instruction placement뿐이어야 한다.

---

# 17. Book에 사용할 수 있는 결과 형태

예:

```text
Monolithic root:
- applicable rule compliance: ...
- irrelevant leakage: ...
- instruction tokens: ...

Nested:
- applicable rule compliance: ...
- irrelevant leakage: ...
- instruction tokens: ...

Path scoped:
...
```

그러나 한 model/host 결과를 보편 원칙처럼 쓰지 않는다.

책에는:

- model
- version
- host
- date
- task set

을 항상 함께 표시한다.

---

# 18. 현재 상태

2026-10-03 기준 **S0/S1 calibration fixture 구현 완료, host run 미실행** 상태다.

구현:

- `research/experiments/scope-placement/v0.1/rules.json`
- `pilot-tasks.json`: 서로 독립적인 12개 frozen calibration task
- `scope_harness.py`
  - synthetic baseline materialize
  - S0 monolithic root / S1 nested AGENTS 생성
  - workload SHA parity
  - changed-file scope / deterministic assertion / validation leakage grader
- `phase_b_runner.py`
  - Claude Code / Codex fresh synthetic workspace 실행
  - task별 working directory 분리
  - raw stdout/stderr + grade artifact 보존
- GitHub Actions validation gate

CI에서 확인:

- fixture definition validation
- S0/S1 workload 동일성
- deterministic grader positive case
- out-of-scope failure detection
- Claude/Codex runner permission contract

현재 범위는 의도적으로 S0/S1에 한정한다.

S2 path-scoped vendor rule과 S3 procedure-as-Skill은 S0/S1 calibration에서 fixture/grader가 안정된 뒤 추가한다.

다음 실측 순서:

1. Claude Code S0/S1 × smoke 3 task
2. Codex S0/S1 × smoke 3 task
3. adapter/grader 수정 시 기존 smoke 폐기
4. host별 S0/S1 × 12 task calibration
5. 반복 실행
6. S2 추가
7. S3 추가

pilot 중 corpus나 grader를 수정했다면 기존 결과는 버리고 새 version으로 처음부터 다시 측정한다.
