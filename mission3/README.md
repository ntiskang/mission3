# Mission 3 — Mini NPU Simulator

> 공식 과제의 **필수 기능 → 오류 검증 → 성능 분석 → 보너스 과제 → 결과 리포트 → 제출** 순서로 수행하는 PowerShell 실습 및 증거 수집 보고서. 모든 증거 링크는 맨 아래 **전체 증거자료 목록의 파일명과 1:1 일치**한다. 실제 캡처를 완료하기 전에는 이미지가 표시되지 않는 것이 정상이다.

## 1. 미션 개요 및 준수 사항

- 목표: Cross(+)와 X 패턴을 2차원 숫자 배열로 표현하고 MAC(Multiply–Accumulate) 점수로 판정한다.
- 실행 환경: Windows PowerShell, Python 3.8 이상, 작업 폴더 `C:\Users\user\mission3`.
- **외부 라이브러리 금지:** NumPy, pandas 등은 사용하지 않는다. Python 표준 라이브러리만 사용한다.
- 필수 기능: 사용자 3×3 입력, JSON 일괄 분석, 라벨 정규화, epsilon 동점 판정, 10회 평균 성능 측정, 실패 리포트.
- 보너스: 2차원/1차원 MAC 비교, 홀수 크기 Cross/X 생성기.
- 원본 `data.json`은 제공된 데이터를 수정하지 않고 사용한다. 원본 기준 6개 테스트 중 PASS 3개, FAIL 3개(동점 판정)이다.

## 2. 폴더 구조

```text
C:\Users\user\mission3\
├── main.py
├── data.json
├── README.md
└── evidence\                # 실제 캡처 PNG 22개 저장
```

> `main.py`의 실제 메뉴는 `1. 사용자 입력`, `2. data.json 분석`, `3. 패턴 생성기`, `4. 1D 최적화 성능 비교` 순서이다. 공식 과제의 기본 실행 흐름은 메뉴 1 또는 2를 선택하는 것이다.

## 3. 작업 지시 순서별 실행 절차

### 3.1 개발환경 준비 및 파일 확인 — 요구사항 6, 7

**① 작업 폴더 확인 및 evidence 생성**

```powershell
New-Item -ItemType Directory -Path C:\Users\user\mission3 -Force
Set-Location C:\Users\user\mission3
New-Item -ItemType Directory -Path .\evidence -Force
Get-Location
Get-ChildItem
```

`main.py`, `data.json`, `README.md`를 이 폴더에 저장한 뒤 파일 목록을 확인한다.

![01 프로젝트 폴더](evidence/01_project_directory.png)

**② Python 버전 확인**

```powershell
python --version
python -m pip --version
```

Python 3.8 이상인지 확인한다. pip는 버전 확인용이며 외부 라이브러리는 설치하지 않는다.

![02 Python 버전](evidence/02_python_version.png)

**③ 문법 및 외부 라이브러리 제약 확인**

```powershell
Select-String -Path .\main.py -Pattern 'numpy|pandas|torch|tensorflow'
python -m py_compile .\main.py
```

검색 결과가 없으므로 컴파일 오류가 없는 것으로 확인했다.

![03 소스 검증](evidence/03_source_validation.png)

### 3.2 데이터 구조·MAC·라벨·epsilon 검증 — 요구사항 4

**④ CPU 기본 MAC 계산**

```powershell
Select-String -Path .\main.py -Pattern '^def mac\(|^def validate_matrix\('
python -c "from main import mac; p=[[0,1,0],[1,1,1],[0,1,0]]; x=[[1,0,1],[0,1,0],[1,0,1]]; print('Cross:',mac(p,p)); print('X:',mac(p,x))"
```

Cross와 Cross의 점수는 5, Cross와 X의 점수는 1이어야 한다. 정수 `5` 또는 실수 `5.0`은 같은 점수다.

![04 MAC 계산](evidence/04_mac_calculation.png)

**⑤ 라벨 정규화**

```powershell
python -c "from main import normalize_label; print(normalize_label('+')); print(normalize_label('cross')); print(normalize_label('x')); print(normalize_label(' X '))"
```

예상 출력: `Cross`, `Cross`, `X`, `X`.

![05 라벨 정규화](evidence/05_label_normalization.png)

**⑥ epsilon 동점 정책**

```powershell
python -c "from main import decide; print(decide(0.9,0.8999999999999999)); print(decide(5.0,1.0))"
```

예상 출력: `UNDECIDED`, `Cross`. 현재 코드의 판정은 `math.isclose(..., rel_tol=0.0, abs_tol=1e-9)`이다.

![06 epsilon 동점 판정](evidence/06_epsilon_policy.png)

### 3.3 모드 1: 사용자 입력 3×3 — 요구사항 4 및 재현성

**⑦ 실행 및 필터 입력**

```powershell
python main.py
```

메뉴에서 `1`을 선택하고 다음을 순서대로 입력한다.

필터 A (Cross):

```text
0 1 0
1 1 1
0 1 0
```

필터 B (X):

```text
1 0 1
0 1 0
1 0 1
```

![07 모드1 필터 입력](evidence/07_mode1_filters.png)

**⑧ 패턴 입력 및 판정**

패턴으로 X를 입력한다.

```text
1 0 1
0 1 0
1 0 1
```

A 점수 1, B 점수 5, 판정 B가 나왔다.

![08 모드1 MAC 결과](evidence/08_mode1_mac_result.png)

**⑨ 잘못된 입력 및 재입력 확인**

다시 `python main.py`를 실행하고 `1`을 선택했다. 필터 첫 행에 `0 1`(열 수 부족)을 입력하고 오류 메시지를 확인했다. 다시 시작된 배열 입력에서 `0 A 0`(숫자 파싱 오류)을 입력해 오류 및 재입력 안내를 확인. 이 모드는 잘못 입력한 **배열 전체**를 처음부터 다시 입력받는다.

![09 모드1 입력 오류](evidence/09_mode1_input_error.png)

### 3.4 모드 2: JSON 로드·스키마 검증·판정 — 요구사항 4

**⑩ JSON 파일 문법과 키 확인**

```powershell
python -m json.tool .\data.json > $null
python -c "import json; d=json.load(open('data.json',encoding='utf-8')); print('filters:',list(d['filters'])); print('patterns:',list(d['patterns']))"
```

`filters`에 `size_5`, `size_13`, `size_25`가 있는지, `patterns`의 키가 `size_N_idx` 형식인지 확인한다.

![10 JSON 구조](evidence/10_json_structure.png)

**⑪ 필터 로드**

```powershell
python main.py
```

메뉴에서 `2`를 선택한다. 5×5, 13×13, 25×25 Cross/X 필터가 로드되는지 확인한다.

![11 JSON 필터 로드](evidence/11_json_filter_load.png)

**⑫ 케이스별 MAC 점수와 PASS/FAIL**

각 패턴의 Cross 점수, X 점수, 판정, expected, PASS/FAIL을 캡처한다. 데이터의 `+`와 `x`는 각각 `Cross`와 `X`로 정규화한다.

![12 JSON 패턴 결과](evidence/12_json_pattern_results.png)

**⑬ 전체 결과 요약**

제공된 원본 `data.json`을 기준으로 전체 6개, PASS 3개, FAIL 3개가 나왔다. 실패 식별자는 `size_5_1`, `size_13_2`, `size_25_1`이며 모두 epsilon 동점으로 `UNDECIDED`가 반환된 경우다. 원본 expected나 필터 가중치를 임의로 수정하지 않는다.

![13 JSON 결과 요약](evidence/13_json_summary.png)

**⑭ 크기 불일치 오류를 의도적으로 발생시키고 복원**

원본을 백업한다.

```powershell
Copy-Item .\data.json .\data_backup.json
```

테스트용으로 `size_5_1` 입력의 첫 행을 제거한다.

```powershell
@'
import json
with open('data.json', encoding='utf-8') as f:
    data = json.load(f)
data['patterns']['size_5_1']['input'].pop(0)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
'@ | python -
```

`python main.py`를 실행하고 메뉴 `2`를 선택한다. 해당 케이스만 데이터/스키마 오류로 FAIL 처리하고 나머지 케이스를 계속 검사하는지 확인했다.

![14 JSON 스키마 오류](evidence/14_json_schema_error.png)

**캡처 직후 원본을 반드시 복원한다.**

```powershell
Copy-Item .\data_backup.json .\data.json -Force
Remove-Item .\data_backup.json
python -m json.tool .\data.json > $null
```

### 3.5 크기별 성능 분석 — 요구사항 4, 과제 목표 3

**⑮ 10회 평균 시간과 N² 연산 횟수**

```powershell
python -c "from main import performance; performance()"
```

| 크기 | 연산 횟수 N² | 평균 실행 시간(ms) |
|---|---:|---|
| 3×3 | 9 | 실제 측정값 기록 |
| 5×5 | 25 | 실제 측정값 기록 |
| 13×13 | 169 | 실제 측정값 기록 |
| 25×25 | 625 | 실제 측정값 기록 |

측정은 각 크기별 10회 반복의 평균이며, 입력·출력·파일 읽기 시간을 제외한 MAC 함수 실행 구간을 대상으로 한다. 

![15 성능 분석](evidence/15_performance_analysis.png)

### 3.6 보너스 1: 2D → 1D 최적화 — 요구사항 5

**⑯ 배열 변환 확인**

```powershell
Select-String -Path .\main.py -Pattern '^def flatten\(|^def mac_flat\(|^def bonus_benchmark\('
python -c "from main import flatten; print(flatten([[1,2,3],[4,5,6],[7,8,9]]))"
```

예상 출력: `[1, 2, 3, 4, 5, 6, 7, 8, 9]`.

![16 1차원 변환](evidence/16_flatten_conversion.png)

**⑰ 동일 데이터·동일 반복 횟수 성능 비교**

```powershell
python main.py
```

메뉴 `4`를 선택한다. 2D/1D 평균 시간, 속도비, 점수 일치 여부를 확인한다. 1D와 2D의 평균처리시간은 4번 실험해본 결과 항상 1D가 빠르다.

![17 2D 1D 벤치마크](evidence/17_2d_1d_benchmark.png)

### 3.7 보너스 2: Cross/X 패턴 생성 — 요구사항 5

**⑱ 홀수 크기 패턴 생성**

```powershell
python main.py
```

메뉴 `3`을 선택하고 `5`를 입력한다. Cross는 가운데 행/열이 1이고 X는 양 대각선이 1인지 확인한다. 이 생성 함수는 성능 분석에서도 재사용된다.

![18 패턴 생성기](evidence/18_pattern_generator.png)

**⑲ 짝수 크기 입력 오류 확인**

다시 `python main.py` → 메뉴 `3` → 크기 `4`를 입력한다. `3 이상의 홀수` 안내와 함께 오류가 처리되는지 확인한다.

![19 잘못된 패턴 크기](evidence/19_generator_invalid_size.png)

### 3.8 결과 리포트 및 최종 검증 — 요구사항 4, 7

**⑳ 원본 데이터 복원 및 최종 실행**

```powershell
python -m py_compile .\main.py
python -m json.tool .\data.json > $null
python main.py
```

메뉴 `2`를 선택해 원본 6개 케이스의 최종 결과를 확인한다.

![20 최종 검증](evidence/20_final_validation.png)

### 3.9 Git/GitHub 제출 및 재현성 확인

**㉑ Git 커밋 및 Push**

```powershell
git status
git remote -v
git add main.py data.json README.md evidence/
git commit -m "Complete Mission 3 MAC simulator and evidence"
git push -u origin main
```

Push가 실패하면 저장소 존재 여부, 접근 권한, 현재 브랜치, 원격 URL을 확인한다.

![21 Git 업로드](evidence/21_git_push.png)

**㉒ GitHub에서 증거 링크 확인**

GitHub 저장소의 README에서 이미지가 실제 표시되는지, `evidence` 폴더에 PNG가 올라갔는지 확인한다. `git status`, `git log -1 --oneline`, `git remote -v`로 최종 상태를 재확인한다.

![22 GitHub 증거자료 확인](evidence/22_github_evidence.png)

## 4. 결과 리포트

### 4.1 JSON 분석 결과 (제공 원본 데이터 기준)

| 케이스 | Cross 점수 | X 점수 | 판정 | expected | 결과 |
|---|---:|---:|---|---|---|
| size_5_1 | 0.9 | 0.9 | UNDECIDED | X | FAIL |
| size_5_2 | 8.9 | 0.1 | Cross | Cross | PASS |
| size_13_1 | 0.3 | 14.7 | X | X | PASS |
| size_13_2 | 7.5 | 7.5 | UNDECIDED | Cross | FAIL |
| size_25_1 | 4.9 | 4.9 | UNDECIDED | X | FAIL |
| size_25_2 | 52.9 | 0.1 | Cross | Cross | PASS |
| **합계** | | | | | **6건 중 PASS 3, FAIL 3** |

### 4.2 실패 원인 분석 및 개선 정책 (10줄 이상)

1. `size_5_1`은 Cross와 X 점수가 모두 0.9이므로 epsilon 동점 정책에 따라 `UNDECIDED`가 된다.
2. 해당 케이스의 예상 라벨은 X이므로 `UNDECIDED != X`가 되어 FAIL이다.
3. `size_13_2`도 두 점수가 7.5로 같아 `UNDECIDED`가 된다.
4. 해당 케이스의 예상 라벨은 Cross이므로 FAIL이다.
5. `size_25_1`도 두 점수가 4.9로 같아 `UNDECIDED`가 된다.
6. 해당 케이스의 예상 라벨은 X이므로 FAIL이다.
7. 이 세 FAIL은 배열 크기 불일치나 JSON 파싱 오류가 아니라 **동점 판정 정책과 기대 라벨 사이의 불일치**이다.
8. `math.isclose`는 부동소수점 표현 오차가 매우 작은 경우도 동점으로 처리하도록 한다.
9. 허용오차가 없으면 `0.9`와 `0.8999999999999999`처럼 사실상 같은 값을 다른 점수로 판단할 수 있다.
10. 라벨 정규화는 `+`·`cross`·`x` 같은 서로 다른 표기를 `Cross`·`X`로 통일한다.
11. 라벨 표기 오류와 수치 비교 오류는 서로 다른 문제이므로 실패 원인을 구분해야 한다.
12. 배열의 행/열 개수가 맞지 않는 경우에는 케이스별 스키마 오류로 처리하여 전체 분석이 중단되지 않도록 한다.
13. 원본 expected나 필터 가중치를 임의로 바꿔 PASS 수를 늘리는 것은 검증의 목적에 맞지 않는다.
14. 향후 개선은 오류 유형별 집계, 동점 케이스에 대한 별도 평가 기준 마련, 경계값 테스트 추가를 중심으로 검토한다.

### 4.3 시간 복잡도 및 측정 해석

MAC 연산은 N×N 행렬의 모든 위치에서 한 번씩 곱셈을 수행하므로 곱셈 횟수는 N²이고 시간 복잡도는 **O(N²)**이다. 3×3은 9회, 5×5는 25회, 13×13은 169회, 25×25는 625회이다. 실측 시간은 반복문 실행 비용, 캐시, 운영체제 스케줄링, Python 인터프리터의 영향을 받는다. 따라서 N² 증가와 측정 시간의 비율이 정확히 같지 않을 수 있다. 실제 측정한 네 크기의 평균 시간을 3.5절 표에 기록하고 연산 횟수와 비교한다.

### 4.4 CPU 2D/1D 비교와 외부 라이브러리 제약

- **CPU 기본 MAC:** 이중 반복문으로 위치별 곱셈과 누적을 직접 구현한다.
- **CPU 1D MAC:** 같은 값을 1차원으로 펼쳐 접근하며, 2D/1D 시간은 동일한 반복 횟수로 측정한다. 변환 비용은 별도 고려한다.
- **NumPy:** 공식 과제에서 외부 라이브러리와 벡터화 MAC을 금지하므로 사용하지 않는다.

### 4.5 Mode 1과 Mode 2의 동점 처리 및 집계 정책

두 모드 모두 MAC 점수 비교에 동일한 허용오차(epsilon) 정책을 적용한다.

두 점수의 차이가 `1e-9` 미만이면 동점으로 판단하며, 내부 판정 결과는 `UNDECIDED`로 통일한다.

다만 모드별 목적이 다르므로 사용자에게 표시하는 문구와 결과 집계 방식에는 차이가 있다.

| 구분 | Mode 1: 사용자 입력 | Mode 2: JSON 분석 |
|---|---|---|
| 입력 데이터 | 사용자 입력 필터 A, B와 패턴 | data.json의 Cross, X 필터와 패턴 |
| 동점 기준 | `abs(A-B) < 1e-9` | `abs(Cross-X) < 1e-9` |
| 동점 출력 | 판정 불가 | UNDECIDED |
| 정답 비교 | 수행하지 않음 | expected와 비교 |
| 집계 정책 | PASS/FAIL 집계 없음 | 동점은 FAIL로 집계 |
| 실패 사유 | 두 필터 점수가 허용오차 범위 내에서 같음 | UNDECIDED가 expected와 일치하지 않음 |

Mode 1은 사용자가 직접 입력한 패턴을 두 필터 중 어느 쪽에 가까운지 판정하는 기능이다. 정답 라벨(expected)이 없으므로 동점이 발생하더라도 FAIL로 집계하지 않는다.

Mode 2는 JSON에 저장된 expected와 실제 판정을 비교하는 테스트 기능이다. 따라서 동점으로 `UNDECIDED`가 발생하면 expected가 Cross 또는 X인 경우 FAIL로 처리하고, 해당 케이스를 실패 목록에 포함한다.


### 4.6 새로운 라벨 추가 절차

현재 프로그램은 Cross와 X 두 가지 표준 라벨을 지원한다. 향후 새로운 라벨인 `O`를 추가하는 경우 다음 순서에 따라 기능을 확장한다.

| 단계 | 수정 대상 | 보완 내용 |
|---|---|---|
| 1. 정규화 | `normalize_label()` | `o`, `O`를 표준 라벨 `O`로 변환하도록 mapping 추가 |
| 2. 필터 | `data.json`, 필터 로딩 함수 | O 패턴에 대응하는 필터와 크기 검증 기능 추가 |
| 3. 판정 | MAC 점수 비교 함수 | Cross, X, O의 점수를 비교하고 최고 점수 라벨 선택 |
| 4. 출력 | 콘솔 결과 출력 | O 점수와 O 판정 결과 표시 |
| 5. 테스트 | 테스트 데이터 및 실행 결과 | O 정답, 오답, 동점, 잘못된 라벨 입력 검증 |

정규화 함수에는 다음과 같은 mapping을 추가한다.

```python
mapping = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
    "o": "O"
}
```

새 라벨을 추가하면 기존 두 필터 점수만 비교하던 판정 로직을 여러 필터의 점수를 비교할 수 있도록 확장해야 한다.

최고 점수가 하나이면 해당 라벨을 반환하고, 최고 점수와 다른 점수의 차이가 epsilon 미만이면 `UNDECIDED`를 반환하도록 한다.

새 라벨 추가 후에는 기존 Cross/X 테스트가 정상적으로 통과하는지도 함께 확인한다.

### 4.6 대규모 행렬 처리 문제와 최적화 우선순위

현재 프로그램은 3×3, 5×5, 13×13, 25×25 행렬을 처리한다. 향후 1000×1000 행렬을 처리하면 다음과 같은 문제가 예상된다.

| 분석 항목 | 25×25 | 1000×1000 |
|---|---:|---:|
| 원소 수 | 625 | 1,000,000 |
| 원소별 곱셈 횟수 | 625 | 1,000,000 |
| 연산량 증가 비율 | 기준 | 1,600배 |
| 시간 복잡도 | O(N²) | O(N²) |

1000×1000 행렬에서는 필터 하나와 입력 패턴 하나를 비교하기 위해 100만 번의 원소별 곱셈과 누적 연산이 필요하다.

또한 Python의 2차원 리스트는 행별 리스트와 원소 객체 참조를 저장하므로, 행렬이 커지면 메모리 사용량과 접근 비용도 증가한다.

대규모 처리에 대비하여 다음 순서로 최적화를 적용한다.

1. **1차원 배열 변환:** 2차원 리스트를 1차원 리스트로 변환하여 접근 구조를 단순화한다. 기존 보너스 과제에서 성능을 비교한다.
2. **블록화(Block Processing):** 행렬을 일정한 크기의 블록으로 나누어 처리한다. 작업 단위를 관리하고 메모리 접근 특성을 개선할 수 있는지 검증한다.
3. **중간 데이터 최소화:** 불필요한 배열 복사와 반복적인 데이터 변환을 줄여 메모리 사용량을 절감한다.
4. **병렬 처리 검토:** 서로 독립적인 연산을 여러 작업으로 나누어 처리한다. 다만 Python에서는 작업 생성과 데이터 전달 비용이 발생하므로 실제 성능 측정이 필요하다.
5. **성능 측정 및 비교:** 각 최적화 단계에서 실행 시간과 메모리 사용량을 측정하고 개선 효과를 확인한다.

블록화나 병렬화가 모든 환경에서 성능 향상을 보장하는 것은 아니다. 특히 단일 MAC 계산은 연산량에 비해 병렬 작업 관리 비용이 클 수 있으므로 측정 결과에 따라 적용 여부를 결정한다.

### 4.7 CPU와 NPU의 처리 구조 및 병목 비교

CPU와 NPU는 모두 MAC 연산을 수행할 수 있지만, 연산 구조와 주요 병목 요인에 차이가 있다.

| 비교 항목 | CPU | NPU |
|---|---|---|
| 설계 목적 | 다양한 범용 연산 처리 | 신경망의 대량 행렬 연산 처리 |
| 연산 방식 | 범용 코어 중심, 순차 실행 및 제한적 병렬 실행 | 다수의 MAC 연산기를 이용한 병렬 처리 |
| 강점 | 복잡한 제어, 조건 분기, 범용 작업 | 대규모 반복 곱셈·누적 연산 |
| 주요 병목 | 반복문 실행 비용, 명령 처리, 캐시 미스, 메모리 접근 | 메모리 대역폭, 데이터 이동, 연산기 활용률 |
| 성능 개선 방향 | 반복문 최적화, 데이터 구조 개선, 병렬 처리 | 데이터 재사용, 병렬 연산기 활용, 메모리 전송 최적화 |

CPU는 다양한 명령을 처리하도록 설계되어 있다. 현재 Mission 3 프로그램은 Python 이중 반복문을 사용하므로 각 원소에 접근하고 곱셈 결과를 누적하는 과정에서 Python 실행 비용이 발생한다.

다만 실제 CPU 자체가 순차 처리만 수행하는 것은 아니다. 현대 CPU도 여러 코어와 SIMD 명령을 이용해 병렬 연산을 수행할 수 있다.

NPU는 다수의 MAC 연산기를 동시에 활용하도록 설계되어 대규모 행렬 연산에서 높은 처리량을 얻을 수 있다. 그러나 연산기에 데이터를 충분히 공급하지 못하면 메모리 대역폭이 병목이 된다.

예를 들어 1000×1000 행렬은 100만 개의 원소별 곱셈이 필요하다. 병렬 연산기가 많더라도 데이터를 메모리에서 읽어오는 속도가 느리거나 연산기 간 누적 결과를 합치는 비용이 크면 기대한 만큼 성능이 향상되지 않는다.

따라서 대규모 MAC 연산에서는 단순히 연산기 수를 늘리는 것뿐 아니라 데이터 배치, 메모리 접근, 데이터 재사용을 함께 고려해야 한다.

이번 Mission 3은 실제 NPU 하드웨어를 구동하는 프로젝트가 아니라 Python 반복문으로 MAC 연산 원리를 구현하는 교육용 시뮬레이터이다. 따라서 CPU와 NPU의 차이는 이론적 구조와 예상 병목을 중심으로 설명하며, 실제 NPU 성능을 측정했다고 주장하지 않는다.


## 5. 전체 증거자료 목록

| 번호 | 파일명 | 증명할 내용 |
|---:|---|---|
| 01 | `01_project_directory.png` | 프로젝트 폴더 구성 |
| 02 | `02_python_version.png` | Python 개발환경 |
| 03 | `03_source_validation.png` | 문법 및 라이브러리 제약 확인 |
| 04 | `04_mac_calculation.png` | MAC 연산 정확성 |
| 05 | `05_label_normalization.png` | 라벨 정규화 |
| 06 | `06_epsilon_policy.png` | 동점 판정 정책 |
| 07 | `07_mode1_filters.png` | 사용자 필터 입력 |
| 08 | `08_mode1_mac_result.png` | MAC 점수 및 판정 |
| 09 | `09_mode1_input_error.png` | 잘못된 입력 처리 |
| 10 | `10_json_structure.png` | JSON 구조 및 문법 |
| 11 | `11_json_filter_load.png` | 필터 로드 |
| 12 | `12_json_pattern_results.png` | 케이스별 PASS/FAIL |
| 13 | `13_json_summary.png` | 전체 테스트 결과 |
| 14 | `14_json_schema_error.png` | 배열 크기 오류 처리 |
| 15 | `15_performance_analysis.png` | 크기별 성능 측정 |
| 16 | `16_flatten_conversion.png` | 2D → 1D 변환 |
| 17 | `17_2d_1d_benchmark.png` | 최적화 전후 비교 |
| 18 | `18_pattern_generator.png` | Cross/X 자동 생성 |
| 19 | `19_generator_invalid_size.png` | 패턴 생성 오류 처리 |
| 20 | `20_final_validation.png` | 최종 실행 검증 |
| 21 | `21_git_push.png` | Git 커밋 및 업로드 |
| 22 | `22_github_evidence.png` | GitHub 증거자료 확인 |

## 6. 제출 전 최종 점검

- [v ] Python 3.8 이상이며 외부 라이브러리를 사용하지 않았다.
- [v] 3×3 입력과 행/열 수 및 숫자 파싱 오류 재입력을 검증했다.
- [v ] 원본 JSON의 필터와 패턴을 검증하고 케이스별 PASS/FAIL을 확인했다.
- [v ] epsilon 동점 정책과 FAIL 원인을 구분해 기록했다.
- [v ] 3×3, 5×5, 13×13, 25×25에 대해 10회 평균 성능을 측정했다.
- [v ] 2D/1D MAC 성능 비교와 Cross/X 생성기 보너스를 검증했다.
- [v ] README의 22개 이미지 링크와 실제 `evidence/*.png` 파일명이 일치한다.
- [v ] GitHub에서 README와 증거 이미지가 정상적으로 표시된다.
