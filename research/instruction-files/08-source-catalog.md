# 리서치 출처 카탈로그

기준일: 2026-09-30

## A. Anthropic / Claude Code

### How Claude remembers your project

URL:
https://code.claude.com/docs/en/memory

사용할 근거:

- CLAUDE.md의 scope
- user/project/local/managed instruction 위치
- CLAUDE.md는 context이며 hard enforcement가 아님
- 구체적이고 간결한 지침 권장
- CLAUDE.md 200줄 미만 목표
- path-scoped Rules
- Rule의 `paths` frontmatter
- user/project Rule 충돌 주의
- import는 context 절감 수단이 아님
- AGENTS.md 지원
- prompt audit 기능

### Extend Claude with skills

URL:
https://code.claude.com/docs/en/skills

사용할 근거:

- Skill discovery/loading semantics
- `description`과 `when_to_use`
- description listing 길이 제한
- unknown frontmatter field silent ignore 가능성
- malformed YAML 문제
- model invocation 설정
- Skill trigger debugging
- Skill eval workflow

### Skill authoring best practices

URL:
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

사용할 근거:

- context window는 공유 자원
- description = what + when
- progressive disclosure
- SKILL.md 500줄 미만 권장
- reference depth를 얕게
- 실제 사용 기반 iteration
- examples, scripts, validation

### Agent Skills overview

URL:
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

사용할 근거:

- metadata first
- body on activation
- resources on demand

### Steering Claude Code

URL:
https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more

발행:
2026-06-18

사용할 근거:

- CLAUDE.md, Rules, Skills, Hooks의 역할 분리
- context cost와 authority 차이
- procedure는 Skill
- deterministic action은 Hook

### Lessons from building Claude Code: How we use skills

URL:
https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills

발행:
2026-06-03

사용할 근거:

- Anthropic 내부 Skill 운영 경험
- Skill 구조/공유/운영에 대한 실무 관찰

### Effective context engineering for AI agents

URL:
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

발행:
2025-09-29

사용할 근거:

- context는 finite resource
- 최소 high-signal token
- brittle if/else prompt와 vague prompt 사이의 적절한 구체성
- 최소하지만 충분한 context

### Hooks reference

URL:
https://code.claude.com/docs/en/hooks

사용할 근거:

- event/matcher semantics
- unsupported matcher silent ignore
- command hook security
- full user permissions
- input sanitization
- path traversal
- sensitive files
- async deduplication 부재

## B. Agent Skills 공개 표준

### Specification

URL:
https://agentskills.io/specification

사용할 근거:

- portable SKILL.md directory structure
- required metadata
- scripts/references/assets
- vendor-specific field와 표준 field 구분

### Overview

URL:
https://agentskills.io/home

사용할 근거:

- discovery → activation → execution
- metadata와 body의 progressive disclosure

## C. OpenAI / Codex

### Rethinking skills and prompts for GPT-6 Astra

URL:
https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

발행:
2026-09-11

사용할 근거:

- description 과잉 문제
- 너무 많은 Skill과 context budget
- broad trigger의 오작동
- minimal router
- 과도한 recipe가 최신 모델을 제한할 수 있음
- AGENTS.md instruction debt
- task-conditioned document pointers
- model evolution에 따른 지침 감사

### Testing Agent Skills Systematically with Evals

URL:
https://developers.openai.com/blog/eval-skills

발행:
2026-01-22

사용할 근거:

- Skill을 prompt처럼 eval
- outcome/process/style/efficiency
- trigger positive/negative control
- trace/artifact 기반 평가
- regression dataset

### Model guidance / AGENTS.md hierarchy

URL:
https://developers.openai.com/api/docs/guides/latest-model

사용할 근거:

- AGENTS.md root-to-leaf injection
- directory-specific instruction model

### Using PLANS.md for multi-hour problem solving

URL:
https://developers.openai.com/cookbook/articles/codex_exec_plans

사용할 근거:

- AGENTS.md에서 세부 procedure 문서를 가리키는 사례
- standing instruction과 detailed execution document 분리

## D. Cursor

### Rules

URL:
https://cursor.com/docs/rules

사용할 근거:

- Project/User/Team Rules
- `.cursor/rules/*.mdc`
- Always / Intelligent / Specific Files / Manual
- description/globs/alwaysApply
- 500줄 미만 권장
- rule 분리
- reference 사용
- style guide 복사 대신 linter
- 반복 mistake에서 rule 추가
- nested AGENTS.md

### pstack repository

URL:
https://github.com/cursor/plugins/tree/main/pstack

분석 파일:

- `skills/poteto-mode/playbooks/authoring-a-skill.md`
- `skills/poteto-mode/playbooks/eval.md`
- `skills/tdd/SKILL.md`
- `skills/how/SKILL.md`
- `skills/why/SKILL.md`
- `skills/technical-writing/SKILL.md`
- `skills/principle-encode-lessons-in-structure/SKILL.md`
- `skills/setup-pstack/SKILL.md`

사용할 근거:

- prose 최소화
- cross-skill reference
- trigger/skip boundary
- structural enforcement
- blinded evaluation
- small global configuration rule

## E. Gemini CLI

### Manage context and memory

URL:
https://geminicli.com/docs/cli/tutorials/memory-management/

사용할 근거:

- global/project/subdirectory GEMINI.md
- focused/actionable rule
- negative constraint
- periodic cleanup

### Agent Skills

URL:
https://geminicli.com/docs/cli/skills/

사용할 근거:

- Agent Skills 표준 기반
- discovery/activation/resource loading
- user/workspace scope
- `.agents/skills/` interoperability alias

### Extension guidance

URL:
https://geminicli.com/docs/extensions/writing-extensions/

사용할 근거:

- GEMINI.md always-on context와 Skill on-demand의 구분
- Hook lifecycle 역할

## F. GitHub Copilot

### Custom instructions support

URL:
https://docs.github.com/en/copilot/reference/custom-instructions-support

사용할 근거:

- repository-wide
- path-specific
- AGENTS.md/CLAUDE.md/GEMINI.md 지원 범위

### Adding repository custom instructions

URL:
https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide

사용할 근거:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `applyTo`
- nearest AGENTS.md

### Code review customization comparison

URL:
https://docs.github.com/en/copilot/concepts/agents/code-review

사용할 근거:

- repo-wide instruction vs path instruction vs AGENTS.md vs Skills

## G. 학술/실증 자료

### From Anatomy to Smells: An Empirical Study of SKILL.md in Agent Skills

URL:
https://arxiv.org/abs/2607.01456

발행:
2026-07

핵심:
- 238개 Skill 정성 분석
- skill smell taxonomy
- 99% 이상 최소 하나 smell 보고

주의:
preprint.

### What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files

URL:
https://arxiv.org/abs/2608.08453

발행:
2026-08

핵심:
- 138,133 SKILL.md
- 91.8% 최소 하나 탐지 결함
- weak routing metadata, bloated/non-actionable body, poor resource organization

주의:
preprint.

### Signal or Noise? A Benchmark Study of Agent Skills in Web Development

URL:
https://arxiv.org/abs/2608.23067

발행:
2026-08

핵심:
- Skill 주입이 항상 성능 향상을 보장하지 않음
- context length/content 영향 분리 시도
- model별 차이
- anti-pattern rule의 유용성 관찰

주의:
특정 web development benchmark의 preprint. 수치 일반화 금지.

### GitSkills: A Dataset of Agent Skills on GitHub

URL:
https://arxiv.org/abs/2608.10906

발행:
2026-08

핵심:
- 수백만 SKILL.md occurrence 규모 dataset
- Skill을 소프트웨어 유지보수 아티팩트로 연구할 기반

주의:
preprint.

### Automating SKILL.md Generation for Computer-Using Agents via Interaction Trajectory Mining

URL:
https://arxiv.org/abs/2606.20363

발행:
2026-06

핵심:
- 실제 interaction trajectory에서 candidate skill을 추출하는 연구
- 실제 업무 trace 기반 Skill 생성/개선 아이디어

주의:
preprint.

### Lost in the Middle

URL:
https://arxiv.org/abs/2307.03172

핵심:
- 긴 context에서 중요한 정보의 위치에 따라 활용 성능 저하 가능
- "context가 크면 전부 넣어도 된다"는 가정의 배경 반례

## H. 추가 조사 상태

2026-10-03 재점검 결과, 링크 조사로 닫을 수 있는 항목은 상세 조사했다.

### 상세 조사 완료

- Claude Code prompt-audit
  - built-in `/doctor prompt-audit` / `/checkup prompt-audit`
  - `/claude-api prompt-audit`
  - model-relative audit, provenance, report + proposed diff contract 확인
- Cursor Rule lint/validation
  - 공식 `.mdc` structural contract와 runtime visibility 확인
  - 공식 standalone lint/JSON Schema/CI validator는 현재 문서에서 확인하지 못함
  - repository-owned structural validator 영역으로 분류
- Codex skill-creator 최신 원문
  - `openai/skills`와 `openai/codex` 공식 source를 대조
  - authoring guidance drift 자체를 canonical-source freshness 사례로 기록
- Gemini Skill best practices
  - discovery, progressive disclosure, degree of freedom, script ergonomics, silent-skip 조건, precedence 확인
- Copilot path-specific instruction precedence
  - GitHub.com/IDE의 precedence와 Copilot CLI의 merge semantics가 다름을 확인
- AGENTS.md nested semantics와 제품별 차이
  - 16/21번 문서와 Copilot surface 조사로 보강
- 실제 공개 repository instruction 사례
  - 35개 corpus 수집 및 10축 재분류 완료

상세 결과:

- [31-product-edge-source-deep-dive.md](31-product-edge-source-deep-dive.md)

### 문서 조사로 닫지 않는 항목

- 지침 파일 변경 전후 실제 coding task eval 데이터
  - 링크 수집 backlog가 아니라 자체 실측 backlog
  - [20-evidence-gap-matrix.md](20-evidence-gap-matrix.md)의 experiment gap으로 관리

### 전체 link-only source 감사 완료

- [32-link-only-source-audit.md](32-link-only-source-audit.md)에서 01~31 연구 문서와 README의 source를 전수 재검토
- 35개 corpus raw link, commit history link, 유명/vendor repository link는 후속 분석이 존재하므로 미조사로 보지 않음
- OpenAI `PLANS.md`, current Codex AGENTS hierarchy, Gemini extension guidance, Copilot Code Review를 추가 상세 조사
- 핵심 source 중 URL만 남아 있어 추가 조사가 필요한 항목은 현재 없음

### Historical / current 구분

- OpenAI `Using PLANS.md for multi-hour problem solving`
  - 현재 페이지가 Archived로 표시됨
  - 현행 Codex syntax 근거가 아니라 standing trigger → procedure → living task document 분리의 역사적/recipe 사례로만 사용

### 이후 source 추가 기준

새 링크는 다음 중 하나를 만족할 때만 우선 수집한다.

- 기존 taxonomy에 없는 authoring failure
- 현재 evidence gap을 직접 줄이는 실측 결과
- 공식 runtime semantics 변경
- instruction deletion/refactor의 새로운 before/after evidence


## I. 실제 변경 이력 / Instruction Debt 사례

### duthaho/skillhub — Description diet + invocation audit

URL:
https://github.com/duthaho/skillhub/commit/429242bd4f6c05c5695a25720f7684da1b9e01ad

사용할 근거:

- near-limit description 축소
- body detail과 trigger surface 분리
- manual-only 전환
- built-in collision validator
- description soft limit
- trigger eval surface가 실제 model-visible skill과 일치해야 함

### duthaho/skillhub — Trigger-first Skill 추가

URL:
https://github.com/duthaho/skillhub/commit/fd6a387ac86e4f71ff1885480d3fd9e324b727ad

사용할 근거:

- Skill 구현 전 trigger eval case 추가
- routing pair
- description을 TDD 대상으로 취급

### duthaho/skillhub — Validator CI gate

URL:
https://github.com/duthaho/skillhub/commit/f61a5d89ee4d5480da1b2acb888a1f167e000b0f

사용할 근거:

- structural validation을 PR gate로 승격
- semantic/LLM eval은 별도 유지
- registration drift를 CI에서 방지

### getsentry/skills — Runtime instruction 축소

URL:
https://github.com/getsentry/skills/commit/412f2368ee3ec90ce042826b57533f080d531aaf

사용할 근거:

- commit Skill 178 → 62 lines
- PR Writer 302 → 160 lines
- runtime에 실제 판단에 필요한 내용만 남김
- maintenance/spec/eval 책임 분리

### getsentry/skills — AXIS eval 도입

URL:
https://github.com/getsentry/skills/commit/5a64b36c62d042d3981b7937d9d6ca7bd1753b9a

사용할 근거:

- 실제 Codex harness 기반 Skill eval
- baseline/artifact/transcript
- small-inline, reference-backed, bad-output iteration case

### getsentry/skills — Skill-root-relative path 수정

URL:
https://github.com/getsentry/skills/commit/c81373583417504de2d3be1ae3d81977b11b2981

사용할 근거:

- provider path variable이 permission/runtime failure를 만든 사례
- portable relative path

### getsentry/skills — allowed-tools portability

URL:
https://github.com/getsentry/skills/commit/21af067ff3397fa35f5a0f22f05f6138d9e03307

사용할 근거:

- Claude에서는 허용되지만 공개 spec/다른 loader에서 깨지는 syntax
- Host-Tolerated Invalidity

### getsentry/skills — Runtime/SPEC 분리

URL:
https://github.com/getsentry/skills/commit/32fdf36273ac530120134ac484b3ab09717f3410

사용할 근거:

- runtime Skill 압축
- scope/maintenance contract를 SPEC으로 분리

### petekp/claude-code-setup — Opus 5.5 Skill audit

URL:
https://github.com/petekp/claude-code-setup/commit/0de2cbc2e9d2777743be990d6812b4d1820c3094

사용할 근거:

- model upgrade audit
- closing self-check 제거
- broad trigger wording 완화
- prompt style leakage
- 오래된 scaffolding 삭제

### c-reichert/flowstate — plugin guidance audit

URL:
https://github.com/c-reichert/flowstate/commit/756a19ae9fcc44cc44b49329dae57273b23be250

사용할 근거:

- stale metadata
- XML prompting guidance → Markdown
- 중복 invocation gate 제거
- trigger description 개선
- non-standard frontmatter 정리

### sfc-gh-eraigosa/dotfiles — Safety gate overcorrection

URL:
https://github.com/sfc-gh-eraigosa/dotfiles/commit/530d68bd0ee792884c85c58f5f528e39d354237d

사용할 근거:

- routine reversible action까지 막은 approval gate 제거
- 실제 publish 위험 경계만 유지
- alternate CLI bypass에 confirmation gate 추가

### sfc-gh-eraigosa/dotfiles — Hook semantic drift

URL:
https://github.com/sfc-gh-eraigosa/dotfiles/commit/fe438db541a1d53f1b6bd45c5e4c48fed2c60674

사용할 근거:

- Hook target resolution과 실제 tool semantics 불일치
- global flag 우회
- false-green test harness
- 실제 semantics와 Hook을 맞춘 regression test

### petekp/claude-code-setup — Skill infrastructure doctor

URL:
https://github.com/petekp/claude-code-setup/commit/aa756fd543657d2fb80ce20b34af50d7958dc3e5

사용할 근거:

- self-parent symlink loop
- content 외 instruction infrastructure health

## J. Nested scope 실제 사례

### sfc-gh-eraigosa/dotfiles

URLs:
- https://github.com/sfc-gh-eraigosa/dotfiles/blob/main/AGENTS.md
- https://github.com/sfc-gh-eraigosa/dotfiles/blob/main/sdk/AGENTS.md
- https://github.com/sfc-gh-eraigosa/dotfiles/blob/main/docker/AGENTS.md
- https://github.com/sfc-gh-eraigosa/dotfiles/blob/main/ai/skills/AGENTS.md

사용할 근거:

- root → subtree → module progressive scope
- Docker local invariant
- Skill authoring local policy
- AGENTS/CLAUDE symlink 기반 shared source

### radio4000/r4-svelte

URLs:
- https://github.com/radio4000/r4-svelte/blob/main/AGENTS.md
- https://github.com/radio4000/r4-svelte/blob/main/src/lib/components/AGENTS.md

사용할 근거:

- nearest nested instruction
- local gotcha만 담는 매우 작은 AGENTS
- 더 깊은 detail은 source header comment로 이동

### pulumi/customer-managed-workflow-agent

URLs:
- https://github.com/pulumi/customer-managed-workflow-agent/blob/main/AGENTS.md
- https://github.com/pulumi/customer-managed-workflow-agent/blob/main/kubernetes/AGENTS.md

사용할 근거:

- repository-wide restriction과 Kubernetes-specific convention 분리
- parent-child 일부 중복 사례

### BlackBeltTechnology/pi-agent-dashboard

URLs:
- https://github.com/BlackBeltTechnology/pi-agent-dashboard/blob/develop/AGENTS.md
- https://github.com/BlackBeltTechnology/pi-agent-dashboard/blob/develop/openspec/specs/dox-directory-foldering/spec.md

사용할 근거:

- AGENTS size/row lint
- byte cap과 row cap 분리
- parent roll-up 금지
- filesystem ownership과 instruction ownership 정렬
- sidecar progressive disclosure


## K. Cross-host Skill runtime / pilot adapter 공식 자료

### Claude Code Skills

URL:
https://code.claude.com/docs/en/skills

사용할 근거:

- description 기반 자동 invocation
- `/skill-name` 명시 호출
- `disable-model-invocation: true`
- manual-only일 때 description도 model context에서 제외
- Skill body lifecycle
- trigger와 output eval을 분리
- `claude plugin eval` 및 skill-creator eval
- nested project Skill loading

### OpenAI / Codex Skill Evals

URL:
https://developers.openai.com/blog/eval-skills

사용할 근거:

- name/description이 primary selection signal
- explicit / implicit / contextual / negative control
- `$skill` / `/skills` explicit activation
- `codex exec --json` JSONL trace
- deterministic grader + rubric grader

### OpenAI Skills Guide

URL:
https://developers.openai.com/api/docs/guides/tools-skills

사용할 근거:

- Skill discovery 시 name/description
- full SKILL.md on selection
- Agent Skills standard compatibility
- skill instruction priority/runtime notes

### Cursor Agent Skills

URL:
https://cursor.com/docs/skills

사용할 근거:

- automatic relevance-based Skill use
- `/skill-name` manual use
- `disable-model-invocation`
- Skill `paths` scope
- legacy `globs` fallback
- Claude/Codex Skill directory compatibility

### Cursor Hooks

URL:
https://cursor.com/docs/hooks

사용할 근거:

- agent lifecycle observability hooks
- 현재 조사에서는 Skill-specific auto-activation event를 별도 확인하지 못함

### Gemini CLI Agent Skills

URL:
https://geminicli.com/docs/cli/skills/

사용할 근거:

- discovery → activation → consent → injection → execution
- startup name/description metadata
- `activate_skill`
- enabled/disabled Skill management

### Gemini `activate_skill`

URL:
https://geminicli.com/docs/tools/activate-skill/

사용할 근거:

- tool argument로 Skill name이 노출됨
- tool은 agent 전용
- activation 관측 surface

### GitHub Copilot CLI Skill reference

URL:
https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference

사용할 근거:

- auto invocation
- `/SKILL-NAME`
- `disable-model-invocation`
- `user-invocable`
- `copilot skill list --json`
- Skill frontmatter limits

### GitHub Copilot Skills how-to

URL:
https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills

사용할 근거:

- prompt + description 기반 선택
- explicit invocation
- enable/disable/reload workflow


## L. 2026 Q3 유명 Skill 실제 규칙

조사 기간: 2026-07-01 ~ 2026-09-30

### Anthropic Skills

Repository:
https://github.com/anthropics/skills

Representative:
https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md

최근 변경 근거:
- 2026-08-18 academy-guide description 1,176 → 992 chars
- 2026-07-17 office skills 문서 trim
- 2026-09-29 claude-api eval/hillclimb guide 보강

사용할 근거:
- intent capture
- realistic eval prompts
- trigger description
- progressive disclosure
- imperative instructions
- eval/iterate loop

### Superpowers

Repository:
https://github.com/obra/superpowers

Representative:
- skills/using-superpowers/SKILL.md
- skills/test-driven-development/SKILL.md
- skills/verification-before-completion/SKILL.md
- skills/writing-skills/SKILL.md

최근 변경 근거:
- 2026-07-23 duplicated/social-proof/recap prose 대량 제거
- TDD rationale 축소 실험에서 pressure compliance 8/10 → 5/10
- rationale를 Common Rationalizations table에 다시 보존
- skill integration references를 point-of-use로 이동

사용할 근거:
- process skill priority
- pressure testing
- TDD for skill authoring
- fresh evidence before completion
- description trigger-only 철학
- prose deletion을 eval로 결정

### Matt Pocock Skills

Repository:
https://github.com/mattpocock/skills

Representative:
- skills/engineering/implement/SKILL.md
- skills/engineering/tdd/SKILL.md
- skills/engineering/code-review/SKILL.md
- skills/productivity/writing-for-agents/SKILL.md

최근 변경 근거:
- 2026-09-17 PR Skill을 action workflow에서 format reference로 축소
- 2026-09-24 stale merge-conflict Skill 삭제
- description/routing flow 정리

사용할 근거:
- manual-only implementation Skill
- pre-agreed test seams
- vertical slices
- standards/spec review separation
- context pointer
- information hierarchy
- completion criteria
- single source of truth

### Addy Osmani Agent Skills

Repository:
https://github.com/addyosmani/agent-skills

Representative:
- docs/skill-anatomy.md
- skills/using-agent-skills/SKILL.md
- skills/constraint-driven-development/SKILL.md
- skills/source-driven-development/SKILL.md

최근 변경 근거:
- 2026-09-23~26 Skill 500-line validator
- empty directory lint
- reference link validation
- artifact path drift checks
- must-not-fire plugin eval
- negated-trigger lint
- security-rule restoration after condensation

사용할 근거:
- what + when, no workflow summary
- rationalization/red flag/verification structure
- model-neutral procedures
- constraint → command/checker
- current official source verification
- Skill authoring rule → lint/CI/eval 승격

### Vercel Agent Skills

Repository:
https://github.com/vercel-labs/agent-skills

Representative:
- skills/react-best-practices/SKILL.md
- skills/react-view-transitions/SKILL.md
- skills/web-design-guidelines/SKILL.md

최근 변경 근거:
- 2026-07 React/Next source fact-check
- absolute rule scope 축소
- detail을 references로 이동
- Skill prose terse rewrite
- markdown cross-reference anchor 검증

사용할 근거:
- rule priority
- rule index + detail files
- live source
- source-backed corrections
- framework-specific stale knowledge 관리

### Planning with Files

Repository:
https://github.com/OthmanAdi/planning-with-files

Representative:
skills/planning-with-files/SKILL.md

최근 변경 근거:
- 2026-09 Cursor/Gemini hook schema 수정
- Python import isolation
- Stop hook noise 제거
- plan attestation target
- stale pointer handling

사용할 근거:
- persistent file memory
- 2-action rule
- read-before-decide
- update-after-act
- 3-strike failure protocol
- Hook-backed enforcement
- replay security boundary
- host adapter drift

### Ponytail

Repository:
https://github.com/DietrichGebert/ponytail

Representative:
skills/ponytail/SKILL.md

최근 변경 근거:
- 2026-07 ponytail marker scope 축소
- adapter/filter bugs 수정
- 2026-09 Cursor native hook 지원

사용할 근거:
- YAGNI ladder
- reuse/stdlib/native/dependency/minimal code order
- unrequested abstraction 금지
- smallest correct diff
- rule over-application 후 scope 축소

### ECC

Repository:
https://github.com/affaan-m/ECC

Representative:
- .agents/skills/tdd-workflow/SKILL.md
- .agents/skills/verification-loop/SKILL.md

최근 변경 근거:
- 2026-09 MCP health Hook matcher 축소
- failed step evidence propagation 차단
- destructive SQL detection hardening
- hook isolation
- Lean / Full / Auto profile

사용할 근거:
- TDD + coverage gates
- build/type/lint/test/security/diff verification
- Skill + Rule + Hook 결합
- deterministic enforcement scope


## M. 공식 Vendor Skill maintenance 사례

조사 기간: 2026-07-01 ~ 2026-09-30

### Firebase Agent Skills

Repository:
https://github.com/firebase/agent-skills

Representative:
- skills/firebase-security-rules-auditor/SKILL.md

최근 변경 근거:
- 2026-07-27 `97090866`: description을 약 69 tokens로 압축하면서 trigger coverage와 negative boundary 확장, activation eval 결과를 근거로 사용
- 2026-09-17 `e35a2d54`: Firestore/Security Rules의 객관적으로 잘못된 code/rule 수정

사용할 근거:
- concise + trigger-rich description
- explicit "Don't use for" boundary
- red-team checklist
- structured JSON output contract
- Skill content도 domain correctness regression을 가질 수 있음

### Expo Skills

Repository:
https://github.com/expo/skills

Representative:
- .claude/skills/expo-skill-eval/SKILL.md
- plugins/expo/skills/expo-upgrade/SKILL.md

최근 변경 근거:
- 2026-07-22 `cb916609`: canonical feedback block + validator/CI enforcement
- 2026-08-04 `5c8f62e0`: eval-candidate signal 수집
- 2026-08-13 `37397230`: Hermes V1 memory regression guidance
- 2026-09-02 `80090ccd`: 실제 feedback 기반 upgrade guidance 수정

사용할 근거:
- trigger accuracy / code quality / runtime screenshot 분리
- candidate Skill과 installed published Skill collision 방지
- evaluator allowed-tools 최소화
- version-specific upgrade reference
- production feedback → eval candidate → Skill maintenance

### Supabase Agent Skills

Repository:
https://github.com/supabase/agent-skills

Representative:
- skills/supabase-postgres-best-practices/SKILL.md

최근 변경 근거:
- 2026-07-30 `32912161`: performance에 치우친 description을 schema/migration/RLS/SQL authoring trigger까지 확장

사용할 근거:
- under-trigger correction
- prioritized rule categories
- thin entrypoint + detailed reference files

### Cloudflare Skills

Repository:
https://github.com/cloudflare/skills

Representative:
- skills/workers-best-practices/SKILL.md

2026-09-05 연속 refactor 근거:
- `79101242`: description을 distinct task trigger로 축소
- `f77752ea`: retrieval/validation을 affected task에 scope
- `defd1121`: generic review procedure 제거
- `42839d0d`: concrete Workers anti-pattern 복구
- `a31c2c41`: focused reference files로 분리
- `3cc7ee96`: description 단순화
- `8afcf8a2`: retrieval-first guidance 명시적으로 복구

사용할 근거:
- prefer retrieval over pre-training
- project configured version/compatibility date를 baseline으로 사용
- latest != applicable
- generic process 제거, domain-specific surprise 유지
- task-scoped validation

### Firecrawl CLI Skills

Repository:
https://github.com/firecrawl/cli

Representative:
- skills/firecrawl/SKILL.md
- firecrawl-* subskills

2026-08-20 핵심 변경:
- `41cc07c7`: router 329 → 141 lines, monitor/install/search detail을 canonical subskill/rule로 이동
- `980163d7`: cached CLI option tables를 `<command> --help` pointer로 교체, 중복 When-to-use 삭제, positive phrasing, 각 narrow Skill에 하나의 Done-when criterion
- `3ebf535a`: always-loaded description을 trigger-first로 압축
- `1d5be955`: forensics에서 빠진 neutral web-research trigger를 복구하고 429/auth terminal rules 추가

사용할 근거:
- thin router
- canonical CLI help
- cheapest-sufficient primitive escalation
- one observable completion bound
- compression 후 behavior regression을 다시 복구
- fetched content reuse / no redundant work

### Google Labs Stitch Skills

Repository:
https://github.com/google-labs-code/stitch-skills

Representative:
- plugins/stitch-design/skills/generate-design/SKILL.md

현재 구조 근거:
- design system 존재 시 generation prompt에서 color/font/theme token을 중복하지 않음
- generation은 layout/content/structure에 집중
- edit flow는 targeted adjustment
- related Skill로 책임 handoff

주의:
- 이번 3개월에 representative file 자체의 변경 이력은 확인하지 못했으므로 현행 구조 사례로만 사용

사용할 근거:
- canonical source ownership
- duplicated domain token 방지
- targeted edit before regeneration
- Skill-to-Skill responsibility separation

### Popularity candidate discovery snapshot

Repository:
https://github.com/LinklyAI/best-skills

Snapshot:
data/2026-09-29/

사용 범위:
- 최근 많이 설치되거나 널리 노출된 Skill 후보 발굴
- official vendor 후보 확장

주의:
- 제3자 집계이므로 Skill 품질의 객관적 ranking 근거로 사용하지 않음
- install/star 수를 authoring quality score로 해석하지 않음


## N. 추가 공식 조직 Skill과 governance 사례

조사 기간: 2026-07-01 ~ 2026-09-30

### GitHub Awesome Copilot

Repository:
https://github.com/github/awesome-copilot

Representative:
- .github/skills/code-review/SKILL.md

최근 변경 근거:
- 2026-09-23 `d7e4ad98`: repository-specific code-review quality Skill 추가

사용할 근거:
- deterministic checklist와 editorial judgment 분리
- AI-authored label 자체를 품질 defect로 사용하지 않음
- concrete/actionable evidence 기반 review
- review-policy instruction 변경을 security-sensitive governance change로 취급

주의:
- community contribution이 포함되는 공식 GitHub 조직 repository이므로 모든 Skill을 GitHub 내부 authored policy로 일반화하지 않음

### Stripe AI

Repository:
https://github.com/stripe/ai

Representative:
- skills/stripe-best-practices/SKILL.md
- skills/upgrade-stripe/SKILL.md

사용할 근거:
- live current-version lookup 우선
- dated bundled fallback snapshot
- fallback freshness interval 설명
- live verification 실패 시 latest라고 주장하지 않음
- explicit user target이 latest보다 우선할 수 있음
- stable → preview 임의 upgrade 금지

주의:
- Skill 파일은 자주 sync되므로 개별 sync commit보다 generated/current architecture를 근거로 사용

### MongoDB Agent Skills

Repository:
https://github.com/mongodb/agent-skills

Representative:
- skills/mongodb-connection/SKILL.md
- skills/mongodb-query-optimizer/SKILL.md

사용할 근거:
- Context Before Configuration
- context 없는 magic-number recommendation 금지
- performance evidence: indexes / explain / slow logs / Performance Advisor
- evidence에 맞춘 assertion strength
- user approval 없는 index mutation 금지
- explicit trigger boundary: optimization Skill은 general query authoring에 사용하지 않음

주의:
- 대표 path의 이번 3개월 직접 수정 commit은 확인하지 못했으므로 현행 구조 사례로만 사용

### HashiCorp Agent Skills

Repository:
https://github.com/hashicorp/agent-skills

Representative:
- plugins/terraform/skills/refactor-module/SKILL.md
- plugins/terraform/skills/run-acceptance-tests/SKILL.md

최근 변경 근거:
- 2026-08-10 `4451ceca`: token-efficient Terraform state access, provider config/test Skill, repository governance 통합

사용할 근거:
- acceptance test가 real infrastructure와 비용을 만들 수 있다는 operational gate
- test-account credential confirmation
- invocation-local secrets
- interrupted acceptance test cleanup/sweeper
- suspiciously passing test의 failure sensitivity 확인
- raw state 대신 documented stable interfaces 우선
- Skill proposal/update template에 source, owner, routing eval, operational-safety review 포함
