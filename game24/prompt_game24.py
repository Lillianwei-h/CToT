# 5-shot
standard_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24.
Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) = 24
Input: 2 9 10 12
Answer: 2 * 12 * (10 - 9) = 24
Input: 4 9 10 13
Answer: (13 - 9) * (10 - 4) = 24
Input: 1 4 8 8
Answer: (8 / 4 + 1) * 8 = 24
Input: 5 5 5 9
Answer: 5 + 5 + 5 + 9 = 24
Input: {input}
'''

# 5-shot
cot_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24. Each step, you are only allowed to choose two of the remaining numbers to obtain a new number.
Input: 4 4 6 8
Steps:
4 + 8 = 12 (left: 4 6 12)
6 - 4 = 2 (left: 2 12)
2 * 12 = 24 (left: 24)
Answer: (6 - 4) * (4 + 8) = 24
Input: 2 9 10 12
Steps:
12 * 2 = 24 (left: 9 10 24)
10 - 9 = 1 (left: 1 24)
24 * 1 = 24 (left: 24)
Answer: (12 * 2) * (10 - 9) = 24
Input: 4 9 10 13
Steps:
13 - 10 = 3 (left: 3 4 9)
9 - 3 = 6 (left: 4 6)
4 * 6 = 24 (left: 24)
Answer: 4 * (9 - (13 - 10)) = 24
Input: 1 4 8 8
Steps:
8 / 4 = 2 (left: 1 2 8)
1 + 2 = 3 (left: 3 8)
3 * 8 = 24 (left: 24)
Answer: (1 + 8 / 4) * 8 = 24
Input: 5 5 5 9
Steps:
5 + 5 = 10 (left: 5 9 10)
10 + 5 = 15 (left: 9 15)
15 + 9 = 24 (left: 24)
Answer: ((5 + 5) + 5) + 9 = 24
Input: {input}
'''

# 1-shot
propose_prompt = '''You should choose two of the input numbers and use basic arithmetic operations (+ - * /) to obtain a new number. The new number should replace those two input numbers. Give me at least 6 possible next steps.
Input: 2 8 8 14
Possible next steps:
2 + 8 = 10 (left: 8 10 14)
8 / 2 = 4 (left: 4 8 14)
14 + 2 = 16 (left: 8 8 16)
2 * 8 = 16 (left: 8 14 16)
8 - 2 = 6 (left: 6 8 14)
14 - 8 = 6 (left: 2 6 8)
14 /  2 = 7 (left: 7 8 8)
14 - 2 = 12 (left: 8 8 12)
Input: {input}
Possible next steps:
'''

value_prompt_1 = '''Evaluate if given numbers can use basic arithmetic operations (+ - * /) to reach 24. You must only reply: sure/likely/impossible.
10 14
10 + 14 = 24
sure
11 12
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
impossible
4 4 10
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
sure
4 9 11
9 + 11 + 4 = 20 + 4 = 24
sure
5 7 8
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but numbers are within a reasonable range
likely
5 6 6
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but numbers are within a reasonable range
likely
10 10 11
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
impossible
1 3 3
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
impossible
{input}
'''

value_prompt = '''Evaluate if given numbers can use basic arithmetic operations (+ - * /) to reach 24. You should only reply with (sure/likely/impossible).
2 12
2 * 12 = 24
sure
3 8
3 * 8 =24
sure
4 6
4 * 6 = 24
sure
12 12
12 + 12 = 24
sure
11 12
all arithmetic operations can't reach 24
impossible
1 2 4
too small
impossible
10 6 6
10 - 6 = 4
4 * 6 = 24
sure
12 5 10
10 / 5 = 2
12 * 2 = 24
sure
1 12 11
1 + 12 + 11 = 24
sure
11 13 10
(13 - 11) * 10 = 20
11 / 10 * 13 = 14.3
Can't obtain 24 now, but numbers are within a reasonable range
likely
{input}
'''

value_last_step_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24. Given an input and an answer, give a judgement (sure/impossible) if the answer is correct, i.e. it uses each input exactly once and no other numbers, and reach 24.
Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) = 24
Judge: 
sure
Input: 2 9 10 12
Answer: 2 * 12 * (10 - 9) = 24
Judge: 
sure
Input: 4 9 10 13
Answer: (13 - 9) * (10 - 4) = 24
Judge: 
sure
Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) + 1 = 25
Judge: 
impossible
Input: 2 9 10 12
Answer: 2 * (12 - 10) = 24
Judge: 
impossible
Input: 4 9 10 13
Answer: (13 - 4) * (10 - 9) = 24
Judge: 
impossible
Input: {input}
Answer: {answer}
Judge:'''

compare_prompt=[]
compare_prompt.append('''I will give you two groups of numbers. The evaluation criteria is if using all of the given numbers with basic arithmetic operations (+ - * /) can reach 24. You should compare the two inputs and decide which input is better. You should only reply 1 or 2. Don't add any explanation. If both inputs are equal, randomly select 1 or 2 as your answer.
input_1: 2 12
2 * 12 = 24
input_2: 11 12
all arithmetic operations can't reach 24
Answer: 1
input_1: 1 2 4
too small
input_2: 3 8
3 * 8 =24
Answer: 2
input_1: 4 6
4 * 6 = 24
input_2: 11 13 10
(13 - 11) * 10 = 20
Answer: 1
input_1: 1 12 11
1 + 12 + 11 = 24
input_2: 12 12
12 + 12 = 24
Both can reach 24, randomly select one
Answer: 1
input_1: {input_1}
input_2: {input_2}
Answer: 
''')

compare_prompt.append('''I will give you two groups of numbers. Tell me which input is better. The better one is more possible to reach 24 by using all of the given numbers with basic arithmetic operations (+ - * /). You should only reply 1 or 2. Don't add any explanation. If both inputs are equal, randomly select 1 or 2 as your answer.
input_1: 3 8
3 * 8 = 24
input_2: 7 12
all arithmetic operations can't reach 24
Answer: 1
input_1: 1 3 4
too small
input_2: 1 3 7
3 * (1 + 7) = 24
Answer: 2
input_1: 5 6 6
5 * 6 - 6 = 24
input_2: 13 10 2
(13 - 2) * 10 = 22
Answer: 1
input_1: 4 8 2
(4 + 8) * 2 = 24
input_2: 11 13
11 + 13 = 24
Both can reach 24, randomly select one
Answer: 1
input_1: {input_1}
input_2: {input_2}
Answer: 
''')

compare_prompt.append('''I will give you two groups of numbers. Tell me which input is better. The better one is more possible to reach 24 by using all of the given numbers with basic arithmetic operations (+ - * /). You should only reply 1 or 2. Don't add any explanation. If both inputs are equal, randomly select 1 or 2 as your answer.
input_1: 1 2 4
too small
input_2: 3 8
3 * 8 =24
Answer: 2
input_1: 2 12
2 * 12 = 24
input_2: 11 12
all arithmetic operations can't reach 24
Answer: 1
input_1: 1 12 11
1 + 12 + 11 = 24
input_2: 12 12
12 + 12 = 24
Both can reach 24, randomly select one
Answer: 1
input_1: 4 6
4 * 6 = 24
input_2: 11 13 10
(13 - 11) * 10 = 20
Answer: 1
input_1: {input_1}
input_2: {input_2}
Answer: 
''')