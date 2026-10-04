# 제품별 지침 파일 엣지 사례 추가 조사

기준일: 2026-10-03

## 1. 목적

기존 `08-source-catalog.md`에는 책 집필 전 추가 조사 가치가 있는 항목으로 다음이 남아 있었다.

- Claude Code `/doctor prompt-audit` 실제 동작
- Cursor Rule lint/validation
- Codex `skill-creator` 최신 원문
- Gemini CLI Skill best practices
- GitHub Copilot path-specific instruction precedence
- AGENTS.md nested semantics
- 실제 대규모 repository corpus
- instruction 변경 전후 coding-task eval

이 문서는 그중 **제품 공식 문서와 공식 저장소를 더 읽으면 닫을 수 있는 항목**을 정리한다.

이번 라운드의 원칙은 링크를 더 추가하는 것이 아니다.

> 제품이 실제로 무엇을 읽고, 무엇을 무시하고, 어떤 우선순위로 합치며, 무엇을 공식 validator로 보장하지 않는지까지 내려간다.

실측이 필요한 항목은 문서 조사로 닫지 않는다.

---

# 2. Claude Code prompt-audit: 두 entrypoint가 존재한다

## 2.1 Claude Code built-in command

Claude Code v2.1.283 release note에는 다음 기능이 추가됐다.

- `/doctor prompt-audit`
- alias: `/checkup prompt-audit`

대상:

- CLAUDE.md
- Skills
- Agents
- Commands

목적:

- older model에 맞춰 쌓인 prompting pattern 탐지
- stale path / stale command
- 서로 충돌하는 instruction file
- 현재 Claude Code에서 의미가 있는 thinking keyword는 오탐으로 삭제하지 않음

즉 기존 카탈로그의 “`/doctor prompt-audit` 실제 출력 사례”라는 메모 자체는 방향이 맞았다.

다만 이후 Anthropic은 별도의 `claude-api` Skill에도 prompt audit workflow를 넣었다.

Source:

- https://github.com/anthropics/claude-code/releases/tag/v2.1.283

## 2.2 `/claude-api prompt-audit`

Anthropic 공식 `anthropics/skills` 저장소의:

- `skills/claude-api/SKILL.md`
- `skills/claude-api/shared/prompt-audit.md`

에도 별도의 prompt-audit procedure가 있다.

이 workflow는 Claude API application prompt뿐 아니라 coding-agent configuration도 함께 본다.

예:

- system prompt
- tool description
- CLAUDE.md / AGENTS.md
- .claude/rules
- SKILL.md / references
- custom commands
- subagent definitions
- output styles
- request-building code
- few-shot examples

Source:

- https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/prompt-audit.md
- https://github.com/anthropics/skills/blob/main/skills/claude-api/SKILL.md

## 2.3 이 audit의 핵심은 “짧게 만들기”가 아니다

공식 prompt-audit 문서가 가장 강하게 경고하는 것은 indiscriminate deletion이다.

프레임은 다음이다.

> Every token earns its place.

하지만 이를:

> Make every prompt short.

로 바꾸지 않는다.

audit은 다음을 구분한다.

### 유지

- 작성자만 아는 context
- 프로젝트 고유 사실
- 실제 quality bar
- tool contract
- hard judgment
- 제약의 이유

### 제거/수정 후보

- 이미 모델 기본 동작인 일반론
- 과거 모델의 under-trigger를 보완하기 위한 압박 표현
- 과거 reasoning 한계를 보완한 scratchpad choreography
- obsolete request parameter
- project가 이미 벗어난 path/command
- 서로 충돌하는 instruction

이 차이는 이 책의 Instruction Diet 장에서 매우 중요하다.

“새 모델이 똑똑해졌으니 지침을 줄여라”가 아니라:

> **현재 모델·현재 저장소·다른 instruction과 더 이상 맞지 않는 구체적 줄만 제거한다.**

로 써야 한다.

## 2.4 audit procedure가 요구하는 evidence

`shared/prompt-audit.md`는 finding마다 다음을 요구한다.

- `file:line`
- matched pattern
- 왜 obsolete인지
- confidence

그리고 두 artifact를 만든다.

1. audit report
2. proposed diff

명시적으로 요청하지 않은 한 자동으로 edit를 적용하지 않는다.

또 git history가 있으면 blame을 이용해:

> 이 문장은 어느 실패를, 어느 모델에서 막기 위해 생겼는가.

를 추적한다.

이것은 instruction debt를 단순 문체 문제가 아니라 **provenance 문제**로 보는 사례다.

## 2.5 주요 anti-pattern group

공식 workflow가 보는 대표 범주는 다음과 같다.

### Pressure language

- CRITICAL
- MUST
- NEVER
- ALWAYS
- “if in doubt, use X”
- “be maximally thorough”
- “do not be lazy”

문제는 강한 단어 자체가 아니라, older model에서 underweight되던 규칙을 current model이 literal하게 과적용할 수 있다는 점이다.

### API feature로 대체된 scaffold

- think step by step
- scratchpad tag
- fixed planning ritual
- prose로 thinking depth 조절
- JSON forcing stack
- stale stop-sequence / retry parsing
- retired request parameter

### Judgment task의 고정 choreography

순서가 실제 invariant가 아닌데도 STEP 1~N을 강제하면 current model의 더 나은 planning을 막을 수 있다.

### stale examples

과거 model behavior를 고정한 few-shot example은 최신 모델에도 그 길이와 사고 패턴을 복제시킬 수 있다.

## 2.6 Anthropic이 공개한 측정

Anthropic의 2026-09 cost/performance 글에서는 older-model anti-pattern을 심은 여섯 prompt를:

- Opus 4.8
- Opus 5.5 그대로
- Opus 5.5 + prompt-audit

으로 비교했다.

공식 보고에서는 model migration 자체의 비용 감소에 더해 prompt-audit 후 추가 비용 감소와 accuracy 개선이 관찰됐다.

이 수치는 특정 customer-support benchmark에 대한 Anthropic의 사례다.

따라서 책에서는 universal effect size로 쓰지 않고:

> model upgrade 후 instruction audit가 실제 cost/behavior에 영향을 줄 수 있음을 보여주는 vendor experiment

로 사용한다.

Source:

- https://claude.com/blog/reducing-cost-and-improving-performance-with-claude-platform

## 2.7 책에 추가할 규칙

**Prompt Audit Rule**

모델 업그레이드 후 지침을 줄이는 것이 아니라 다음 순서로 audit한다.

1. target model을 정한다.
2. instruction surface를 inventory한다.
3. provenance를 본다.
4. obsolete pattern을 식별한다.
5. project-specific context와 old workaround를 구분한다.
6. report와 diff를 분리한다.
7. clean surface면 아무것도 바꾸지 않는다.

---

# 3. Cursor Rules: 공식 lint command보다 structural contract가 먼저다

## 3.1 현재 공식 Rule contract

Cursor 공식 Rules 문서 기준 Project Rule은:

- `.cursor/rules/**/*.mdc`
- YAML frontmatter
- Markdown body

구조다.

현재 공식 field:

- `description`
- `globs`
- `alwaysApply`

Rule type은 실질적으로 이 metadata 조합으로 결정된다.

- Always Apply
- Auto Attached
- Agent Requested
- Manual

Source:

- https://cursor.com/docs/rules
- https://prod.cursor.com/docs/reference/plugins

## 3.2 확실하게 검증할 수 있는 structural fact

공식 문서에서 확인 가능한 deterministic condition은 다음이다.

### Extension

Project Rule은 `.mdc`여야 한다.

`.cursor/rules/api-guidelines.md`처럼 plain `.md`를 넣으면 Rule system이 무시한다.

plain Markdown이 필요하면 AGENTS.md를 사용한다.

### Agent Requested

`alwaysApply: false`이고 semantic selection을 기대한다면 description이 중요하다.

공식 FAQ도 Agent Requested가 동작하지 않을 때 description 존재 여부를 확인하라고 한다.

### Auto Attached

glob이 실제 referenced file과 맞아야 한다.

rule이 안 붙는 대표 원인은 glob mismatch다.

### Visibility

Cursor Settings > Rules에서 rule 목록과 상태를 볼 수 있고, applied rule은 Agent sidebar에서 확인할 수 있다.

이것은 runtime observation surface이지 schema validator는 아니다.

## 3.3 찾지 못한 것: 공식 standalone lint/schema validator

2026-10-03 기준 공식 Cursor Rules 문서와 plugin reference에서 다음과 같은 제품 내장 기능은 확인하지 못했다.

- `cursor rules lint`
- `cursor rules validate`
- 공개 JSON Schema
- 공식 CI용 `.mdc` validator command

즉 “Cursor rule lint/validation 방법”을 공식 제품 기능으로 찾으려던 기존 질문은 조금 잘못 잡혀 있었다.

현재 공식 표면은:

- file extension
- frontmatter field
- rule type
- glob matching
- Settings/status
- runtime application

을 문서화한다.

**static lint는 repository가 별도로 소유해야 하는 영역**으로 보는 것이 안전하다.

이 결론은 “Cursor가 validation을 전혀 하지 않는다”는 뜻이 아니다.

IDE가 파일을 parsing하고 status를 보여줄 수 있지만, 그 내부 validation을 CI contract로 의존할 공개 interface가 현재 공식 문서에는 없다는 뜻이다.

## 3.4 책의 validator 설계와 연결

따라서 `29-structural-validator-spec.md`에서 Cursor Rule에 대해 deterministic하게 검사할 수 있는 항목은:

- `.mdc` extension
- YAML parse
- known frontmatter fields
- `alwaysApply` boolean
- glob syntax
- Agent Requested에 description 부재
- referenced local file 존재 여부
- duplicate/overlapping obvious path rule

정도다.

반면:

- description이 semantic하게 좋은가
- 실제 필요한 prompt에서 Agent Requested가 선택되는가
- nested rule collision이 실제 behavior를 망치는가

는 lint가 아니라 eval이다.

## 3.5 새 원칙

> **Product recognizes it**와 **repository can validate it**는 다른 문제다.

Cursor가 Rule을 읽는다고 해서 팀이 CI에서 그 Rule의 구조와 drift를 검사할 수 있는 공식 validator가 자동으로 생기는 것은 아니다.

---

# 4. Codex skill-creator: “최신 원문”도 하나가 아니다

## 4.1 공식 source가 둘 이상 존재한다

2026-10-03 현재 최소 두 공식 저장소에서 skill-creator를 확인할 수 있다.

### openai/skills

`skills/.system/skill-creator/SKILL.md`

Source:

https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md

### openai/codex

`codex-rs/skills/src/assets/samples/skill-creator/SKILL.md`

Source:

https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md

두 파일은 같은 철학을 공유하지만 완전히 동일하지 않다.

따라서 “Codex skill-creator 최신 원문”을 단일 파일로 고정해 책의 영구 canonical source처럼 취급하면 안 된다.

## 4.2 공통된 핵심

두 version 모두 다음을 강하게 지지한다.

### Assume Codex is already capable

generic explanation을 넣지 않는다.

다른 Codex instance가 실제 task에서 판단을 바꾸는 정보만 남긴다.

### Progressive disclosure

- name + description
- SKILL.md body
- resources

로 나눈다.

### Description is routing

description에는:

- 무엇을 하는지
- 언제 쓰는지

가 들어가야 한다.

### Deterministic logic -> scripts

반복 계산/변환/검증은 자연어 재작성보다 script를 쓴다.

### Structural validation

`quick_validate.py`로:

- frontmatter
- naming
- scaffold placeholder

같은 structural issue를 먼저 잡는다.

## 4.3 openai/codex sample에서 더 강해진 부분

현재 Codex repository sample은 이전의 “Concise is Key”보다 더 구체적으로 다음을 강조한다.

### Preserve user scope

Skill이:

- 사용자가 선택한 product를 바꾸거나
- assignment를 넓히거나
- unrelated configuration을 수정하거나
- 추가 external action 권한을 암묵적으로 얻으면 안 된다.

### Match specificity to risk

작업이 fragile하지 않으면 fixed sequence를 강제하지 않는다.

반대로 correctness/safety/permission이 걸린 작업은:

- detailed steps
- deterministic scripts
- absolute constraints

를 사용할 수 있다.

### Cheap and precise discovery

description에 exhaustive capability list와 catch-all을 넣지 않는다.

### Explicit-only invocation은 UI metadata policy

현재 sample은 `agents/openai.yaml`에서:

```yaml
policy:
  allow_implicit_invocation: false
```

를 explicit-only control로 설명한다.

이것은 portable Agent Skills core가 아니라 OpenAI-specific interface policy다.

### Independent forward-testing

복잡하거나 위험한 Skill은 independent subagent를 이용한 forward test를 고려한다.

중요한 점은 evaluator에게:

- intended answer
- suspected bug
- proposed fix

를 노출하지 않는 것이다.

이는 기존 책의 blinded eval과 직접 연결된다.

## 4.4 source drift 자체가 사례다

공식 `openai/skills`와 `openai/codex`의 skill-creator는 일부 세부 guidance와 metadata 처리에서 차이가 있다.

또 OpenAI의 다른 최신 문서는 reusable skill 경로 예시로 `.agents/skills`를 사용한다.

예:

- Claude Agent SDK -> OpenAI Agents SDK migration guide

반면 일부 bundled/sample guidance에는 `$CODEX_HOME/skills` 또는 `~/.codex/skills`가 여전히 등장한다.

이 차이는 “어느 쪽이 무조건 틀렸다”는 결론보다 더 중요한 사례를 제공한다.

> **official source도 runtime·repository·migration 시점에 따라 drift할 수 있으므로 현재 host의 discovery contract를 다시 확인해야 한다.**

Book에서는 이를 **Canonical-source freshness** 사례로 사용한다.

Sources:

- https://developers.openai.com/cookbook/examples/agents_sdk/migrate-from-claude-agent-sdk/readme
- https://developers.openai.com/api/docs/guides/tools-skills

## 4.5 책의 규칙

Codex-specific syntax를 설명할 때는 세 층을 분리한다.

1. Agent Skills portable core
2. current Codex runtime behavior
3. current Codex skill-creator authoring guidance

skill-creator 자체도 implementation artifact이므로 “공식이니까 영구 불변”으로 취급하지 않는다.

---

# 5. Gemini CLI Skill best practices: authoring guidance까지 상세 조사 완료

## 5.1 Description이 activation 전 유일한 signal이다

Gemini 공식 best-practices는 description을 가장 중요한 부분으로 명시한다.

activation 전 model이 보는 것은 name + description이다.

따라서 description은:

- specific keyword
- 실제 trigger
- adjacent Skill과의 overlap 방지

를 포함해야 한다.

Source:

- https://geminicli.com/docs/cli/skills-best-practices/

## 5.2 Progressive disclosure 수치

공식 문서는 세 수준을 설명한다.

1. metadata: always in context, 약 100 words
2. SKILL.md body: activation 후, 5k words 미만 권장
3. bundled resources: 필요할 때

여기서 중요한 것은 숫자보다 loading semantics다.

긴 schema/example을 `references/`로 내리는 이유는 파일 정리가 아니라 **activation 이후에도 조건부 context를 유지하기 위해서**다.

## 5.3 Degrees of freedom

Gemini는 Skill instruction의 구체성을 task fragility에 맞추라고 한다.

### High freedom

여러 접근이 합리적이고 context-dependent.

자연어 principle 중심.

### Medium freedom

preferred pattern은 있으나 variation 허용.

pseudocode / parameterized script.

### Low freedom

fragile sequence, error-prone operation.

specific script, 좁은 parameter.

이는 Codex skill-creator와 거의 동일한 방향이다.

제품이 달라도 다음 원칙이 반복된다.

> **instruction specificity should track operational risk.**

## 5.4 Script ergonomics

Gemini best-practices는 deterministic task를 script로 옮기는 것뿐 아니라 script output 자체도 LLM-friendly하게 만들라고 한다.

예:

- verbose traceback 억제
- clear success/failure
- concise stdout

즉 “script로 옮겼다”가 끝이 아니다.

script도 agent가 소비하는 interface다.

## 5.5 실제 discovery failure 조건

Getting Started 문서에는 실전 debugging 조건도 비교적 명확하다.

workspace Skill이 안 보일 때:

- workspace trust 확인
- discovery depth 확인
- 파일명이 정확히 `SKILL.md`인지 확인
- frontmatter가 파일의 첫 내용인지 확인
- name/description 필수
- malformed frontmatter는 Skill이 silently skipped될 수 있음

이 부분은 structural validator chapter에 쓸 수 있다.

Source:

- https://geminicli.com/docs/cli/tutorials/skills-getting-started/

## 5.6 Discovery precedence

Gemini의 현재 tier:

1. Built-in
2. Extension
3. User
4. Workspace

같은 name이면 higher-precedence location이 이긴다.

같은 user/workspace tier 안에서는:

- `.agents/skills/`
- `.gemini/skills/`

중 `.agents/skills/` alias가 더 높은 precedence를 갖는다.

이는 cross-host portable path를 도입할 때 collision test가 필요한 이유다.

## 5.7 Built-in skill-creator

Gemini도 built-in `skill-creator`를 제공한다.

공식 Creating Skills 문서는 내부 helper로:

- `init_skill.cjs`
- `validate_skill.cjs`
- `package_skill.cjs`

를 설명한다.

여기서도 structural validation과 semantic quality는 분리된다.

Source:

- https://geminicli.com/docs/cli/creating-skills/

## 5.8 책의 규칙

Gemini 조사에서 추가할 내용은 새로운 철학보다 **구체적 failure mode**다.

- wrong filename -> undiscovered
- malformed frontmatter -> silent skip
- untrusted workspace -> workspace Skill 미로드
- duplicate name -> precedence로 shadowing

따라서 Skill review checklist에는 “내용이 좋은가” 전에:

> 이 host에서 실제로 discoverable한가.

를 넣어야 한다.

---

# 6. GitHub Copilot: precedence는 surface마다 다르다

이 항목이 이번 조사에서 가장 중요한 edge case다.

## 6.1 GitHub.com / repository customization의 order

현재 GitHub Docs의 customization 개념 문서는 다음 priority를 설명한다.

상위:

1. Personal instructions

Repository 내부:

1. path-specific `.github/instructions/**/*.instructions.md`
2. repository-wide `.github/copilot-instructions.md`
3. agent instruction, 예: `AGENTS.md`

그 아래:

- organization instruction

GitHub은 conflict를 피하라고 권장한다.

Source:

- https://docs.github.com/en/copilot/concepts/prompting/response-customization

## 6.2 path-specific + repository-wide는 함께 들어간다

GitHub.com instruction 문서는 target file이 `applyTo`와 match하고 repository-wide instruction도 있으면 **둘 다 사용**한다고 명시한다.

즉 path-specific file은 repository-wide를 “대체하는 파일”이 아니다.

scope가 좁은 추가 instruction이다.

Source:

- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions

## 6.3 AGENTS.md는 nearest rule

GitHub.com/IDE 문서는 repository 안에 여러 AGENTS.md가 있을 때 현재 작업과 가장 가까운 AGENTS.md가 precedence를 갖는다고 설명한다.

다만 surface support가 동일하지 않다.

일부 IDE에서는 workspace root 밖 AGENTS.md support가 설정에 따라 달라질 수 있다.

따라서 “GitHub Copilot은 항상 모든 nested AGENTS를 같은 방식으로 읽는다”라고 쓰면 안 된다.

## 6.4 Copilot CLI는 다르다

Copilot CLI 문서는 applicable user/repository instruction을 **combine**한다고 설명하면서:

> general precedence order between these files is not defined.

라고 명시한다.

즉 CLI에서는 다음을 단순한 override chain으로 모델링하면 안 된다.

- repo-wide
- AGENTS
- CLAUDE
- GEMINI
- modular instructions

path-specific instruction은 `applyTo`가 current working file과 match할 때만 포함된다.

또 `/instructions`로 현재 discovered instruction을 보고 individual file을 disable할 수 있다.

Source:

- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions

## 6.5 Copilot CLI의 추가 nuance

현재 CLI는 다음도 instruction source로 읽을 수 있다.

- `.claude/rules/**/*.md`

그리고 path scope에는:

- `paths`
- `applyTo`

를 사용할 수 있다고 command reference가 설명한다.

즉 cross-vendor compatibility가 넓어졌지만 그만큼 **한 저장소에 여러 instruction surface가 동시에 보일 가능성**도 커진다.

Source:

- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference

## 6.6 file reference 지원도 surface마다 다르다

Copilot CLI 문서 기준:

다음에서는 `@relative/path` reference를 읽는다.

- `.github/copilot-instructions.md`
- AGENTS.md
- CLAUDE.md

하지만:

- GEMINI.md
- `*.instructions.md`

에서는 같은 방식의 reference expansion을 하지 않는다.

따라서 동일 내용을 여러 file format으로 mechanical conversion하면 의미가 보존되지 않을 수 있다.

## 6.7 책의 규칙

**Surface-specific precedence**

> 같은 vendor 안에서도 instruction precedence를 제품 전체의 단일 규칙으로 일반화하지 않는다.

최소한 다음을 따로 기록한다.

- GitHub.com
- IDE integration
- cloud agent/code review
- Copilot CLI

portable instruction guide에서 “Copilot precedence”라는 한 줄 표보다 **surface matrix**가 더 정확하다.

---

# 7. 기존 H 섹션 항목 재평가

## 7.1 Claude Code `/doctor prompt-audit`

상태: **상세 조사 완료**

추가로 `/claude-api prompt-audit`와 built-in `/doctor prompt-audit`를 구분했다.

## 7.2 Cursor rule lint/validation

상태: **조사 완료, 결론 수정**

공식 standalone lint/JSON schema를 찾은 것이 아니라:

- 공식 structural contract
- runtime visibility
- 공식 CI validator 부재

를 확인했다.

자체 validator가 필요한 영역이다.

## 7.3 Codex skill-creator 최신 원문

상태: **상세 조사 완료**

오히려 official source가 둘 이상이고 drift가 있음을 발견했다.

## 7.4 Gemini Skill best practices

상태: **상세 조사 완료**

authoring principle뿐 아니라 discovery failure와 precedence까지 보강했다.

## 7.5 Copilot path-specific precedence

상태: **상세 조사 완료**

가장 중요한 결과는 GitHub.com/IDE와 CLI가 동일 precedence model이 아니라는 점이다.

## 7.6 AGENTS.md nested semantics

상태: **기존 조사로 이미 완료**

주요 근거:

- `16-nested-scope-case-studies.md`
- `21-cross-host-skill-pilot-adapters.md`
- 이번 Copilot surface 조사

## 7.7 실제 대규모 repository corpus

상태: **완료**

`11-public-instruction-corpus.md`에서 35개 표본을 확보했고 이후 10축으로 재분류했다.

## 7.8 instruction 변경 전후 실제 coding-task eval

상태: **미완료 — 문서 조사 문제가 아님**

이 항목은 더 이상 “자료 수집” backlog에 두지 않는다.

자체 실측 backlog다.

---

# 8. 아직 링크 수준이거나 추가 가치가 낮은 자료

이번 정리 후 남은 “링크만 있고 독립 심층 문서가 없는” 항목 중 책의 핵심 근거에 영향을 주는 것은 거의 없다.

대표적으로 OpenAI의:

- `Using PLANS.md for multi-hour problem solving`

은 카탈로그에서 standing instruction과 execution document 분리 사례로만 사용하고 있다.

하지만 이 책의 핵심 주장:

- root instruction과 task-specific procedure 분리

는 이미:

- Skills
- scoped Rules
- public repository case
- vendor guidance

로 충분히 지지된다.

따라서 PLANS.md를 독립 심층 조사하는 우선순위는 낮다.

---

# 9. 이번 조사에서 새로 강화된 책의 원칙

## P1. Audit는 shortening이 아니다

Instruction Diet은 length reduction이 아니라 target-model/project alignment다.

## P2. Discovery validity precedes semantic quality

Skill/Rule이 구조적으로 discoverable하지 않으면 좋은 prose도 의미가 없다.

## P3. Official source도 하나가 아닐 수 있다

runtime, sample, docs, system Skill이 서로 다른 시점의 guidance를 가질 수 있다.

## P4. Product support와 validation interface를 분리한다

제품이 format을 읽는 것과 CI에서 검사할 공식 validator가 있는 것은 다른 문제다.

## P5. Same vendor != same precedence

GitHub Copilot처럼 product surface가 달라지면 instruction merge/precedence semantics도 달라질 수 있다.

## P6. Instruction source 자체도 freshness audit 대상이다

공식 Skill authoring guide조차 host runtime과 drift할 수 있다.

따라서 책에서 특정 path/syntax를 설명할 때:

> 기준일 + surface + source

를 함께 기록한다.

---

# 10. 남은 실제 공백

링크 조사 관점에서 이번 5개 항목은 닫아도 된다.

남은 큰 공백은 `20-evidence-gap-matrix.md`의 실측 문제다.

1. same Skill metadata cross-host routing
2. monolithic root vs scoped instruction
3. description boundary routing effect
4. model upgrade instruction diet
5. reference depth
6. prose vs Hook controlled comparison

따라서 다음 연구는 링크 수집보다 experiment가 우선이다.

---

# 11. 주요 출처

## Anthropic

- Claude Code v2.1.283 release
  - https://github.com/anthropics/claude-code/releases/tag/v2.1.283
- Prompt Audit source
  - https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/prompt-audit.md
- Claude API Skill
  - https://github.com/anthropics/skills/blob/main/skills/claude-api/SKILL.md
- Reducing cost and improving performance with Claude Platform
  - https://claude.com/blog/reducing-cost-and-improving-performance-with-claude-platform

## Cursor

- Rules
  - https://cursor.com/docs/rules
- Plugins reference
  - https://prod.cursor.com/docs/reference/plugins

## OpenAI

- openai/skills Skill Creator
  - https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md
- openai/codex bundled Skill Creator
  - https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md
- Skills API guide
  - https://developers.openai.com/api/docs/guides/tools-skills
- Claude Agent SDK migration guide
  - https://developers.openai.com/cookbook/examples/agents_sdk/migrate-from-claude-agent-sdk/readme

## Gemini CLI

- Agent Skill best practices
  - https://geminicli.com/docs/cli/skills-best-practices/
- Agent Skills
  - https://geminicli.com/docs/cli/skills/
- Creating Agent Skills
  - https://geminicli.com/docs/cli/creating-skills/
- Getting started
  - https://geminicli.com/docs/cli/tutorials/skills-getting-started/

## GitHub Copilot

- About customizing Copilot responses
  - https://docs.github.com/en/copilot/concepts/prompting/response-customization
- Repository instructions
  - https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- Copilot CLI custom instructions
  - https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
- Copilot CLI command reference
  - https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
