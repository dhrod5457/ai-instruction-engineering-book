# Trigger Routing Pilot Runbook v0.1

기준일: 2026-09-30

이 runbook은 `research/experiments/trigger-routing/v0.1/`의 frozen fixture를 실제 host에서 실행하기 위한 절차다.

## 1. 실험 대상

Variant:

- A0 Broad
- A1 Concise
- A1L Length Control
- A2 Boundary-Aware

Calibration prompt:

- 20 cases

최종 benchmark가 아니다.

---

# 1.1 공통 harness preflight

host 실행 전에 아래 두 명령이 통과해야 한다.

```bash
cd research/experiments/trigger-routing/v0.1
python3 harness.py validate
python3 -m unittest -v test_harness.py test_phase_a_runner.py
```

`validate`는 다음을 확인한다.

- 4개 description variant 존재
- 각 variant에 feature/bugfix/refactor/review description 존재
- calibration 20개와 `split.json` calibration이 동일
- 전체 split ID가 80개이고 중복 없음
- `split.json`이 고정한 corpus/pilot/variant Git blob SHA와 현재 파일이 동일
- `results-template.csv` header가 scorer contract와 동일

실험 fixture가 바뀌었는데 blob SHA가 달라지면 기존 결과와 섞지 않는다.

# 1.2 Materialize

`harness.py materialize`는 네 Skill의 body를 완전히 동일하게 유지하고 description만 선택한 variant로 바꾼다.

예:

```bash
python3 harness.py materialize \
  --variant A2_boundary_aware \
  --host claude \
  --output /tmp/trigger-routing-a2-claude
```

기본 project Skill root:

| Host | Path |
| --- | --- |
| generic | `.agents/skills` |
| Claude Code | `.claude/skills` |
| Codex | `.codex/skills` |
| Cursor | `.cursor/skills` |
| Gemini CLI | `.gemini/skills` |
| GitHub Copilot CLI | `.github/skills` |

실행 시점의 host 문서가 다른 경로를 요구하면:

```bash
--skills-dir <relative/path>
```

로 override하고 결과 notes에 그 경로를 기록한다.

# 1.3 Score

20-case 1회 calibration 결과를 `results-template.csv` schema로 저장한다.

```bash
python3 harness.py score \
  --results results.csv \
  --json-out score.json \
  --md-out score.md
```

현재 scorer가 계산하는 항목:

- observable rate
- observable run 기준 accuracy
- macro-F1
- none abstention accuracy
- none false-positive rate
- routing-pair collision error rate
- 반복 실행 시 run consistency
- confusion matrix
- label별 precision/recall/F1

observable하지 않은 run을 억지로 실패나 none으로 바꾸지 않는다.

---

# 1.4 Phase A runner

Claude Code, Codex, Gemini CLI는 공통 runner로 calibration을 실행할 수 있다.

먼저 설치/버전만 확인한다.

```bash
python3 phase_a_runner.py --host claude --out /tmp/phase-a-claude --preflight-only
python3 phase_a_runner.py --host codex --out /tmp/phase-a-codex --preflight-only
python3 phase_a_runner.py --host gemini --out /tmp/phase-a-gemini --preflight-only
```

한 host에서 4개 variant × 20 calibration case를 1회 실행:

```bash
python3 phase_a_runner.py \
  --host claude \
  --model <exact-model-id> \
  --runs 1 \
  --out runs/claude-calibration
```

smoke case만 먼저 실행하려면 `--case`를 반복한다.

```bash
python3 phase_a_runner.py \
  --host gemini \
  --model <exact-model-id> \
  --variant A1_concise \
  --case EP-F01 \
  --case EP-B01 \
  --case NO-04 \
  --runs 1 \
  --out runs/gemini-smoke
```

runner는 각 prompt마다 별도 workspace를 materialize하고 새 CLI process를 시작한다.

안전 경계:

- 실제 사용자 repository를 실험 대상으로 사용하지 않음
- synthetic 빈 git workspace만 사용
- Claude는 `--permission-mode plan`
- Gemini는 `--approval-mode plan`
- Codex는 `--full-auto`를 사용하지 않음
- Skill body 자체도 파일 수정/명령 실행을 금지
- stdout/stderr/command/result row를 raw artifact로 보존

관측 규칙:

- Gemini: `activate_skill(name)` event 우선
- 공통 fallback: 정확한 `SKILL_ACTIVATED:<name>` sentinel
- Claude/Codex에서 sentinel도 native event도 없으면 `unobservable`
- Gemini는 정상 종료된 complete stream에 `activate_skill`이 없으면 `none`을 관측 가능 상태로 기록

`--model`에는 가능하면 alias가 아니라 정확한 model ID를 사용한다.

현재 runner는 host CLI 인증을 설정하거나 설치하지 않는다. 사용자의 기존 로그인/credential을 그대로 사용한다.

---

# 2. Routing-only Skill Body

이 실험은 Skill이 선택된 뒤 실제 코딩 성능을 측정하지 않는다.

오직:

> 어떤 description에서 어떤 Skill이 선택되는가

만 본다.

따라서 네 Skill body는 모두 동일한 구조로 최소화한다.

예: `feature/SKILL.md`

```markdown
---
name: feature
description: <VARIANT의 feature description>
---

# Routing evaluation sentinel

This is a routing-only evaluation skill.

Do not modify files, run commands, or perform the requested task.

If this skill is activated, respond with exactly:

SKILL_ACTIVATED:feature
```

다른 Skill도 marker 이름만 다르다.

- `SKILL_ACTIVATED:bugfix`
- `SKILL_ACTIVATED:refactor`
- `SKILL_ACTIVATED:review`

## 왜 body를 이렇게 만드는가

장점:

- body가 선택 후에만 로드되는 host에서는 routing decision을 거의 오염시키지 않는다.
- 실제 코드 수정/도구 호출을 없애 pilot 비용을 줄인다.
- machine-readable marker를 제공한다.
- host-native trace가 부족할 때 fallback activation evidence가 된다.

한계:

- marker는 model compliance에 의존한다.
- marker가 없다고 Skill이 절대 활성화되지 않았다고 단정할 수 없는 host가 있을 수 있다.
- 따라서 host-native activation evidence가 있으면 marker보다 우선한다.

---

# 3. 판정 우선순위

각 run의 `actual`은 아래 순서로 판정한다.

## Level 1 — Native activation event

예:

- Gemini `activate_skill(name)`
- host가 제공하는 Skill invocation event

가장 신뢰한다.

## Level 2 — Structured trace

예:

- Codex JSONL에서 Skill load/read/invocation을 확인할 수 있는 경우
- Claude eval/transcript에서 Skill invocation을 직접 확인

## Level 3 — Sentinel

최종 출력:

```text
SKILL_ACTIVATED:<name>
```

이 정확히 나오면 해당 Skill activation의 fallback evidence로 사용.

## Level 4 — Unobservable

다음만 있을 경우 성공/실패로 억지 판정하지 않는다.

- Skill 스타일과 비슷한 답변
- "이건 bugfix 같네요" 같은 자연어
- model self-report
- body와 유사한 표현

`actual=unobservable`로 기록한다.

---

# 4. None 판정

`none`에는 Skill이 존재하지 않는다.

따라서:

- native Skill activation 없음
- sentinel 없음

이면 `none` 후보다.

하지만 host trace가 불완전하다면:

```text
actual=none
observable=false
```

처럼 confidence를 분리한다.

최종 benchmark에서는 `observable=true`인 run을 기본 분석 대상으로 하고, unobservable 비율도 host metric으로 따로 보고한다.

---

# 5. Session isolation

각 prompt는 **fresh session**에서 실행한다.

이유:

- 앞에서 activation된 Skill body가 context에 남을 수 있음
- Claude Code는 invoked Skill content가 이후 turn에도 남음
- 대화 context가 다음 routing을 바꿀 수 있음

따라서 20개 prompt를 한 세션에 연속 입력하면 안 된다.

---

# 6. Variant isolation

A0 → A1로 파일을 덮어쓴 뒤 같은 session을 재사용하지 않는다.

각 variant마다:

1. fixture materialize
2. discovery reload/restart
3. discovery inventory 확인
4. fresh session prompt 실행
5. raw artifact 저장

순서로 한다.

---

# 7. Discovery preflight

각 host에서 본 실험 전에 네 Skill이 모두 발견되는지 확인한다.

기대:

```text
feature
bugfix
refactor
review
```

Skill inventory가 틀리면 routing 결과를 기록하지 않는다.

---

# 8. Claude Code adapter

Official:
https://code.claude.com/docs/en/skills

확인할 것:

- 네 project Skill discovery
- description variant
- fresh session
- auto invocation
- sentinel 또는 native eval evidence

Claude는 공식적으로:

- description 기반 auto invocation
- `/skill-name` explicit invocation
- `disable-model-invocation`
- plugin eval / skill-creator eval

을 지원한다.

## Pilot 권장

routing fixture를 작은 plugin 또는 project skills로 구성한다.

먼저 direct control:

```text
/feature
```

에서 sentinel이 나오는지 확인한다.

그 뒤 natural-language prompt로 auto routing을 본다.

## 주의

A0~A2에서는 `disable-model-invocation`을 쓰지 않는다.

A3 manual-only control에서만 별도 적용한다.

---

# 9. Codex adapter

Official:
https://developers.openai.com/blog/eval-skills

Codex 공식 eval workflow는 automation 시:

```bash
codex exec --json "<prompt>"
```

을 사용해 JSONL trace를 저장하는 방식을 권장한다.

## Preflight

명시 호출로 fixture body가 정상 동작하는지 확인:

```text
$feature
```

또는 current Codex의 Skills invocation surface를 사용.

## Auto routing

skill 이름을 prompt에 쓰지 않은 natural-language case를 실행한다.

## Raw evidence

- JSONL stdout 보존
- stderr 보존
- final response 보존
- sentinel
- Skill load/invocation 관련 event가 있다면 별도 추출

## 주의

`codex exec --json`이 구조화 trace를 제공한다는 사실과, 모든 버전에서 별도 `skill_activated` event가 존재한다는 것은 다른 주장이다.

실제 pilot에서 event schema를 먼저 기록하고 grader를 그 schema에 맞춘다.

---

# 10. Gemini CLI adapter

Official:
https://geminicli.com/docs/cli/skills/
https://geminicli.com/docs/tools/activate-skill/

Gemini routing은 관측 surface가 명확하다.

모델이:

```text
activate_skill(name)
```

을 호출한다.

## 판정

`activate_skill` argument의 `name`을 `selected_skill`로 기록한다.

sentinel은 secondary evidence다.

## Consent

Gemini는 Skill activation에 consent 단계가 있다.

따라서 별도 기록:

- consent_required
- consent_result
- consent latency

routing metric에는 consent 이후 실행 성공 여부를 섞지 않는다.

### 예

모델이 정확히 `bugfix`를 골랐지만 사용자가 activation을 거부:

- routing = correct
- activation consent = denied
- body_loaded = false

이렇게 분리한다.

---

# 11. Cursor adapter

Official:
https://cursor.com/docs/skills

현재 docs에서:

- automatic Skill use
- explicit `/skill-name`
- `disable-model-invocation`
- `paths`

가 확인된다.

그러나 이번 조사에서는 machine-readable Skill auto-activation event를 확정하지 못했다.

## Pilot 순서

전체 20개를 바로 돌리지 않는다.

1. explicit `/feature`
2. 매우 명확한 feature prompt
3. 매우 명확한 bugfix prompt
4. none prompt

네 개만 먼저 실행.

native transcript/UI에 activation evidence가 남는지 확인한다.

없으면 sentinel을 pilot evidence로 사용하되:

```text
activation_evidence=sentinel
```

로 명시한다.

---

# 12. GitHub Copilot CLI adapter

Official:
https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference

현재 CLI는:

- `/SKILL-NAME`
- auto invocation
- `disable-model-invocation`
- `user-invocable`
- `copilot skill list --json`

을 지원한다.

## Discovery preflight

`skill list --json`은 discovery inventory를 확인하는 데 사용한다.

주의:

inventory에 있다는 것은 해당 prompt에서 Skill이 activation됐다는 뜻이 아니다.

## Pilot

Cursor와 동일하게 먼저 4개 smoke case로 activation evidence를 확인한 뒤 전체 20개로 간다.

---

# 13. 결과 row 규칙

`results-template.csv`의 핵심:

### expected

corpus의 gold label.

### actual

- feature
- bugfix
- refactor
- review
- none
- unobservable

중 하나.

### observable

`true/false`

### routing_evidence

예:

```text
activate_skill:bugfix
native-skill-event:refactor
sentinel:feature
no-activation-observed
```

---

# 14. Calibration 결과로 수정 가능한 것

파일럿에서는 수정 가능:

- host adapter
- result collector
- event parser
- 잘못된 gold label
- 명백히 모호한 prompt
- description이 의도한 variant를 제대로 구현하지 못한 경우

하지만 수정했으면:

- pilot version 증가
- 기존 결과 폐기
- 새 calibration 처음부터 실행

한다.

---

# 15. Development 단계에서 수정 가능한 것

calibration이 끝난 뒤 development 44개를 사용해:

- description 개선
- boundary 개선
- length control 보정

을 할 수 있다.

단:

> holdout 16개 prompt는 열어 보고 description을 조정하는 용도로 사용하지 않는다.

현재 holdout ID는 `split.json`에 freeze되어 있지만 실험자가 description을 수정하는 동안 prompt 본문은 되도록 노출하지 않는 운영이 바람직하다.

---

# 16. Frozen confirmatory set

final candidate description을 고정한 뒤 frozen confirmatory set을 실행한다. 이 set은 tuning에는 사용하지 않지만 corpus 작성자가 이미 전체 prompt를 본 상태이므로 blind holdout은 아니다.

최종 보고서에 최소 포함:

- host/model/version
- variant
- N runs
- accuracy
- macro-F1
- false positive
- routing-pair collision
- abstention accuracy
- unobservable rate
- description size
- run consistency

---

# 17. 이 pilot의 성공 기준

파일럿의 목적은 A2가 A1보다 이기는 것이 아니다.

성공 조건은:

1. 실제 Skill selection을 판정할 수 있다.
2. host 간 판정 기준 차이를 문서화했다.
3. fresh-session 반복이 가능하다.
4. raw trace를 보존할 수 있다.
5. none을 판정할 수 있다.
6. variant를 바꿔도 body와 나머지 조건이 동일하다.

이 조건이 만족될 때만 full eval로 넘어간다.


## Publication-level external holdout

책에서 model/host 일반화 수치를 제시하기 전에는 별도의 unseen dataset을 추가한다.

내부 frozen set의 목적은 **분할 변경과 tuning leakage를 줄이는 것**이지, 독립 검증을 대체하는 것이 아니다.
