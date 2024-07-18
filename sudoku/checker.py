import numpy as np

def check(answer,puzzle_size=3):
    answer = answer.replace('*', 'None').replace(' ', '')
    from ast import literal_eval
    try:
        result = literal_eval(answer)
    except SyntaxError:
        result = [[]]
    matrix=np.array(result, dtype=object)
    expected_set = set(range(1, puzzle_size + 1))

    for row in matrix:
        if set(row) != expected_set:
            return False
    for col in matrix.T:
        if set(col) != expected_set:
            return False
    return True

answer="[[1, 2, 3], [3, 1, 2], [2, 3, 1]]"
print(check(answer))