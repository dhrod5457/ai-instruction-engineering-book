# Trigger Routing Pilot v0.1

## 상태

이 디렉터리는 최종 벤치마크가 아니라 **calibration pilot**이다.

목적:

1. description variant가 서로 의도한 차이를 실제로 갖는지 확인
2. host adapter가 Skill metadata를 정확히 노출하는지 확인
3. 결과 collector와 scorer가 routing을 잘 기록하는지 확인
4. ambiguous prompt나 잘못 라벨링된 case를 찾기

파일럿 결과를 보고 description, case, scorer, harness 중 하나라도 수정했다면 이 실행의 숫자는 폐기한다.

이 저장소 내부의 최종 확인에는 frozen confirmatory set을 사용한다. 다만 corpus 작성자가 전체 80개를 이미 작성·검토했으므로 이것은 진짜 blind holdout이 아니다. 출판 수준의 일반화에는 독립적으로 작성되거나 사전에 보지 않은 external holdout을 추가한다.

## 파일

- `variants.json`: A0 Broad, A1 Concise, A1L Length-Control, A2 Boundary-Aware의 정확한 description
- `pilot-cases.json`: 20개 calibration prompt
- `harness.py`: fixture validation, host별 Skill materialize, 결과 score
- `phase_a_runner.py`: Claude Code/Codex/Gemini CLI Phase A fresh-process 실행 및 raw trace 수집
- `PHASE-A-STATUS.md`: 현재 실행 상태, smoke 기준, host 실측 전제
- `test_harness.py`: harness 표준 라이브러리 기반 회귀 테스트
- `results-template.csv`: 수집 결과 schema
- `split.json`: calibration/development/frozen confirmatory split
- full corpus 원본: `../../../instruction-files/18-trigger-eval-corpus.md`

## 실험 단위

각 run에는 다음을 고정한다.

- 같은 host
- 같은 model
- 같은 host/model version
- 같은 Skill name
- 같은 Skill body
- 같은 tool permission
- 같은 prompt
- 같은 available Skill set

A0/A1/A1L/A2 사이에서 달라지는 것은 **description text만**이다.

## 파일럿 20개 구성

- explicit positive: 4
- implicit positive: 4
- noisy positive: 4
- routing pair: 6
- none/abstention: 2

파일럿은 빠르게 harness 문제를 찾는 목적이므로 최종 80개 corpus의 class 비율과 정확히 같을 필요는 없다.

## A3 Manual-only

manual-only는 공통 variant에서 제외한다.

이유:

- Claude Code, Codex, Cursor, Gemini 등은 manual invocation 관련 metadata와 semantics가 동일하지 않을 수 있다.
- 후보 목록에서 완전히 빠지는지, slash command로만 보이는지, 자연어 요청에서 대체 Skill을 고르는지가 host behavior다.

따라서 A3는 **host adapter별 control experiment**로 따로 만든다.

## Harness preflight

외부 host를 실행하기 전에 먼저 fixture 자체를 검증한다.

```bash
cd research/experiments/trigger-routing/v0.1
python3 harness.py validate
python3 -m unittest -v test_harness.py test_phase_a_runner.py
```

variant를 host별 project Skill 위치에 materialize할 수 있다.

```bash
python3 harness.py materialize --variant A1_concise --host claude --output /tmp/route-claude
python3 harness.py materialize --variant A1_concise --host codex --output /tmp/route-codex
python3 harness.py materialize --variant A1_concise --host gemini --output /tmp/route-gemini
```

기본 경로는 기준일 현재 문서에 맞춘다.

- generic: `.agents/skills`
- Claude Code: `.claude/skills`
- Codex: `.codex/skills`
- Cursor: `.cursor/skills`
- Gemini CLI: `.gemini/skills`
- Copilot CLI: `.github/skills`

제품 문법이 바뀌었거나 다른 호환 경로를 시험하려면 `--skills-dir`로 명시적으로 override한다.

수집한 CSV는 다음처럼 score한다.

```bash
python3 harness.py score --results results.csv --json-out score.json --md-out score.md
```

scorer는 observable run만 routing accuracy/F1 계산에 사용하고, observable rate는 별도로 보고한다.

## 1차 실행 권장 순서

1. `harness.py validate`와 `test_harness.py` 통과
2. A0/A1/A1L/A2 각각 20개 prompt를 1회 실행
2. routing trace가 정상 수집되는지 확인
3. case label/harness 오류가 있으면 수정
4. 수정 후 pilot version을 올리고 처음부터 재실행
5. fixture가 안정되면 각 prompt 5회 반복
6. 그 뒤 full 80-case corpus + holdout으로 이동

## 파일럿에서 볼 값

### 반드시 기록

- expected
- actual selected skill
- selected none 여부
- host/model/version
- variant
- prompt id
- run index
- raw routing evidence

### 가능하면 기록

- metadata tokens
- total input tokens
- latency
- Skill body load 여부

## 판정

`actual`은 최종 답변 내용을 보고 추측하지 않는다.

우선순위:

1. host가 제공하는 Skill invocation/activation trace
2. 실제 Skill body load/tool event
3. 명시적 routing log
4. 위 정보가 없으면 해당 host의 결과는 `unobservable`로 표시

모델이 답변에서 "bugfix skill을 사용했다"고 말한 자기보고만으로 success를 판정하지 않는다.

## Calibration 종료 조건

다음을 모두 만족하면 v0.1 fixture를 고정할 수 있다.

- 20개 case에서 expected label 자체의 명백한 오류가 없음
- host adapter가 `none`을 포함해 실제 선택을 판정 가능
- A0/A1/A2 description 외 다른 조건이 동일함
- raw run artifact를 재검토 가능
- scorer가 confusion matrix를 만들 수 있음

이후 full run에서는 파일럿을 보고 수정한 prompt를 holdout으로 재사용하지 않는다.


## Variant 비교 해석

- **A0 vs A1**: 현실적인 broad/verbose → concise 개선 효과. 길이와 범위가 함께 달라지므로 원인 분리는 불가.
- **A1 vs A1L**: 같은 routing 의미에서 description 길이와 비-routing detail 증가 효과.
- **A0 vs A1L**: 길이가 비슷할 때 broad trigger surface와 narrow trigger surface 차이.
- **A1 vs A2**: adjacent boundary 문장을 추가한 효과.

이 네 비교를 분리해야 "짧아서 좋아졌다"와 "경계가 좋아져서 좋아졌다"를 혼동하지 않는다.


## Holdout 한계

`split.json`의 16개는 **frozen confirmatory set**이다.

- description iteration 중에는 사용하지 않는다.
- 분할을 결과에 맞춰 다시 고르지 않는다.
- 하지만 corpus 작성자가 전체 prompt를 이미 알고 있으므로 blind holdout이라고 부르지 않는다.

책에서 강한 일반화 수치를 제시하려면 이후 다음 중 하나를 추가한다.

1. 다른 사람이 독립적으로 작성한 prompt
2. 공개 이슈/실제 사용자 요청에서 사후 샘플링한 prompt
3. 실험 설계가 끝난 뒤 새로 확보한 unseen prompt

