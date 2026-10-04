# Trigger Routing Phase A 실행 상태

기준일: 2026-10-03

## 상태

**SMOKE RUN STARTED / CALIBRATION NOT STARTED**

자료 수집 단계는 종료했고 실제 cross-host routing 실측을 위한 실행 harness까지 구현했다.

현재 완료:

- frozen fixture structural validation
- source Git blob SHA 고정 검증
- host별 routing-only Skill materialize
- 결과 CSV schema
- confusion matrix / accuracy / macro-F1 / abstention / collision / consistency scorer
- Claude Code / Codex / Gemini CLI Phase A runner
- raw command/stdout/stderr/result-row artifact 보존
- unittest
- GitHub Actions validation gate

아직 하지 않은 것:

- 실제 Claude Code routing calibration
- 실제 Codex routing calibration
- 실제 Gemini CLI routing calibration

2026-10-03 로컬 환경에서 Claude Code 2.1.287, Codex CLI 0.160.0, Gemini CLI 0.38.2로 첫 smoke를 실행했다.

Claude/Codex의 feature·bugfix sentinel을 관측했다. none은 여전히 unobservable로 유지한다. Gemini는 지원되지 않는 `--skip-trust` 옵션을 제거한 뒤 서버의 `UNSUPPORTED_CLIENT` 인증 거부를 확인했다. 이 시도들은 전체 calibration 또는 책의 효과 수치가 아니다.

상세 결과와 무효화 정책: [SMOKE-REPORT-2026-10-03.md](../../SMOKE-REPORT-2026-10-03.md).

---

## Phase A 대상

첫 실측 대상:

1. Claude Code
2. Codex CLI
3. Gemini CLI

Cursor와 Copilot CLI는 activation observability smoke를 먼저 별도 확인한 뒤 Phase B로 넣는다.

---

## 실행 안전 경계

runner는 실제 project repository에서 prompt를 실행하지 않는다.

각 run마다:

1. 별도 synthetic workspace 생성
2. routing-only Skill 4개 materialize
3. 빈 git repository initialize
4. fresh CLI process 실행
5. raw trace 저장

Skill body:

- 파일 수정 금지
- 명령 실행 금지
- 실제 사용자 task 수행 금지
- activation 시 sentinel만 출력

host별 추가 경계:

- Claude: `--permission-mode plan`, `Skill,Read,Glob,Grep`만 제공, user settings/MCP/browser 제외
- Gemini: `--approval-mode plan`
- Codex: `--sandbox read-only`, `--ask-for-approval never`, `--full-auto` 사용 안 함

---

## Preflight

```bash
cd research/experiments/trigger-routing/v0.1

python3 harness.py validate
python3 -m unittest -v test_harness.py test_phase_a_runner.py

python3 phase_a_runner.py --host claude --out /tmp/claude-preflight --preflight-only
python3 phase_a_runner.py --host codex --out /tmp/codex-preflight --preflight-only
python3 phase_a_runner.py --host gemini --out /tmp/gemini-preflight --preflight-only
```

preflight는 CLI 설치 여부와 version을 기록한다.

---

## 첫 smoke

전체 80 run 전에 host마다 다음 세 case만 먼저 본다.

- `EP-F01`: 명확한 feature
- `EP-B01`: 명확한 bugfix
- `NO-04`: none

A1 concise 하나로 실행한다.

예:

```bash
python3 phase_a_runner.py \
  --host claude \
  --model <exact-model-id> \
  --variant A1_concise \
  --case EP-F01 \
  --case EP-B01 \
  --case NO-04 \
  --out runs/claude-smoke
```

smoke 목적은 accuracy 측정이 아니다.

확인할 것:

- Skill inventory가 실제로 discovery되는가
- activation evidence가 machine-readable한가
- sentinel fallback이 동작하는가
- none을 관측할 수 있는가
- CLI가 synthetic workspace 밖에 side effect를 만들지 않는가

---

## 관측 한계

Gemini:

- `activate_skill(name)` event를 native evidence로 사용 가능
- 정상 complete stream에서 activation event가 없으면 none을 관측 가능 상태로 기록

Claude/Codex:

- 현재 runner는 sentinel을 확실한 activation evidence로 사용
- sentinel/native activation evidence가 없으면 `unobservable`
- absence만으로 none이라고 단정하지 않음

따라서 Claude/Codex smoke에서 native activation event가 새롭게 확인되면 parser를 먼저 보강하고 기존 smoke 결과는 calibration metric에서 제외한다.

---

## Calibration

smoke 후 adapter를 고정하면 host당:

```text
4 variants
× 20 prompts
× 1 run
= 80 runs
```

을 실행한다.

이 80 run은 calibration이다.

description, parser, gold label, harness를 수정하면 해당 calibration 결과는 폐기한다.

fixture가 안정된 뒤에만 반복 횟수를 5로 올린다.

---

## 현재 성공 조건

Phase A가 “완료”되려면 accuracy가 높을 필요는 없다.

다음이 충족되어야 한다.

- 세 host에서 동일 fixture를 재현 가능
- 실제 activation 판정 가능
- none 관측 정책 확정
- raw trace 보존
- fresh session/process 보장
- 동일 prompt/variant 조건 유지
- scorer가 host 결과를 동일 schema로 계산

그 뒤에야 description variant 성능 비교를 시작한다.
