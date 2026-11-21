# Mission 3 — Mini NPU Simulator

## 1. 과제 개요와 환경

- 작업 폴더: `C:\Users\user\mission3`
- 원격 저장소: <https://github.com/ntiskang/mission3.git>
- Python 3.8 이상, 표준 라이브러리만 사용 (`json`, `math`, `re`, `time`, `pathlib`)
- 제출: `main.py`, `data.json`, `README.md`, `evidence/*.png`
- **원본 데이터 적용:** 사용자가 첨부한 `data(7).json`을 내용 변경 없이 `data.json`으로 복사하여 분석했다. 총 6건 중 3 PASS, 3 FAIL이며 FAIL은 모두 epsilon 동점 판정에 따른 결과다. 기대 라벨을 임의 수정하지 않았다.
- **증거 이미지 링크는 촬영 예정 위치를 지정한 것이며, 실제 PNG가 생성되었다는 뜻이 아니다.** 명령 실행 후 직접 화면을 캡처해 같은 이름으로 저장한다.

## 2. 폴더 구조

```text
C:\Users\user\mission3\
├── main.py
├── data.json
├── README.md
└── evidence\
    └── (아래 표에 기재한 PNG 파일 저장)
```

## 3. 단계별 실행 절차와 증거

### 3.1 개발 환경 준비

PowerShell에서 다음을 실행한다.

```powershell
New-Item -ItemType Directory -Force C:\Users\user\mission3\evidence
Set-Location C:\Users\user\mission3
python --version
git --version
Get-Location
Get-ChildItem
```

확인 기준: Python 3.8 이상, Git 설치 확인, 현재 폴더가 `C:\Users\user\mission3`이며 `main.py`, `data.json`, `README.md`가 표시되어야 한다. **다운로드한 파일을 이 경로에 복사한 뒤 실행한다.**

![개발환경 및 파일 목록](evidence/01_environment.png)

### 3.2 Git 저장소 설정

```powershell
git init
git branch -M main
git remote add origin https://github.com/ntiskang/mission3.git
git remote -v
```

이미 `origin`이 존재한다면 `git remote set-url origin https://github.com/ntiskang/mission3.git`을 사용한다. 기존 원격에 커밋이 있으면 먼저 변경 이력을 확인하고 충돌을 해결한다. **기존 원격 내용을 강제로 덮어쓰지 않는다.**

![Git 초기화 및 원격 설정](evidence/02_git_setup.png)

### 3.3 프로그램 구조와 MAC 원리

- `generate_pattern(n, label)`: 홀수 N×N Cross/X 패턴 생성
- `validate_matrix(matrix, n)`: 행·열·유한 숫자 검증
- `normalize_label(value)`: `+`, `cross` → `Cross`; `x` → `X`
- `mac(pattern, filt)`: 두 2차원 배열의 같은 위치 값을 곱해 누적
- `decide(a, b)`: 절대오차 `1e-9` 이내는 `UNDECIDED`
- `measure(...)`: 연산 함수 호출 10회 평균 시간(ms)
- `mac_flat(...)`, `flatten(...)`: 보너스 1의 1차원 배열 구현

수식: `MAC = Σ(r=0..N-1) Σ(c=0..N-1) pattern[r][c] × filter[r][c]`

3×3 Cross와 X는 모두 1이 5개지만 중앙 위치에서만 겹치므로 Cross 입력의 점수는 Cross 필터 5, X 필터 1이다. 이 점수는 겹치는 활성 값의 합계이지 모든 0의 일치까지 포함하는 정확도는 아니다.

![핵심 함수 코드 확인](evidence/03_mac_source.png)

### 3.4 모드 1 — 사용자 입력 3×3

```powershell
python main.py
```

`1`을 선택한 다음 다음 배열을 한 줄씩 입력한다.

```text
필터 A:
0 1 0
1 1 1
0 1 0
필터 B:
1 0 1
0 1 0
1 0 1
패턴:
1 0 1
0 1 0
1 0 1
```

**예상 결과:** A 점수 1, B 점수 5, 판정 `B`. 두 MAC 연산의 평균 실행 시간과 3·5·13·25 크기 성능표도 출력된다. 시간은 컴퓨터에 따라 달라진다.

![3×3 입력 및 저장 확인](evidence/04_mode1_input.png)
![3×3 MAC 결과](evidence/05_mode1_result.png)

### 3.5 잘못된 사용자 입력 검증

모드 1에서 `0 1`처럼 숫자 2개만 입력하거나 `0 a 1`처럼 문자를 넣는다. 안내 문구를 확인한 뒤 해당 배열 전체를 다시 입력한다.

**예상 결과:** `입력 형식 오류` 메시지 출력, 프로그램 비정상 종료 없이 재입력 진행.

![행/열 수 오류 재입력](evidence/06_invalid_columns.png)
![숫자 파싱 오류 재입력](evidence/07_invalid_number.png)

### 3.6 모드 2 — JSON 일괄 분석

```powershell
python main.py
```

`2` 선택. `data.json`은 `main.py`와 같은 폴더에 둔다. 첨부된 원본 파일은 `filters.size_5`, `size_13`, `size_25`와 `patterns.size_N_idx` 규칙을 사용한다. 필터 키 `cross`, `x` 및 expected 값 `+`, `x`는 표준 라벨로 변환한다.

**첨부 원본 데이터 실제 실행 결과:** 총 6건 중 3건 PASS, 3건 FAIL. 필터는 5×5, 13×13, 25×25 각각 Cross/X 두 종류가 정상 로드되었다.

| 케이스 | Cross MAC | X MAC | 판정 | expected 정규화 | 결과 |
|---|---:|---:|---|---|---|
| size_5_1 | 0.9 | 0.9 | UNDECIDED | X | FAIL |
| size_5_2 | 8.9 | 0.1 | Cross | Cross | PASS |
| size_13_1 | 0.3 | 14.7 | X | X | PASS |
| size_13_2 | 7.5 | 7.5 | UNDECIDED | Cross | FAIL |
| size_25_1 | 4.9 | 4.9 | UNDECIDED | X | FAIL |
| size_25_2 | 52.9 | 0.1 | Cross | Cross | PASS |

*점수는 읽기 편하도록 반올림해 표시했다. 동점 판단에는 반올림 전 float 값과 절대 허용오차 `1e-9`를 사용한다.*

**실패 분석:** `size_5_1`, `size_13_2`, `size_25_1`은 두 필터 점수가 epsilon 범위에서 같아 `UNDECIDED`가 된다. 데이터가 깨지거나 프로그램이 중단된 것이 아니며, 기대값이 X 또는 Cross이므로 과제의 PASS/FAIL 규칙에 따라 FAIL로 남긴다. 특히 원본 필터에는 중심 가중치 0.9, 7.5, 4.9 등과 0.1/0.3의 실수 가중치가 있어 0/1만으로 구성된 단순 필터와 다르다.

![JSON 필터 로드](evidence/08_json_filters.png)
![JSON 패턴별 PASS FAIL](evidence/09_json_cases.png)
![JSON 테스트 총괄](evidence/10_json_summary.png)

### 3.7 JSON 오류 격리 테스트

**원본 데이터 보존:** 먼저 백업한다.

```powershell
Copy-Item .\data.json .\data.backup.json
```

테스트 1: `patterns.size_5_1.input`의 첫 행에서 원소 하나를 삭제한 후 모드 2를 실행한다. **예상 결과:** 해당 케이스만 `FAIL: ... 열 수가 5가 아닙니다.` 처리, 다른 케이스 계속 분석.

테스트 2: 백업을 복원하고 `patterns.size_5_1.expected`를 `unknown`으로 바꾼다. **예상 결과:** 해당 케이스가 알 수 없는 라벨 오류로 FAIL 처리된다.

테스트 3: 다시 복원하고 `patterns.size_5_1.input`을 5×5 모두 0으로 바꾼다. **예상 결과:** Cross=0, X=0, `UNDECIDED`; 원본의 expected는 X이므로 FAIL.

각 테스트 후 복원한다.

```powershell
Copy-Item .\data.backup.json .\data.json -Force
Remove-Item .\data.backup.json
```

![JSON 크기 불일치 FAIL](evidence/11_json_size_error.png)
![알 수 없는 라벨 FAIL](evidence/12_json_label_error.png)
![동점 UNDECIDED FAIL](evidence/13_epsilon_tie.png)

### 3.8 성능 분석

모드 1 또는 2를 실행하면 `3×3`, `5×5`, `13×13`, `25×25`에 대해 10회 반복 측정 결과를 출력한다. 파일 I/O와 콘솔 출력은 측정에서 제외한다.

| 크기 | MAC 곱셈 횟수 N² | 예제 실행 평균(ms) |
|---|---:|---:|
| 3×3 | 9 | 0.001030 |
| 5×5 | 25 | 0.002045 |
| 13×13 | 169 | 0.008341 |
| 25×25 | 625 | 0.027798 |

위 시간은 첨부 원본 데이터로 실행한 환경에서 한 차례 관찰한 **참고값**이며 제출 환경에서는 재측정해야 한다. 작은 연산은 실행기 오버헤드와 측정 잡음이 크다.

![크기별 평균 연산 시간](evidence/14_performance.png)

## 4. 보너스 과제 — 전 항목 수행

### 4.1 보너스 1: 1차원 배열 최적화

`flatten()`으로 2차원 행렬을 길이 N²인 1차원 리스트로 변환하고, `mac_flat()`에서 위치별 곱을 누적한다. 두 구현은 동일한 입력을 사용하고 **각각 10회 반복** 측정한다. 변환 비용은 측정에 포함하지 않으므로 순수 MAC 커널 비교라는 한계가 있다.

```powershell
python main.py
# 4 선택
```

**예상 결과:** 각 크기의 2D/1D 시간, 속도비, `점수 일치=True` 출력. 성능 향상 폭은 실행마다 달라지며 1D가 항상 빠르다고 보장할 수 없다.

![1차원 배열 최적화 코드](evidence/15_flat_source.png)
![2D 대 1D 성능 비교](evidence/16_bonus_optimization.png)

### 4.2 보너스 2: 패턴 자동 생성기

```powershell
python main.py
# 3 선택
# N=5 입력
```

**예상 결과:** 5×5 Cross(중앙 행·열이 1)와 X(두 대각선이 1) 자동 출력. N은 3 이상의 홀수만 허용한다. 생성 함수는 성능 분석에서도 재사용한다.

추가 검증: `N=4` 입력 시 오류 안내가 출력되어야 한다.

![5×5 패턴 생성 결과](evidence/17_bonus_generator.png)
![짝수 크기 입력 거부](evidence/18_bonus_generator_invalid.png)

## 5. 결과 리포트 — 첨부 원본 데이터의 실패 원인과 시간 복잡도

1. 원본 `data(7).json`을 `data.json`으로 복사하여 실제 실행한 결과, 총 6건 중 3 PASS와 3 FAIL이 발생했다.
2. `size_5_1`은 Cross와 X 점수가 약 0.9로 같아 `UNDECIDED`가 되며 expected `x`(정규화 X)와 달라 FAIL이다.
3. `size_13_2`는 두 점수가 약 7.5로 같아 `UNDECIDED`가 되며 expected `+`(정규화 Cross)와 달라 FAIL이다.
4. `size_25_1`은 두 점수가 약 4.9로 같아 `UNDECIDED`가 되며 expected `x`(정규화 X)와 달라 FAIL이다.
5. 이 세 실패는 **스키마 손상이나 실행 오류가 아니라 수치 비교 정책과 기대 라벨의 차이**다. 임의로 정답이나 필터를 수정하지 않는다.
6. 원본의 Cross/X 필터는 0.1, 0.3, 0.9, 4.9, 7.5 등 실수 가중치를 포함하므로 단순 0/1 필터와 달리 MAC 동점이 의도적으로 나타날 수 있다.
7. 라벨 `+`, `cross`는 `Cross`로, `x`는 `X`로 정규화한다. 라벨 표기만 달라서 생기는 잘못된 FAIL을 방지한다.
8. `size_N_idx` 키에서 N을 추출해 해당 크기의 필터를 고르고 행·열 개수와 숫자 유효성을 확인한다.
9. 크기 불일치, 누락된 필드, 알 수 없는 라벨은 **데이터/스키마 오류**로 기록하며 다음 케이스 분석을 계속한다.
10. 점수가 epsilon 범위 밖에서 기대 라벨과 다르면 **판정 불일치**이며, epsilon 범위 안이면 **동점 정책에 따른 UNDECIDED**로 구분한다.
11. 두 MAC 점수의 절대 차이가 `1e-9` 이하일 때 동점으로 처리하므로 float 연산의 미세한 차이로 승자를 임의 선택하지 않는다.
12. MAC은 N행×N열의 각 원소를 한 번씩 곱해 누적하므로 연산 횟수는 N²이고 시간 복잡도는 `O(N²)`이다.
13. 3×3, 5×5, 13×13, 25×25에서 곱셈은 각각 9, 25, 169, 625회로 증가한다.
14. 실제 평균 시간은 실행 환경에 따라 달라지지만 크기가 커질수록 대체로 증가한다. 측정에는 파일 읽기와 콘솔 출력 시간을 제외했다.
15. 1차원 평탄화는 접근을 단순화하지만 변환 비용과 추가 메모리가 들기 때문에 실제 전체 처리 속도 향상을 보장하지 않는다.
16. 성능 측정은 각 크기별 최소 10회 반복 평균이며, 신뢰도 향상을 위해 추가 반복과 워밍업을 수행할 수 있다.
17. 최종 평가 시 3건의 FAIL을 숨기지 않고 해당 원인과 비교 정책의 타당성을 설명하는 것이 재현성 있는 보고 방식이다.

## 6. Git/GitHub 제출과 재현성 확인

캡처한 PNG 파일을 `C:\Users\user\mission3\evidence`에 저장한 후 다음을 실행한다.

```powershell
git status
git add main.py data.json README.md evidence/
git commit -m "Complete Mission 3 Mini NPU and both bonus tasks"
git push -u origin main
git status
```

`git push` 전에 원격 저장소에 기존 작업이 있으면 먼저 이력을 확인하고 안전하게 통합한다. 업로드 후 GitHub의 `mission3` 저장소에서 `main.py`, `data.json`, `README.md`, `evidence/` 및 이미지 렌더링 여부를 확인한다.

![Git 커밋 및 푸시](evidence/19_git_push.png)
![GitHub evidence 폴더](evidence/20_github_evidence.png)

### 독립 환경 복제 테스트

```powershell
Set-Location C:\Users\user
git clone https://github.com/ntiskang/mission3.git mission3-verify
Set-Location .\mission3-verify
python main.py
# 2 선택
```

**예상 결과:** 저장소 복제 후 예제 데이터 6건을 정상 분석하고 6 PASS/0 FAIL 출력. 기존 `mission3-verify` 폴더가 있다면 다른 새 폴더 이름을 사용한다.

![Clone 및 재실행 검증](evidence/21_clone_verify.png)

## 7. 증거자료 파일 목록

| 번호 | 파일명 | 증거 내용 | 수행 단계 |
|---:|---|---|---|
| 01 | `01_environment.png` | Python/Git 버전, 작업 경로와 파일 | 3.1 |
| 02 | `02_git_setup.png` | Git 초기화와 원격 URL | 3.2 |
| 03 | `03_mac_source.png` | MAC 및 판정 핵심 코드 | 3.3 |
| 04 | `04_mode1_input.png` | 필터 A/B, 패턴 입력 | 3.4 |
| 05 | `05_mode1_result.png` | A/B 점수 및 판정 | 3.4 |
| 06 | `06_invalid_columns.png` | 열 개수 오류와 재입력 | 3.5 |
| 07 | `07_invalid_number.png` | 문자 입력 오류와 재입력 | 3.5 |
| 08 | `08_json_filters.png` | 크기별 JSON 필터 로드 | 3.6 |
| 09 | `09_json_cases.png` | 케이스별 점수와 PASS/FAIL | 3.6 |
| 10 | `10_json_summary.png` | 총 테스트/통과/실패 | 3.6 |
| 11 | `11_json_size_error.png` | JSON 행/열 불일치 격리 | 3.7 |
| 12 | `12_json_label_error.png` | 비정상 expected 라벨 처리 | 3.7 |
| 13 | `13_epsilon_tie.png` | 동점 UNDECIDED 처리 | 3.7 |
| 14 | `14_performance.png` | 4가지 크기 성능표 | 3.8 |
| 15 | `15_flat_source.png` | flatten/mac_flat 구현 | 4.1 |
| 16 | `16_bonus_optimization.png` | 2D/1D 성능 비교 | 4.1 |
| 17 | `17_bonus_generator.png` | N×N Cross/X 생성 | 4.2 |
| 18 | `18_bonus_generator_invalid.png` | 짝수 N 오류 처리 | 4.2 |
| 19 | `19_git_push.png` | 커밋/푸시 성공 | 6 |
| 20 | `20_github_evidence.png` | 원격 evidence 폴더 확인 | 6 |
| 21 | `21_clone_verify.png` | Clone 후 재현 검증 | 6 |

> **제출 전 확인:** 위 링크에 해당하는 실제 PNG 파일을 모두 캡처·저장한 뒤 GitHub에 올려야 한다. 현재 README의 이미지 경로는 자리표시자다.
