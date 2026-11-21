import json
import math
import re
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
EPSILON = 1e-9
REPEAT = 10
SIZES = (3, 5, 13, 25)


def generate_pattern(n, label):
    if n < 3 or n % 2 == 0:
        raise ValueError('패턴 크기는 3 이상의 홀수여야 합니다.')
    label = normalize_label(label)
    center = n // 2
    return [[int((r == center or c == center) if label == 'Cross' else (r == c or r + c == n - 1)) for c in range(n)] for r in range(n)]


def normalize_label(value):
    if not isinstance(value, str):
        raise ValueError('라벨은 문자열이어야 합니다.')
    label = value.strip().lower()
    mapping = {'+': 'Cross', 'cross': 'Cross', 'x': 'X'}
    if label not in mapping:
        raise ValueError(f'알 수 없는 라벨: {value!r}')
    return mapping[label]


def validate_matrix(matrix, n, name='배열'):
    if not isinstance(matrix, list) or len(matrix) != n:
        raise ValueError(f'{name}: 행 수가 {n}이 아닙니다.')
    for i, row in enumerate(matrix, 1):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(f'{name}: {i}행 열 수가 {n}이 아닙니다.')
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'{name}: 유한한 숫자만 허용합니다.')
    return matrix


def mac(pattern, filt):
    n = len(pattern)
    return sum(pattern[r][c] * filt[r][c] for r in range(n) for c in range(n))


def mac_flat(pattern, filt):
    return sum(a * b for a, b in zip(pattern, filt))


def flatten(matrix):
    return [value for row in matrix for value in row]


def decide(a, b, first='Cross', second='X'):
    if math.isclose(a, b, rel_tol=0.0, abs_tol=EPSILON):
        return 'UNDECIDED'
    return first if a > b else second


def measure(func, *args, repeat=REPEAT):
    start = time.perf_counter()
    for _ in range(repeat):
        func(*args)
    return (time.perf_counter() - start) * 1000 / repeat


def read_matrix(name, n=3):
    while True:
        print(f'{name} ({n}줄, 각 줄 {n}개 숫자)')
        rows = []
        valid = True
        for i in range(n):
            line = input(f'  {i + 1}행: ')
            parts = line.split()
            if len(parts) != n:
                valid = False
                print(f'입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.')
                break
            try:
                row = [float(x) for x in parts]
                if not all(math.isfinite(x) for x in row):
                    raise ValueError
                rows.append(row)
            except ValueError:
                valid = False
                print('입력 형식 오류: 유한한 숫자만 입력하세요.')
                break
        if valid:
            return rows
        print('해당 배열을 처음부터 다시 입력하세요.')


def performance(filters=None):
    print('\n[성능 분석: 2차원 MAC, 평균/10회]')
    print(f'{"크기":<10}{"평균 시간(ms)":>17}{"연산 횟수":>14}')
    for n in SIZES:
        p = generate_pattern(n, 'Cross')
        f = (filters or {}).get(n, {}).get('Cross', generate_pattern(n, 'Cross'))
        print(f'{n}x{n:<7}{measure(mac, p, f):>17.6f}{n*n:>14}')


def bonus_benchmark():
    print('\n[보너스 1: 동일 데이터/10회, 2차원 vs 1차원 MAC]')
    print(f'{"크기":<9}{"2D(ms)":>13}{"1D(ms)":>13}{"속도비(2D/1D)":>17}{"점수 일치":>12}')
    for n in SIZES:
        p, f = generate_pattern(n, 'Cross'), generate_pattern(n, 'X')
        pf, ff = flatten(p), flatten(f)
        t2, t1 = measure(mac, p, f), measure(mac_flat, pf, ff)
        equal = math.isclose(mac(p, f), mac_flat(pf, ff), rel_tol=0, abs_tol=EPSILON)
        print(f'{n}x{n:<6}{t2:>13.6f}{t1:>13.6f}{t2/t1 if t1 else 0:>17.2f}{str(equal):>12}')
    print('주의: 1차원 변환 시간은 측정에서 제외하며, 성능 우위는 환경에 따라 달라집니다.')


def mode_user():
    print('\n[1] 필터 입력')
    a = read_matrix('필터 A')
    b = read_matrix('필터 B')
    print('필터 A/B 저장 확인: 각 3x3 배열')
    print('\n[2] 패턴 입력')
    p = read_matrix('패턴')
    sa, sb = mac(p, a), mac(p, b)
    print('\n[3] MAC 결과')
    print(f'A 점수: {sa:.12g} | B 점수: {sb:.12g}')
    print(f'연산 시간(두 MAC 합계, 평균/10회): {measure(lambda: (mac(p, a), mac(p, b))):.6f} ms')
    print(f'판정: {decide(sa, sb, "A", "B")}')
    performance()


def parse_filters(data):
    result, errors = {}, {}
    raw = data.get('filters')
    if not isinstance(raw, dict):
        return result, {'전체': 'filters는 객체여야 합니다.'}
    for n in (5, 13, 25):
        key = f'size_{n}'
        try:
            obj = raw[key]
            if not isinstance(obj, dict):
                raise ValueError('필터 항목은 객체여야 합니다.')
            normalized = {}
            for label, matrix in obj.items():
                standard = normalize_label(label)
                if standard in normalized:
                    raise ValueError(f'중복 라벨: {standard}')
                normalized[standard] = validate_matrix(matrix, n, key + '/' + label)
            if set(normalized) != {'Cross', 'X'}:
                raise ValueError('Cross와 X 필터가 모두 필요합니다.')
            result[n] = normalized
            print(f'✓ {key} 필터 로드 완료 (Cross, X)')
        except (KeyError, ValueError, TypeError) as exc:
            errors[n] = str(exc)
            print(f'✗ {key} 필터 오류: {exc}')
    return result, errors


def mode_json():
    print('\n[1] 필터 로드')
    try:
        with (BASE / 'data.json').open('r', encoding='utf-8') as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError('최상위 JSON은 객체여야 합니다.')
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f'data.json 로드 실패: {exc}')
        return
    filters, errors = parse_filters(data)
    patterns = data.get('patterns')
    if not isinstance(patterns, dict):
        print('patterns는 객체여야 합니다. 분석을 종료합니다.')
        return
    passed, failures = 0, []
    print('\n[2] 패턴 분석')
    for key, item in patterns.items():
        print(f'--- {key} ---')
        try:
            match = re.fullmatch(r'size_(\d+)_(\d+)', key)
            if not match:
                raise ValueError('패턴 키 형식 오류: size_N_idx 필요')
            n = int(match.group(1))
            if n not in (5, 13, 25):
                raise ValueError(f'지원하지 않는 크기: {n}')
            if n in errors:
                raise ValueError(f'필터 오류: {errors[n]}')
            if not isinstance(item, dict):
                raise ValueError('패턴 항목은 객체여야 합니다.')
            expected = normalize_label(item['expected'])
            p = validate_matrix(item['input'], n, key)
            cross, x = mac(p, filters[n]['Cross']), mac(p, filters[n]['X'])
            actual = decide(cross, x)
            ok = actual == expected
            print(f'Cross 점수: {cross:.12g} | X 점수: {x:.12g}')
            print(f'판정: {actual} | expected: {expected} | {"PASS" if ok else "FAIL"}')
            if not ok:
                reason = 'epsilon 동점(UNDECIDED)' if actual == 'UNDECIDED' else '예상 라벨과 판정 불일치'
                failures.append((key, reason))
            else:
                passed += 1
        except (KeyError, ValueError, TypeError) as exc:
            failures.append((key, f'데이터/스키마 오류: {exc}'))
            print(f'FAIL: {exc}')
    performance(filters)
    print('\n[4] 결과 요약')
    print(f'총 테스트: {len(patterns)}개 | 통과: {passed}개 | 실패: {len(failures)}개')
    if failures:
        print('실패 케이스:')
        for key, reason in failures:
            print(f'- {key}: {reason}')
    else:
        print('실패 케이스: 없음')


def mode_generator():
    try:
        n = int(input('생성할 홀수 크기 N (3 이상): '))
        for label in ('Cross', 'X'):
            print(f'\n{label} ({n}x{n})')
            for row in generate_pattern(n, label):
                print(' '.join(map(str, row)))
        print('생성 함수 generate_pattern()은 성능 분석에서도 재사용됩니다.')
    except ValueError as exc:
        print(f'입력 오류: {exc}')


def main():
    print('=== Mini NPU Simulator ===')
    print('1. 사용자 입력 (3x3)\n2. data.json 분석\n3. 보너스: 패턴 생성기\n4. 보너스: 1D 최적화 성능 비교')
    choice = input('선택: ').strip()
    if choice == '1':
        mode_user()
    elif choice == '2':
        mode_json()
    elif choice == '3':
        mode_generator()
    elif choice == '4':
        bonus_benchmark()
    else:
        print('1~4 중 하나를 선택하세요.')


if __name__ == '__main__':
    main()
