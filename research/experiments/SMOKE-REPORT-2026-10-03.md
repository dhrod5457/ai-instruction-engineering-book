# 실제 CLI Smoke 보고서 — 2026-10-03

상태: **SMOKE COMPLETED / FULL CALIBRATION NOT STARTED**

실제 모델을 호출해 실행 환경·Skill 선택 관측·S0/S1 검증 기록을 점검했다. 아래 결과는 성능 비교를 위한 표본이 아니며 책에 효과 수치로 인용하지 않는다.

## 실행 환경

- Claude Code: 2.1.287, claude-sonnet-4-6, claude.ai 계정 로그인.
- Codex CLI: 0.160.0, gpt-6.1-sol, ChatGPT 계정 로그인.
- Gemini CLI: 0.38.2, 모델 실행 전 인증 거부. model/version 실측 없음.
- 실제 저장소 대신 run마다 별도 synthetic workspace와 새 CLI process를 사용했다.
- 로컬에 Claude 2.1.274도 존재했다. 초기 PATH가 이 버전을 선택해 초기 시도를 폐기하고 2.1.287 binary를 선택했다. Phase B preflight는 이제 2.1.277 미만을 거부한다.

## Experiment A — A1_concise, 세 과제

| Host | EP-F01 (feature) | EP-B01 (bugfix) | NO-04 (none) |
| --- | --- | --- | --- |
| Claude 2.1.287 | feature sentinel | bugfix sentinel | unobservable |
| Codex 0.160.0 | feature sentinel | bugfix sentinel | unobservable |
| Gemini 0.38.2 | 인증 거부 | 인증 거부 | 인증 거부 |

Claude/Codex에서 명확한 두 routing을 관측했다. Codex 최종 A 실행에는 read-only sandbox와 approval=never를 명시했다. NO-04 응답은 로그 제공을 요청했지만, activation evidence가 없다는 이유만으로 none이라고 판정하지 않았다. 세 host의 none 관측 정책이 확정되기 전에는 전체 routing calibration을 실행하지 않는다.

Gemini는 `--skip-trust`를 지원하지 않아 처음에는 옵션 파싱 단계에서 종료됐다. 해당 옵션을 제거한 재실행에서는 서버가 `IneligibleTierError / UNSUPPORTED_CLIENT`로 현재 개인 Code Assist 클라이언트의 인증을 거부했다. 이는 실제 routing 실패가 아니다. 새 인증 방식·키 생성·클라이언트 교체는 수행하지 않았다.

## Experiment B — 세 과제 × S0/S1

B-01, F-01, DOC-01을 조건별 한 번씩 수행했다. 최신 smoke 선택: Codex v3, Claude v4.

| Host | Variant | 과제 통과 | 검증 기록 누락 |
| --- | --- | ---: | ---: |
| codex | S0_monolithic_root | 3/3 | 0 |
| codex | S1_nested_agents | 3/3 | 0 |
| claude | S0_monolithic_root | 3/3 | 0 |
| claude | S1_nested_agents | 3/3 | 0 |

각 host당 6건뿐이다. 두 placement 조건의 우열, 일반적 rule compliance 효과, context 절감 효과를 결론 내릴 수 없다. 토큰 노출량을 측정하지 않았으며 fixture_instruction_bytes는 실제 context exposure가 아니다.

## Smoke에서 발견하고 수정한 문제

1. **Codex subsystem CWD 쓰기 경계:** backend/frontend/docs에서 시작하면 루트의 검증 로그 쓰기가 거부됐다. 해당 run의 workspace root를 `--add-dir`로 지정했다. workspace-write와 approval=never를 유지했다.
2. **검증 후 로그 정리:** Codex는 “한 파일만 변경”을 지키려고 verifier가 만든 로그를 삭제/복원했다. G5로 평가 로그가 파일 제한의 예외임을 명시하고 보존하게 했다. 모든 S0/S1 조건에 동일하게 적용했다.
3. **Claude 지침 로딩:** fallback 모드의 run은 task 수정은 했지만 지정된 검증을 실행하지 않았다. 최종 adapter를 `agents-md@builtin`의 `claude-md-and-agents-md`로 고정한 재실행에서 검증까지 수행했다. 이전 run만으로 fallback suppression의 원인을 확정하지 않는다.
4. **Claude routing 환경 혼입:** 초기 run은 user 설정/도구가 들어와 추가 에이전트까지 실행했다. 최종 A adapter는 project settings, Skill/Read/Glob/Grep만 제공하고 MCP와 browser를 제외했다. 사용자 전역 파일이나 설치 설정을 변경하지 않았다.
5. **sentinel 오판정 가능성:** stdout 전체 검색을 중단했다. tool output·echoed Skill body가 아닌 구조화된 assistant text의 정확한 sentinel만 인정한다. 실패/timeout 및 여러 sentinel은 unobservable이다.
6. **원본 기록 유실:** TimeoutExpired가 반환하는 byte stdout/stderr를 보존하고 stdin을 닫았다.
7. **Gemini 빈 stream:** 종료 코드 0만으로 none을 판정하지 않는다. 완료 success event가 필요하다.

## 결과 보존과 무효화

- [선택된 CSV와 SHA-256 manifest](smoke/2026-10-03/).
- raw command/stdout/stderr, 과제·grader 결과와 workspace snapshot은 로컬 `ai-instruction-experiment-runs`에 보존했다. 원본 trace는 이 PR에 공개하지 않았다.
- manifest는 모든 로컬 artifact의 상대 경로와 SHA-256을 기록한다. final adapter hash는 수정 후 snapshot이며 각 과거 실행의 정확한 source snapshot이라는 뜻이 아니다.
- 초기 run, fixture/adapter 변경 전 run, 인증 오류 run은 calibration에서 제외한다. 최신 smoke도 calibration sample로 재사용하지 않는다.
- 외부 계정 정보나 자격 증명은 저장소에 추가하지 않았다.
- 사용자 scope 지침/기본 Skill 목록을 완전히 제거한 대조 환경은 아직 만들지 않았다. 따라서 최신 smoke도 재현 경로 점검용이다.

## 다음 단계

1. 완료 stream + inventory + native Skill activation을 근거로 Claude/Codex none 관측 정책을 확정한다.
2. scope host 환경을 고정하고 user 지침 혼입을 기록/통제한 뒤 host당 2 variants × 12 tasks 전체 calibration을 별도로 실행한다.
3. Gemini의 지원 클라이언트와 인증 경로를 해결한 뒤 동일 smoke를 재실행한다.
4. adapter가 안정되면 routing host당 4 variants × 20 prompts calibration을 수행한다.
5. 반복 실행과 holdout을 거친 뒤 7/14/15/16장에 검증 결과를 반영한다.

## 로컬 검증

- Trigger Routing: frozen fixture VALID, 13개 테스트 통과.
- Scope Placement: S0/S1 workload parity VALID, 9개 테스트 통과.
- git diff whitespace 검사 통과.

## 수정 근거

- [OpenAI CLI reference](https://developers.openai.com/codex/cli/reference/): --add-dir 쓰기 경계.
- [Anthropic agents-md 원문](https://github.com/anthropics/claude-code/blob/main/mods/agents-md/README.md): built-in 설정 키와 instructionFiles 모드.
- [Gemini Trusted Folders](https://geminicli.com/docs/cli/trusted-folders/): 현행 문서와 설치 0.38.2 옵션 계약 차이는 실제 help/실행 결과로 구분했다. trust 설정을 전역 변경하지 않았다.
