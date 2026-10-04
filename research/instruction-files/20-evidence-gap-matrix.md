# Evidence Gap Matrix

기준일: 2026-09-30

목적: 책의 핵심 주장을 "그럴듯한 조언"으로 쓰지 않도록, 각 주장에 어떤 종류의 근거가 있는지 관리한다.

근거 유형:

- **O** — Official documentation/spec
- **R** — Real-world repository snapshot
- **H** — Real-world commit/history evidence
- **P** — Published paper/preprint
- **E** — Our reproducible experiment

강도 표기:

- Strong — 서로 다른 유형의 근거가 3개 이상이며 직접적인 사례가 있음
- Medium — 공식/사례는 있으나 자체 검증 또는 일반화 근거가 부족
- Weak — 흥미로운 사례는 있으나 아직 주장으로 쓰기 위험
- Open — 실험/추가 조사 필요

---

# 1. Placement / Scope

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 모든 규칙을 root에 넣지 말고 필요한 scope로 내린다 | Yes | Yes | Partial | Indirect | Planned | Strong 원칙 / 효과 크기는 미검증 | Scope experiment |
| path-specific rule은 repo-wide noise를 줄이는 목적에 적합 | Yes | Yes | Partial | No | Planned | Medium | S0~S2 비교 |
| nested AGENTS는 subsystem local invariant에 적합 | Yes | Yes | Yes | No | Planned | Strong | 실제 효과 수치만 보강 |
| procedure는 always-on rule보다 Skill이 적합한 경우가 있다 | Yes | Yes | Yes | No | Planned | Medium | S3 비교 |
| local gotcha는 source comment가 instruction file보다 나을 수 있다 | No | Yes | Partial | No | No | Weak | 더 많은 사례 필요 |

핵심 source:

- GitHub Copilot path-specific instructions
- Cursor Rules
- dotfiles nested AGENTS
- radio4000 nested AGENTS
- Pulumi nested AGENTS
- PI Dashboard instruction foldering

---

# 2. Skill Description / Routing

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| description은 routing interface다 | Yes | Yes | Yes | Partial | Planned | Strong | 80-case eval |
| what + when을 포함해야 한다 | Yes | Yes | Yes | No | Planned | Strong authoring rule | 실험 효과 측정 |
| broad description은 over-trigger 위험이 있다 | Yes | Yes | Yes | Partial | Planned | Medium-Strong | A0 vs A1 |
| adjacent boundary가 routing collision을 줄인다 | Partial | Yes | Yes | No | Planned | Medium | A1 vs A2 |
| manual-only Skill은 auto-trigger와 다르게 평가해야 한다 | Yes | Yes | Yes | No | Planned | Strong | A3 pilot |
| description을 줄이면 성능을 유지하면서 context를 줄일 수 있다 | Indirect | Yes | Yes | No | Planned | Medium | token + routing 측정 |

핵심 source:

- Agent Skills spec
- Anthropic Skill best practices
- skillhub trigger eval/history
- getsentry bad-output eval

---

# 3. Skill Body / Progressive Disclosure

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Skill body는 activation 후 전체가 로드된다 | Yes | N/A | N/A | No | No | Strong fact | 없음 |
| 긴 reference는 root에서 분리하는 편이 좋다 | Yes | Yes | Yes | Partial | Planned | Strong | token 실험 |
| reference chain은 얕게 유지하는 편이 좋다 | Yes | Yes | Partial | No | Not planned | Medium | deep-chain experiment 후보 |
| script로 deterministic work를 옮기면 prose를 줄일 수 있다 | Yes | Yes | Partial | No | Not planned | Medium | script-backed case 확장 |
| runtime docs와 maintainer docs를 분리할 수 있다 | Partial | Yes | Yes | No | No | Strong pattern | Sentry 사례 사용 |

핵심 source:

- agentskills.io specification
- Anthropic best practices
- getsentry runtime/SPEC/EVAL
- skillhub
- script-backed public Skills

---

# 4. Hook / Enforcement

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| critical invariant는 prose만으로 두지 않는 편이 좋다 | Yes | Yes | Yes | Security literature indirect | Not planned | Strong engineering principle | 실제 비교 실험 후보 |
| Hook도 테스트해야 한다 | Yes/Partial | Yes | Yes | No | No | Strong | 사례 chapter 작성 가능 |
| deny test와 legitimate near-match test를 같이 둬야 한다 | Partial | Yes | Yes | No | No | Strong case-based | dotfiles 사례 |
| Hook scope가 너무 넓으면 false positive/비용이 커진다 | Yes | Yes | Yes | No | No | Strong | 전후 commit 사용 |
| 안전 gate는 실제 위험 경계와 맞아야 한다 | General | Yes | Yes | No | No | Strong | overcorrection 사례 |
| equivalent bypass path를 함께 봐야 한다 | General | Yes | Yes | Security literature | No | Strong | gh bypass 사례 |
| Hook은 보호 대상 tool의 semantics를 정확히 모델링해야 한다 | No | Yes | Yes | No | No | Medium-Strong | target resolution 사례 |

---

# 5. Validation / Eval

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| structural lint와 semantic eval을 분리한다 | Partial | Yes | Yes | Evaluation literature | Planned | Strong | 자체 protocol 구현 |
| positive trigger만으로 부족하다 | Partial | Yes | Yes | Classification methodology | Planned | Strong | 80-case corpus |
| routing pair가 중요한 hard case다 | No direct | Yes | Yes | Classification methodology | Planned | Medium-Strong | corpus 실행 |
| raw artifact/trace를 보존해야 한다 | Partial | Yes | Yes | Eval methodology | Planned | Strong | experiment output schema |
| baseline/holdout을 둬야 한다 | Partial | Yes | Yes | Yes | Planned | Strong | 실행 |
| LLM judge만으로 structural fact를 판정하지 않는다 | Partial | Yes | Yes | Eval literature | Planned | Strong | deterministic grader |

---

# 6. Instruction Debt

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 지침은 계속 추가하면 부채가 된다 | Yes/Recent guidance | Yes | Yes | Skill smell studies | Planned | Strong | C experiment |
| 모델 업그레이드 후 오래된 scaffolding을 삭제해야 할 수 있다 | Yes | Yes | Yes | No | Planned | Strong | C0 vs C1 |
| old under-trigger fixes가 새 모델에서 over-trigger가 될 수 있다 | Yes/Partial | Yes | Yes | No | Planned | Medium-Strong | model-version 반복 |
| 중복 gate는 정상 workflow를 방해할 수 있다 | No direct | Yes | Yes | No | No | Strong case | flowstate/dotfiles |
| stale reference는 실행 영향이 있는 instruction debt다 | General | Yes | Yes | No | No | Strong | link validator chapter |
| registration drift는 instruction infrastructure bug다 | Partial | Yes | Yes | No | No | Strong | skillhub validator |

---

# 7. Portability

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AGENTS/Skill 지원 여부는 host/surface마다 다르다 | Yes | Yes | Yes | No | Planned | Strong | 실행 시 version lock |
| 한 host에서 동작해도 표준 준수라는 보장은 없다 | Yes | Yes | Yes | No | Planned | Strong | allowed-tools 사례 |
| provider extension과 portable core를 분리해야 한다 | Yes | Yes | Yes | No | Planned | Strong | cross-host experiment |
| syntax portability와 enforcement portability는 다르다 | Yes/Partial | Yes | Yes | No | Not planned | Medium-Strong | Gemini/Codex Hook 추가 조사 |
| 동일 SKILL.md가 여러 host에서 같은 trigger를 보장하지 않는다 | No | Partial | Partial | No | Planned | Open | cross-host routing 필수 |

가장 중요한 미검증 주장이다.

---

# 8. Context Cost

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| context는 제한된 자원이다 | Yes | Yes | Yes | Yes | Planned | Strong | 없음 |
| 항상-on instruction이 길수록 실제 task 품질이 떨어진다 | Indirect | Partial | Partial | Long-context papers indirect | Planned | Open | Scope experiment |
| relevant info 위치가 길어진 context에서 영향을 받을 수 있다 | N/A | N/A | N/A | Yes | Not direct | Medium background | 과도한 일반화 금지 |
| progressive disclosure가 실제 coding task 품질을 개선한다 | Official recommendation | Yes | Yes | No | Planned | Open | 직접 비교 필요 |

주의:

`Lost in the Middle`은 long-context QA 연구다.

이를 곧바로 "CLAUDE.md 300줄이면 coding 성능이 떨어진다"는 증거로 쓰면 안 된다.

책에서는:

- long context에 위치/검색 문제가 존재할 수 있다는 배경 연구
- instruction-file 효과는 자체 실험으로 별도 검증

으로 분리한다.

Source:

- https://arxiv.org/abs/2307.03172

---

# 9. 보안

| Claim | O | R | H | P | E | 현재 강도 | 다음 행동 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 외부 Skill은 코드/지침 공급망 위험이 있다 | Yes | Yes | Partial | Prompt injection literature | No | Strong | chapter source 보강 |
| reference/web content를 instruction으로 오인하면 위험하다 | General official | Partial | Partial | Yes | No | Medium-Strong | indirect injection 사례 |
| instruction hierarchy가 중요하다 | General | Partial | Partial | Yes | No | Strong background | hierarchy 논문 사용 |
| Skill 자체의 script/tool permission을 검토해야 한다 | Yes | Yes | Yes | No | No | Strong | checklist |

Background:

- Instruction Hierarchy: https://arxiv.org/abs/2404.13208

보안 논문은 repository instruction authoring에 직접 적용한 연구가 아닐 수 있으므로 범위를 명시한다.

---

# 10. 현재 가장 큰 Evidence Gap

우선순위 순.

## Gap 1. 실제 cross-host routing

질문:

같은 80개 prompt와 같은 Skill metadata를:

- Claude Code
- Codex
- Cursor
- Gemini CLI
- GitHub Copilot CLI

에서 실행했을 때 같은 routing pattern이 나오는가.

2026-09-30 공식 문서 비교로 **runtime semantics 차이와 adapter 요구사항은 정리했다**.

확인된 차이:

- Claude/Cursor/Copilot CLI: `disable-model-invocation` 지원
- Gemini CLI: 모델의 `activate_skill` + 사용자 consent
- Codex: structured eval trace는 강하지만 Claude식 manual-only field를 portable guarantee로 확인하지 못함
- activation evidence surface가 host마다 다름

남은 공백은 문서 조사보다 **실제 동일 corpus 실행 결과**다.

**우선순위: 최고 — Phase A pilot 실행 필요**

## Gap 2. Root monolith vs scoped instruction의 실제 효과

공식 문서는 scope 분리를 권장하고 실제 저장소도 그렇게 하지만:

- rule compliance
- irrelevant leakage
- token cost
- over-verification

을 같은 fixture로 측정한 자료는 아직 없다.

**우선순위: 최고**

## Gap 3. Description boundary의 실제 효과

skillhub 사례는 강하지만 특정 repository/model의 결과다.

80-case corpus로 반복 검증 필요.

**우선순위: 최고**

## Gap 4. Model upgrade 후 instruction diet

실제 commit 사례는 있지만 동일 task를 legacy/diet prompt로 비교한 controlled result가 없다.

**우선순위: 높음**

## Gap 5. Deep reference chain

공식 spec은 한 단계 깊이를 권장한다.

그러나 1-hop/2-hop/3-hop reference 구조가 retrieval 성공률과 token cost에 미치는 자체 결과가 없다.

**우선순위: 중간**

## Gap 6. Prose vs Hook enforcement

실전 사례는 충분하지만 controlled benchmark가 없다.

다만 책의 실전 가이드에는 사례만으로도 상당 부분 설명 가능하다.

**우선순위: 중간**

---

# 11. 현재 당장 수집을 줄여도 되는 영역

## 공식 문법

이미 충분:

- Agent Skills structure
- Claude Skill best practice
- Cursor Rules
- GitHub Copilot custom instruction
- AGENTS/nested scope

버전 변경 확인 외에 같은 종류의 공식 문서를 더 모으는 효용이 낮다.

## 일반 Agent framework

책 범위 밖.

추가 수집 금지 후보:

- multi-agent orchestration
- planner/executor architecture
- autonomous software factory
- memory framework
- MCP server architecture

지침 파일 작성 원칙과 직접 연결될 때만 포함한다.

## 좋은 SKILL.md 단순 추가

35개 corpus + 심층 사례가 이미 있다.

새 사례를 추가하려면 기존 taxonomy의 빈칸을 채워야 한다.

예:

- deep reference failure
- instruction removal PR
- real cross-host incompatibility
- nested scope conflict

그렇지 않으면 corpus 숫자만 늘어난다.

---

# 12. 집필 가능 상태

현재 자료만으로 비교적 자신 있게 작성 가능한 장:

- 3장 CLAUDE.md
- 4장 AGENTS.md
- 5장 Path-scoped Rules
- 6장 Skill 구조
- 8장 Skill body
- 9장 References/Scripts
- 10장 구조적 enforcement
- 11장 Hook
- 17장 Instruction Debt
- 18장 모델 변화
- 19장 리뷰 프로세스

자체 실험 결과가 나온 뒤 쓰는 편이 좋은 장:

- 7장 description
- 14장 Trigger Eval
- 15장 Output Eval
- 16장 A/B Eval

이 네 장은 실제 수치가 책의 차별점이 된다.

---

# 13. 다음 연구 순서

이제 추가 링크 수집보다 다음 순서가 우선이다.

1. Trigger corpus pilot
2. Scope fixture pilot
3. grader 보정
4. full repeated run
5. cross-host 반복
6. model-upgrade diet experiment
7. 결과를 바탕으로 7/14/16장 먼저 집필

실험이 예상과 다르면 현재 원칙을 고친다.

그게 이 책을 "지침 파일 모범답안 모음"이 아니라 검증 가능한 가이드로 만드는 핵심이다.


## 자료 수집 포화점: 유명 Skill 추가 수집

2026-09-30 기준 최근 3개월의 유명/공식 Skill 표본을 다음 범주까지 확장했다.

- 방법론형: Superpowers, Matt Pocock, Addy Osmani, ECC, Ponytail
- vendor framework: Anthropic, Vercel, Supabase, Cloudflare, Expo, Firebase
- operational: Microsoft Azure, Prisma, Firecrawl, agent-browser, Remotion, Sentry
- 추가 official-org: GitHub Awesome Copilot, Stripe, MongoDB, HashiCorp, Google Stitch

새 표본을 추가할수록 완전히 새로운 authoring axis보다 다음 기존 축이 반복됐다.

1. Trigger
2. Boundary
3. Preconditions
4. State / authority
5. Procedure
6. Permission / side effect
7. Evidence
8. Handoff
9. Freshness / canonical source
10. Eval / maintenance

따라서 단순히 "유명 Skill N개 더 수집"하는 작업의 추가 정보 가치는 낮아졌다.

### 남은 가치가 높은 비실측 작업

- 공개 corpus를 위 10개 축으로 재분류
- 대표 bad → good refactor case 작성
- structural validator 규칙 설계
- 최근 commit-history 사례를 각 책 장에 배치
- Skill review checklist를 실제 template로 만들기
- vendor-neutral principle과 product syntax 표 분리

### 여전히 실측이 필요한 공백

- description variant routing 성능
- cross-host routing consistency
- root monolith vs scoped instruction
- reference depth effect
- model upgrade 전후 instruction removal effect

사용자가 실측을 보류한 현재 단계에서는 **추가 수집보다 taxonomy와 집필 구조로 통합하는 작업이 우선**이다.


## 비실측 통합 작업 완료

2026-09-30에 추가 수집 이후 우선순위로 잡았던 비실측 작업을 다음과 같이 진행했다.

### 완료

- **35개 공개 corpus 10축 재분류**
  - Trigger
  - Boundary
  - Preconditions
  - State / authority
  - Procedure
  - Side effect / permission
  - Evidence
  - Handoff
  - Freshness
  - Maintenance

  결과: [27-corpus-ten-axis-reclassification.md](27-corpus-ten-axis-reclassification.md)

- **bad → good composite refactor casebook**
  - root bloat
  - broad trigger
  - state ownership collision
  - cached CLI manual
  - verification side effect
  - prose-only safety gate
  - compatibility duplication
  - eval contamination
  - latest-version override
  - duplicated canonical tokens
  - generic process duplication
  - missing completion bound

  결과: [28-bad-good-refactoring-casebook.md](28-bad-good-refactoring-casebook.md)

- **structural validator 설계**
  - structural fact만 ERROR/WARNING/INFO로 검사
  - routing/output quality는 eval로 분리
  - semantic lint overreach 금지

  결과: [29-structural-validator-spec.md](29-structural-validator-spec.md)

- **실전 review checklist**
  - CLAUDE/AGENTS
  - path Rule
  - auto/manual Skill
  - high-side-effect Skill
  - validation/test Skill
  - fast-moving API/CLI Skill
  - Hook
  - instruction-change PR

  결과: [30-instruction-review-checklist.md](30-instruction-review-checklist.md)

### 남은 비실측 우선 작업

1. 책 각 장에 대표 real-world commit case를 배치
2. vendor-neutral principle과 provider-specific syntax를 표로 분리
3. Chapter 13 bad→good 사례를 하나의 end-to-end repository 구조로 확장
4. validator spec을 실제 예제 config + expected diagnostics fixture로 보강

실측이 재개되기 전까지는 위 네 작업의 가치가 추가 corpus 수집보다 높다.


## 2026-10-03 제품별 문서 조사 공백 재분류

다음 항목은 더 이상 "추가 링크 수집" 공백으로 보지 않는다.

- Claude Code prompt-audit: built-in `/doctor prompt-audit` / `/checkup prompt-audit`와 `/claude-api prompt-audit` 상세 조사 완료
- Cursor Rule validation: 공식 structural contract와 runtime visibility 확인, 공식 standalone CI validator는 현재 문서에서 확인하지 못함
- Codex skill-creator: `openai/skills`와 `openai/codex` 공식 source 차이까지 조사
- Gemini Skill best practices: discovery/precedence/silent-skip/validation helper까지 조사
- GitHub Copilot path-specific precedence: GitHub.com/IDE와 CLI의 merge/precedence semantics 차이 확인
- nested AGENTS 및 공개 repository corpus: 기존 16/21/27번 자료로 충분히 보강됨

상세:

- [31-product-edge-source-deep-dive.md](31-product-edge-source-deep-dive.md)

따라서 현재 큰 gap은 제품 문서 수집이 아니라 **controlled experiment**다.

우선순위는 기존과 동일하게 유지한다.

1. cross-host routing
2. root monolith vs scoped instruction
3. description boundary
4. model-upgrade instruction diet
5. reference depth
6. prose vs Hook enforcement

새 링크가 생겨도 위 실측 공백을 직접 줄이지 않으면 corpus 확장 우선순위를 낮춘다.


## 2026-10-03 Link-only source 전수 감사

01~31 연구 문서와 README의 URL을 다시 확인했다.

결론:

- 핵심 공식/학술/실제 저장소 source는 별도 분석 또는 후속 synthesis가 존재한다.
- public corpus의 raw URL 목록은 provenance index이며 12/16/27번 문서에서 후속 분석됐다.
- OpenAI PLANS.md는 현재 Archived이므로 current syntax evidence가 아니라 historical pattern으로 하향했다.
- current Codex AGENTS hierarchy, Gemini extension surface, Copilot Code Review semantics를 추가 보강했다.
- 상세: [32-link-only-source-audit.md](32-link-only-source-audit.md)

따라서 **source-depth 자체는 더 이상 주요 evidence gap이 아니다.**

남은 큰 gap은 controlled experiment다.


## 2026-10-03 Controlled experiment 구현 진행

source collection 이후 실제 experiment harness 구현으로 전환했다.

### Experiment A — Skill description routing

상태:

- fixture frozen
- host-neutral validator/scorer 구현
- Claude Code/Codex/Gemini Phase A runner 구현
- GitHub Actions gate PASS
- 실제 host smoke는 아직 미실행

### Experiment B — Root monolith vs nested scope

우선 S0/S1만 구현했다.

- S0: monolithic root AGENTS.md
- S1: root global + nested subsystem AGENTS.md
- 동일 workload SHA 자동 검증
- 12개 독립 calibration task
- deterministic grader
- Claude Code/Codex Phase B runner
- GitHub Actions gate PASS

의도적으로 아직 추가하지 않음:

- S2 path-scoped vendor rules
- S3 procedure-as-Skill

이 둘은 S0/S1 실제 calibration으로 fixture와 grader가 안정된 뒤 확장한다.

### 현재 evidence gap 상태

문서/링크 공백보다 다음 실제 run이 우선이다.

1. Claude Code routing smoke
2. Codex routing smoke
3. Gemini routing smoke
4. Claude Code S0/S1 scope smoke
5. Codex S0/S1 scope smoke
6. adapter가 안정되면 calibration 전체 실행

실제 host/model/version이 기록되지 않은 harness-only 결과를 책의 효과 수치로 사용하지 않는다.


## 2026-10-03 실제 host smoke 시작

로컬 환경의 Claude/Codex/Gemini에서 소규모 실행을 시작했다.

- Claude/Codex: feature·bugfix sentinel 확인. none은 아직 unobservable이다.
- Scope: sandbox CWD와 검증 기록 정리 때문에 발생한 오류를 수정하고 S0/S1 smoke를 재실행했다.
- Gemini: CLI option mismatch 수정 후 UNSUPPORTED_CLIENT 인증 거부를 확인했다.
- 모든 시도는 관측/fixture 검증이며 효과 크기 또는 full calibration 결과가 아니다.
- source/adapter가 바뀐 이전 smoke는 calibration에서 제외한다.
- 상세 결과: [SMOKE-REPORT-2026-10-03.md](../experiments/SMOKE-REPORT-2026-10-03.md).

다음 우선순위: none 관측 정책 확정, 깨끗한 host 환경에서 scope 전체 calibration, Gemini 지원 클라이언트/인증 경로 확인.
