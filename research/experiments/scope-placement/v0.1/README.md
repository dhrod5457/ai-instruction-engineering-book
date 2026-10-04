# Scope Placement Pilot v0.1

## 상태

**SMOKE RUN STARTED / CALIBRATION NOT STARTED**

Experiment B의 첫 비교는 다음 두 조건만 다룬다.

- `S0_monolithic_root`: 모든 global/local rule을 root `AGENTS.md` 하나에 둔다.
- `S1_nested_agents`: global rule은 root, subsystem rule은 `backend/`, `frontend/`, `deploy/`, `docs/`의 nested `AGENTS.md`에 둔다.

이번 단계에서는 S2 path-scoped vendor rule과 S3 on-demand Skill을 넣지 않는다. S0/S1에서 fixture와 grader가 안정된 뒤 확장한다.

## 파일

- `rules.json`: global/backend/frontend/deploy/docs 규칙 집합
- `pilot-tasks.json`: 서로 독립적인 12개 calibration task
- `scope_harness.py`: synthetic repo materialize + deterministic grader
- `phase_b_runner.py`: Claude Code/Codex fresh-workspace S0/S1 실행 및 결과 집계
- `test_scope_harness.py`: variant parity와 grader 회귀 테스트
- `test_phase_b_runner.py`: host command/permission contract와 summary 회귀 테스트

## 핵심 통제 조건

S0와 S1은 다음이 완전히 동일하다.

- application/workload 파일
- task prompt
- validation script
- baseline content
- deterministic assertions

달라지는 것은 instruction placement뿐이다.

`test_scope_harness.py`가 두 variant의 workload SHA 집합이 동일한지 검사한다.

## Pilot task 구성

- backend: 2
- backend test: 1
- frontend: 2
- frontend test: 1
- deploy: 2
- docs: 2
- cross-cutting: 2

합계 12개.

각 task는 다음을 가진다.

- working directory
- allowed files
- required rule IDs
- required validation target
- forbidden validation target
- must-contain / must-not-contain deterministic assertion

## Validation command

fixture는 실제 Java/Node build를 요구하지 않는다.

대신 host가 다음 command를 실행하도록 규칙에 명시한다.

```bash
python3 scripts/verify.py backend
python3 scripts/verify.py frontend
python3 scripts/verify.py deploy
python3 scripts/verify.py docs
```

검증 script는 `.experiment/validation-log.jsonl`에 실제 target을 기록한다.

따라서 grader가 다음을 구분할 수 있다.

- 필요한 validation 누락
- 다른 subsystem validation leakage
- `all` 같은 과도한 verification

## Preflight

```bash
cd research/experiments/scope-placement/v0.1
python3 scope_harness.py validate
python3 -m unittest -v test_scope_harness.py
```

## Materialize

```bash
python3 scope_harness.py materialize \
  --variant S0_monolithic_root \
  --output /tmp/scope-s0

python3 scope_harness.py materialize \
  --variant S1_nested_agents \
  --output /tmp/scope-s1
```

## Grade

host가 task를 수행한 뒤:

```bash
python3 scope_harness.py grade \
  --workspace /tmp/scope-s1 \
  --task B-01 \
  --json-out /tmp/B-01.json \
  --md-out /tmp/B-01.md
```

현재 deterministic grader는 다음을 본다.

- changed-file scope
- task-specific required content
- forbidden content
- targeted validation 수행
- over-verification
- controller -> repository 직접 dependency
- frontend direct fetch
- deploy latest tag
- deploy resource removal
- plaintext secret

## 아직 측정하지 않는 것

현재 `fixture_instruction_bytes`는 fixture에 존재하는 instruction file 총량이다.

이 값은 **실제 model context exposure가 아니다.**

실제 host가:

- ancestor/root AGENTS를 언제 읽는지
- nested AGENTS를 어떤 시점에 주입하는지
- cross-cutting task에서 여러 scope를 어떻게 합치는지

는 host trace 또는 실행 결과로 따로 측정해야 한다.

## 다음 실행 순서

1. S0/S1 × 12 task를 한 host에서 1회 calibration
2. grader/fixture 오류 수정
3. 수정이 발생하면 기존 calibration 폐기
4. stable하면 반복 실행
5. 그 뒤 S2 path-scoped rules 추가
6. 마지막에 S3 procedure-as-Skill 추가

첫 host는 AGENTS.md nested semantics가 명확한 Codex 또는 Claude Code가 적합하다.


## Phase B runner

CLI 설치/버전만 확인:

```bash
python3 phase_b_runner.py --host claude --out /tmp/scope-claude --preflight-only
python3 phase_b_runner.py --host codex --out /tmp/scope-codex --preflight-only
```

3개 smoke task만 S0/S1에 각각 1회:

```bash
python3 phase_b_runner.py \
  --host claude \
  --model <exact-model-id> \
  --task B-01 \
  --task F-01 \
  --task DOC-01 \
  --runs 1 \
  --out runs/claude-smoke
```

전체 calibration:

```bash
python3 phase_b_runner.py \
  --host codex \
  --model <exact-model-id> \
  --runs 1 \
  --out runs/codex-calibration
```

runner는 task마다 fresh synthetic workspace를 만들고 task의 `working_dir`에서 host를 시작한다.

Claude Code는 현재 built-in `agents-md`를 다음 모드로 강제한다.

```text
claude-md-and-agents-md
```

fixture에는 CLAUDE.md가 없다. fallback suppression을 피하기 위해 both 모드를 명시한다. 설정 전달만으로 실제 로딩을 증명하지 않으며, smoke의 검증 수행과 raw trace를 함께 확인한다. 로컬에는 Claude 2.1.274와 2.1.287이 공존했으므로 PATH와 preflight의 실제 binary/version을 고정해야 한다.

Claude permission boundary:

- edit: acceptEdits
- permission prompt: none
- Bash allow: fixture verifier, git status/diff
- MCP: deny

Codex permission boundary:

- sandbox: workspace-write
- add-dir: 해당 run의 synthetic workspace root (subsystem CWD에서도 검증 로그 쓰기 허용)
- approval: never
- 기본 sandbox network 정책 유지

실제 사용자 repository는 agent workspace로 사용하지 않는다.

### Gemini가 아직 Phase B에 없는 이유

Gemini `auto_edit`는 edit tool만 자동 승인하고 shell validation은 별도 승인 대상이다.
`yolo`로 우회하면 실험 자동화는 쉽지만 권한 조건 자체가 Claude/Codex보다 넓어진다.

따라서 Phase B v0.1에서는 Claude/Codex로 S0/S1 fixture를 먼저 안정화하고,
Gemini는 verifier command만 허용하는 Policy Engine profile을 추가한 뒤 같은 실험에 넣는다.

## 2026-10-03 smoke 수정

- G5: `.experiment/validation-log.jsonl`은 평가 기록이며 task 파일 제한의 예외다. 삭제·복원·덮어쓰기를 금지한다.
- 기존 과제의 “한 파일만 수정” 제한 때문에 Codex가 정상 검증 후 로그를 정리하는 경우를 실제로 관측했다. 로그 없음은 검증 미실행과 동일하지 않았다.
- timeout의 byte stdout/stderr를 보존하고 stdin을 닫아 외부 입력 혼입을 막는다.
- 수정 전 run은 calibration에서 제외한다.
- 결과: [SMOKE-REPORT-2026-10-03.md](../../SMOKE-REPORT-2026-10-03.md).
