# 리서치 전체 Link-only Source Audit

기준일: 2026-10-03

## 1. 목적

31번 조사에서는 `08-source-catalog.md`에 명시적으로 남아 있던 미조사 항목을 닫았다.

이번 단계에서는 그 목록에만 의존하지 않고 `research/instruction-files` 전체 Markdown을 다시 훑어 다음 유형을 찾았다.

- URL만 있고 실제 내용 분석이 없는 source
- source catalog에서 한두 줄만 요약되고 다른 문서에서 해부되지 않은 source
- 과거에는 유효했지만 현재는 archived/deprecated되어 근거 등급을 내려야 하는 source
- 같은 vendor의 공식 문서끼리 현재 semantics가 어긋나는 source
- 링크는 충분하지만 실제 behavior를 확인하지 않아 문서 조사와 실측을 혼동한 항목

목적은 URL 개수를 늘리는 것이 아니다.

> **각 링크가 책의 어떤 주장에 어떤 강도로 기여하는지를 분류하고, 링크만 남은 근거를 제거한다.**

---

# 2. 감사 범위와 판정 기준

대상:

- `01` ~ `31` 연구 문서
- `README.md`
- 총 32개 Markdown

검토 관점:

## A. Catalog-only

`08-source-catalog.md`, README, outline 등에만 존재하고 실제 분석 문서에 등장하지 않는가.

## B. Analysis-backed

URL 자체는 출처 목록에만 있어도 같은 문서나 후속 문서에서:

- 주장
- 실제 동작
- 사례
- 제한
- 책 적용점

이 분석되어 있는가.

## C. Historical-only

현재 공식 페이지가 archived/deprecated이고 현행 syntax의 근거로 사용하면 안 되는가.

## D. Surface conflict

같은 vendor 공식 문서끼리 지원 범위나 precedence 설명이 다르게 보이는가.

## E. Experiment-only gap

더 읽을 문서가 부족한 것이 아니라 동일 fixture로 직접 실행해야만 닫히는가.

---

# 3. 전수 감사 결과

큰 결론부터 말하면:

> **핵심 주장에 사용되는 링크 중 “URL만 남아 있어 근거를 확인할 수 없는” 항목은 거의 남지 않았다.**

35개 공개 corpus의 원문 링크는 `11-public-instruction-corpus.md`에서 한 줄씩만 나열되어 보이지만 실제로는:

- 같은 파일의 corpus table
- `12-observed-patterns-and-smells.md`
- `16-nested-scope-case-studies.md`
- `27-corpus-ten-axis-reclassification.md`

에서 후속 분석이 이루어져 있다.

유명 Skill 저장소 링크도:

- 22번
- 23번
- 25번
- 26번

문서에서 commit/history 및 rule pattern까지 분석되어 단순 링크가 아니다.

논문 링크도:

- `07-evaluation-and-skill-smells.md`
- `20-evidence-gap-matrix.md`

에서 연구 설정, 수치, 한계, 일반화 금지 조건까지 정리되어 있다.

따라서 남은 진짜 후보는 4개였다.

1. OpenAI `PLANS.md`
2. OpenAI current AGENTS.md hierarchy
3. Gemini extension guidance
4. GitHub Copilot Code Review customization

이번 문서에서 이 네 개를 닫는다.

---

# 4. OpenAI PLANS.md: 현재 표준이 아니라 archived historical pattern

Source:

- https://developers.openai.com/cookbook/articles/codex_exec_plans

문서는 2025-10-07에 공개되었고 현재 페이지 상단에:

> This recipe is archived and may reference outdated models or APIs.

라고 표시된다.

따라서 이 문서를:

- 최신 Codex syntax
- 최신 model recommendation
- 현재 mandatory workflow

의 근거로 사용하면 안 된다.

## 4.1 그래도 남길 가치가 있는 이유

이 글의 가치가 남는 부분은 제품 syntax가 아니라 **instruction placement pattern**이다.

구조:

```text
AGENTS.md
  -> 복잡한 기능/대규모 refactor에서 ExecPlan을 사용하라는 standing rule

.agent/PLANS.md
  -> ExecPlan이 어떤 문서이며 어떻게 유지할지에 대한 detailed procedure

실제 ExecPlan
  -> 현재 task의 living execution state
```

즉 세 책임이 분리된다.

### Standing trigger

항상 읽히는 파일에는:

> 언제 detailed planning procedure를 호출하는가.

만 둔다.

### Procedure definition

PLANS.md에는:

- plan 형식
- milestone
- progress
- decision log
- restartability

를 둔다.

### Task state

실제 ExecPlan이 현재 작업의 상태를 가진다.

이것은 책에서 다루는:

- root instruction 최소화
- detailed procedure 분리
- persistent task artifact

와 잘 맞는다.

## 4.2 현재도 이어지는 패턴

OpenAI의 더 최근 Code Modernization cookbook도 Phase 0에서 AGENTS + PLANS 구조를 다시 사용한다.

다만 이것 역시 특정 modernization workflow의 cookbook 사례다.

따라서 책에서는:

> “PLANS.md가 OpenAI의 현재 universal standard다”

가 아니라:

> “standing trigger와 long-running execution document를 분리한 historical/recipe pattern”

으로 사용한다.

Source:

- https://developers.openai.com/cookbook/examples/codex/code_modernization

## 4.3 재분류

기존:

- current official authoring source처럼 보일 수 있음

변경:

- **Historical official recipe**
- Principle support only
- current syntax source로 사용 금지

---

# 5. OpenAI current AGENTS.md hierarchy: 상세 semantics 확보

기존 source catalog에는:

- root-to-leaf injection
- directory-specific instruction

정도만 기록되어 있었다.

현재 OpenAI latest-model guide는 더 구체적이다.

Source:

- https://developers.openai.com/api/docs/guides/latest-model

## 5.1 discovery

Codex CLI는 대략 다음 범위를 탐색한다.

1. user Codex home
2. repository root
3. root에서 current working directory까지의 각 directory

optional fallback filename과 size cap도 존재한다.

## 5.2 merge order

발견된 instruction은 root-to-leaf 순으로 merge된다.

뒤의, 더 가까운 directory instruction이 앞의 instruction보다 우선할 수 있다.

즉 단순한 “nearest only” model과 다르다.

## 5.3 model-visible representation

각 discovered instruction chunk는 model에게 별도 user-role message 형태로 주입된다.

개념적으로:

```text
# AGENTS.md instructions for <directory>
<INSTRUCTIONS>
...
</INSTRUCTIONS>
```

형태다.

이 사실은 두 가지를 의미한다.

### Scope는 파일 위치만의 문제가 아니다

model-visible context에 directory identity가 같이 전달된다.

### Conflicting rule을 많이 쌓으면 merge가 해결해 주는 것이 아니다

later instruction이 override semantics를 갖더라도 prose conflict를 의도적으로 설계하는 것은 여전히 위험하다.

## 5.4 AGENTS.override.md

현재 guide는 `AGENTS.override.md`도 언급한다.

override file이 사용되어도 injected header에는 해당 directory가 표시된다.

따라서 책의 제품 참조 부록에서 Codex semantics를 설명할 때:

- AGENTS.md
- AGENTS.override.md
- root-to-CWD discovery
- root-to-leaf injection

을 하나의 현재 product syntax block으로 묶는 편이 맞다.

## 5.5 모델 업그레이드와 연결

같은 current guide는 GPT-6 Astra 계열이 Skill/AGENTS 등의 instruction에 더 민감할 수 있다고 설명하며 accessible instruction files를 audit하라고 권한다.

즉:

> nested instruction support가 좋아졌기 때문에 더 많이 써도 된다

가 아니라:

> 더 잘 따르므로 오래된 instruction debt의 영향도 더 커질 수 있다

로 해석해야 한다.

---

# 6. Gemini extension guidance: context surface를 선택하는 공식 decision table

기존 source catalog에는 Gemini extension guidance를:

- GEMINI.md always-on
- Skill on-demand
- Hook lifecycle

정도로만 적어 두었다.

현재 공식 extension guide는 이를 한 단계 더 명확한 **surface selection table**로 제공한다.

Source:

- https://geminicli.com/docs/extensions/writing-extensions/

## 6.1 MCP server

사용 목적:

- 새 tool
- database/API access
- local application control

Invocation:

- model

즉 “지식을 알려주는 것”과 “새 capability를 주는 것”을 분리한다.

## 6.2 Custom command

사용 목적:

- 반복 prompt shortcut
- 명시적 automation

Invocation:

- user

Skill과의 중요한 차이는 **user-invoked surface**라는 점이다.

## 6.3 GEMINI.md

사용 목적:

- extension personality
- coding standard
- essential knowledge
- every-session context

Invocation:

- CLI가 model context에 항상 제공

## 6.4 Agent Skill

사용 목적:

- 복잡하지만 가끔 필요한 task-specific workflow

Invocation:

- model

공식 문서 자체가 context clutter를 피하기 위해 occasional workflow를 Skill로 옮기라고 설명한다.

## 6.5 Hook

사용 목적:

- lifecycle intercept
- argument validation
- logging
- input/output modification

Invocation:

- CLI

즉 Gemini도:

```text
always-on knowledge -> GEMINI.md
on-demand procedure -> Skill
deterministic lifecycle action -> Hook
new external capability -> MCP
explicit shortcut -> Custom Command
```

로 역할을 나눈다.

이것은 책의 vendor-neutral placement decision tree를 강하게 지지한다.

## 6.6 Extension best practices의 GEMINI.md 규칙

공식 extension best-practices는 GEMINI.md에 대해:

- high-level purpose에 집중
- concise
- exhaustive documentation dump 금지
- tool/command 사용 예시는 짧게

를 권한다.

Source:

- https://geminicli.com/docs/extensions/best-practices/

따라서 Gemini의 always-on context도 “extension manual 전체”가 아니라 **essential context**여야 한다.

## 6.7 Hook precedence

현재 Gemini hooks 문서는 여러 설정 layer가 동시에 존재할 때 Hook config precedence를 설명한다.

높은 순:

1. project
2. user
3. system
4. extension

Source:

- https://geminicli.com/docs/hooks/

이것은 Skill discovery precedence와 별개의 precedence system이다.

즉 동일 vendor 안에서도:

- Skill discovery precedence
- Hook config precedence
- GEMINI.md context discovery

를 하나의 precedence 규칙으로 뭉치면 안 된다.

---

# 7. GitHub Copilot Code Review: 별도 instruction runtime으로 봐야 한다

기존 catalog의 “Code review customization comparison”은 지나치게 얕았다.

현재 공식 문서는 Code Review 자체를 별도의 instruction consumer로 봐야 할 정도의 semantics를 제공한다.

Sources:

- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review
- https://docs.github.com/en/copilot/tutorials/customize-code-review
- https://docs.github.com/en/copilot/reference/custom-instructions-support

## 7.1 지원되는 주요 instruction surface

현재 Code Review guide는 다음을 설명한다.

- repository-wide: `.github/copilot-instructions.md`
- path-specific: `.github/instructions/**/*.instructions.md`
- repository context: `AGENTS.md`
- 추가 instruction file: `CLAUDE.md`, `GEMINI.md`, `REVIEW.md`

그리고 agent skills도 review context에 사용할 수 있다.

## 7.2 가장 중요한 edge: head branch semantics

PR을 review할 때 Copilot Code Review는:

- base branch가 아니라
- **head branch의 repository instruction, agent instruction, skills**

를 읽는다.

즉 다음 workflow가 가능하다.

```text
feature branch
  + code change
  + instruction/skill change
      ↓
same PR에서 Copilot review
      ↓
새 instruction behavior 관찰
```

instruction change를 merge하기 전에 같은 PR에서 test할 수 있다.

이것은 instruction engineering의 매우 좋은 self-test surface다.

## 7.3 단, contamination 위험도 있다

같은 특성 때문에 다음도 가능하다.

PR 작성자가 review instruction을 함께 수정하면 그 PR의 review behavior가 바뀐다.

따라서 high-assurance repository라면:

- instruction file 변경을 security-sensitive governance change로 취급
- review instruction 변경과 일반 feature diff를 구분
- independent reviewer 사용
- baseline instruction과 candidate instruction 결과 비교

를 고려할 수 있다.

## 7.4 Code Review Skill routing

GitHub은 review-focused skill directory/name/description을 사용하면 Code Review가 해당 Skill을 사용할 가능성이 높아진다고 설명한다.

예:

- `code-review`

또 review comment의 attribution과 linked review session에서:

- 어떤 Skill
- 어떤 MCP server
- 어떤 tool

이 사용됐는지 확인할 수 있다.

이것은 routing/output eval의 관측 surface로 가치가 있다.

## 7.5 공식 문서끼리의 support matrix tension

전수 감사 중 한 가지 주의점도 발견했다.

Code Review 사용 가이드는 현재:

- CLAUDE.md
- GEMINI.md
- REVIEW.md

까지 읽는다고 설명한다.

반면 custom-instructions support matrix는 surface별 표기가 더 제한적으로 보이는 구간이 있다.

이것을 곧바로 “문서 오류”라고 단정하지 않는다.

가능한 이유:

- rollout timing
- surface별 기능 차이
- support matrix 갱신 지연
- 문서 표현 범위 차이

책에서는 이 사례를:

> **지원 여부는 한 개 문서가 아니라 현재 target surface에서 다시 확인한다.**

의 근거로 사용한다.

실제 production rule을 만들 때는 target surface smoke test가 필요하다.

---

# 8. Link-only로 보였지만 실제로는 상세 조사된 항목

전수 감사에서 false positive도 많았다.

## 8.1 35개 public corpus 원문 링크

`11-public-instruction-corpus.md` 하단에는 URL이 줄줄이 있어 link dump처럼 보인다.

하지만:

- corpus table에 각 관찰점 존재
- 12번에서 smell/pattern 합성
- 27번에서 10축 재분류

가 되어 있다.

따라서 raw link list는 provenance index이지 미조사 목록이 아니다.

## 8.2 commit history 링크

`15-instruction-debt-history.md`의 commit URL은 section 시작에 붙어 있어 기계적으로 보면 설명이 짧다.

실제 section 뒤에는:

- before/after
- 왜 변경됐는지
- smell
- 일반화 가능한 rule

이 상세히 있다.

## 8.3 operational/vendor repository 링크

22/23/25/26 문서도 repository URL이 section 초반에 있어 “링크만 있음”으로 오탐되기 쉽다.

실제 분석은 child heading에 있다.

따라서 향후 자동 link audit를 만들 경우:

> URL 주변 N자만 보지 말고 parent section의 descendant heading까지 포함해야 한다.

---

# 9. 감사 후 source 상태

## 상세 조사 완료

- Claude project memory / Rules
- Claude Skills
- Claude Hooks
- prompt audit
- Agent Skills spec
- Codex AGENTS hierarchy
- Codex Skills / eval
- Codex skill-creator
- Cursor Rules / Skills / Hooks
- Gemini memory / Skills / extension surface
- Copilot repository instructions / CLI / code review
- nested AGENTS cases
- public corpus
- famous/official Skill maintenance
- academic/preprint evidence

## Historical source로 하향

- OpenAI `Using PLANS.md for multi-hour problem solving`
  - archived
  - principle pattern만 사용

## 실측으로만 닫을 수 있음

- same Skill cross-host routing
- monolith vs scoped instruction
- description boundary
- reference depth
- model-upgrade instruction diet
- prose vs Hook enforcement
- Copilot/other surface documentation conflict의 실제 runtime behavior

---

# 10. 책에 추가해야 할 새 포인트

이번 audit은 새 chapter를 요구할 정도의 범위 확대는 아니다.

기존 장에 다음을 보강하면 된다.

## 4장 AGENTS.md와 portability

추가:

- Codex root-to-CWD discovery
- root-to-leaf injection
- AGENTS.override.md
- same vendor에서도 surface semantics를 확인해야 함

## 10장 구조적 enforcement

추가:

- product support != repository validator
- extension surface selection table

## 16장 A/B와 blinded eval

추가:

- Copilot Code Review head-branch instruction을 candidate test surface로 활용 가능
- 단 candidate가 evaluator context까지 바꾸는 contamination 주의

## 18장 모델이 바뀌면 지침도 다시 본다

추가:

- archived official recipe와 current source를 구분
- official source 자체도 freshness audit

## 부록 C 제품별 참조

추가:

- PLANS.md historical 표시
- Codex AGENTS hierarchy 상세
- Gemini extension decision table
- Copilot Code Review head-branch semantics

---

# 11. 최종 판정

이번 전수 감사 후에는 “링크만 저장하고 실제 내용은 조사하지 않았다”는 이유로 추가 수집해야 할 **핵심 source는 사실상 없다.**

남은 작업을 source collection이라고 부르면 오히려 방향이 흐려진다.

다음 단계는:

```text
source collection
    ↓ 완료에 가까움

source classification / freshness
    ↓ 이번 audit로 정리

controlled experiments
    ↓ 현재 가장 큰 공백
```

이다.

따라서 이후 새 URL을 추가하려면 최소 하나를 만족해야 한다.

1. 기존 taxonomy에 없는 새로운 authoring failure를 보여준다.
2. 현재 Open gap의 실측 결과를 제공한다.
3. 기존 공식 semantics가 바뀌었음을 증명한다.
4. 실제 instruction deletion/refactor의 새로운 before/after evidence를 준다.

그 외의 링크는 수집하지 않는 편이 낫다.
