from models import *
import itertools
import random
from collections import Counter
import re
import numpy as np

def check(answer,args):
    answer = answer.replace('*', 'None').replace(' ', '')
    from ast import literal_eval
    try:
        result = literal_eval(answer)
    except SyntaxError:
        result = [[]]
    matrix=np.array(result, dtype=object)
    expected_set = set(range(1, args.puzzle_size + 1))

    for row in matrix:
        if set(row) != expected_set:
            return False
    for col in matrix.T:
        if set(col) != expected_set:
            return False
    return True

def check_duplicate(answer):
    copy_ans=answer
    copy_ans = copy_ans.replace('*', 'None').replace(' ', '')
    from ast import literal_eval
    try:
        result = literal_eval(copy_ans)
    except SyntaxError:
        return False
    matrix=np.array(result, dtype=object)
    for row in matrix:
        filtered_row = [item for item in row if item is not None]
        if len(filtered_row) != len(set(filtered_row)):
            return False
    for col in matrix.T:
        filtered_col = [item for item in col if item is not None]
        if len(filtered_col) != len(set(filtered_col)):
            return False
    return True

def get_proposals(round,z,args):
    input = f"This is a {args.puzzle_size}x{args.puzzle_size} two-dimensional array represents a matrix, \
        where some numbers are already given, and '*' represents the numbers that need to be filled in. \
        You should pick 1 or 2 '*' to fill in a number between 1 to {args.puzzle_size}. \
        Don't change the given number.\
        Don't complete the whole puzzle immediately until there is only 1 or 2 '*' left to be filled in. \
        Your answer should just be the same format as the question below. \
        When you answer, begin with ###. For example: ###[[1, *, *], [*, 1, *], [*, 2, *]]\n\
        Question: " + z
    proposals=[]
    for _ in range(args.n_generate_sample):
        proposal = gpt(input, model=args.backend)
        answer = proposal.split('###')[-1]
        proposals.append(answer)
    return proposals

def get_value(z, n, evaluate_time, backend):
    value_prompt = f"You should judge if the two two-dimensional is able to construct a {n}x{n} Sudoku.\
          For example, check if each number appears only once in each row or column.\
          0 means impossible. 1 means likely. 2 means sure. You must only reply with 0 or 1 or 2.\n"+z
    values=[]
    for _ in range (evaluate_time):
        value = gpt(value_prompt, model=backend)
        numbers = re.findall(r'\d+', value)
        if(len(numbers)>0):
            values.append(int(numbers[0]))
        else:
            values.append(1)
    value = sum(values)/len(values)
    return value

def get_values(zs, args):
    values = []
    local_value_cache = {}
    for z in zs:
        if z in local_value_cache:
            value = 0
        else:    
            value = get_value(z, args.puzzle_size, args.n_evaluate_time, args.backend)
            local_value_cache[z] = value
        values.append(value)
    return values

def compare(pair, n, evaluate_times, backend):
    compare_prompt=[]
    compare_prompt.append(f"You should judge which of the two two-dimensional array better represents a {n}x{n} Sudoku puzzle.\
        '*' means the value is yet to be decided.\
        You should judge by considering if in each row or column 1 to {n} could appear and only appear once.\
        You must only reply 1 or 2. If both inputs are equal, randomly print 1 or 2. \
        Don't explain or reply anything else.\n\
        1:" +pair[0]+"2:"+pair[1])
    compare_prompt.append(f"Find which of the two two-dimensional array better represents a {n}x{n} Sudoku puzzle.\
        '*' means the value hasn't been decided.\
        The better one should satisfy that in each row or column 1 to {n} could appear and only appear once.\
        You must only reply 1 or 2. If both inputs are equal, randomly print 1 or 2. \
        Don't explain or reply anything else.\n\
        1:" +pair[0]+"2:"+pair[1])
    compare_prompt.append(f"Which of the two two-dimensional array better represents a {n}x{n} Sudoku puzzle?\
        '*' means the value is yet to be decided.\
        A better one means in each row or column 1 to {n} could appear and only appear once.\
        You must only reply 1 or 2. If both inputs are equal, randomly print 1 or 2. \
        Don't explain or reply anything else.\n\
        1:" +pair[0]+"2:"+pair[1])
    values = []
    for i in range (evaluate_times):
        value_output=gpt(compare_prompt[i], model=backend)
        number = re.findall(r'\d+', value_output)
        if(len(number)):
            values.append(number[0])
        else:
            values.append(random.randint(1, 2))
    counter = Counter(values)
    result = counter.most_common(1)[0][0]
    return int(result) - 1

def get_comparison(zs, args, shuffle, select_num=3, evaluate_times = 1):
    compare_info = []
    not_selected_zs = []
    current_zs = zs
    while(len(current_zs)>select_num):
        if (shuffle):
            random.shuffle(current_zs)
        pairs = []
        new_zs = []
        for i in range(0, len(current_zs) - 1, 2):
            pairs.append(current_zs[i:i+2])
        if len(current_zs) % 2 != 0:
            new_zs.append(current_zs[-1])
        for pair in pairs:
            result = compare(pair,args.puzzle_size, evaluate_times, args.backend)
            new_zs.append(pair[result])
            not_selected_zs.append(pair[1-result])
            compare_info.append(f"Compare {pair[0]} and {pair[1]}, choose {result+1}.\n")
        current_zs = new_zs
    return current_zs, not_selected_zs, compare_info

def solve(question ,args, to_print):
    x = question
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    round = 0
    while round < max_round:
        round += 1
        new_zs = [get_proposals(round,z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        values = get_values(new_zs, args)
        
        continue_zs=[]
        sorted_new_zs, sorted_values = zip(*sorted(zip(new_zs, values), key=lambda x: x[1], reverse=True))
        for z in sorted_new_zs:
            if (check_duplicate(z)):
                continue_zs.append(z)
        continue_zs = continue_zs[:min(len(continue_zs),args.n_select_sample)]
        for z in continue_zs:
            if (check(z,args)):
                answers.append(z)
        if(len(answers)==0 and round==max_round):
            answers=continue_zs[0]
        
        if to_print: 
            print(f'-- new_zs --: {new_zs}\n-- choices --: {continue_zs}')
        print("round:",round)
        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs':sorted_new_zs, 'values':sorted_values, 'select_zs': continue_zs})
        zs = continue_zs
        if(len(answers)):
            break
        if(len(zs)==0):
            break
        
    if(len(answers)):
        print('Final answer: ',answers[0])
        return answers[0], {'steps': infos}
    else:
        return "",{'steps': infos}

def compare_solve(question ,args, to_print):
    x = question
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    round = 0
    while round < max_round:
        round += 1
        new_zs = [get_proposals(round,z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        
        continue_zs=[]
        selected_zs, not_selected_zs, compare_info = get_comparison(new_zs, args, shuffle = args.shuffle, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)
        for z in selected_zs:
            if (check_duplicate(z)):
                continue_zs.append(z)
        for z in continue_zs:
            if (check(z,args)):
                answers.append(z)
        if(len(answers)==0 and round==max_round):
            answers=continue_zs[0]
        
        if to_print: 
            print(f'-- new_zs --: {new_zs}\n-- choices --: {continue_zs}')
        print("round:",round)
        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs':new_zs, 'compare_info':compare_info, 'select_zs': continue_zs})
        zs = continue_zs
        if(len(answers)):
            break
        if(len(zs)==0):
            break
        
    if(len(answers)):
        print('Final answer: ',answers[0])
        return answers[0], {'steps': infos}
    else:
        return "",{'steps': infos}

def duel_solve(question ,args, to_print):
    x = question
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    remained_zs=[]
    round = 0
    while round < max_round:
        round += 1
        new_zs = [get_proposals(round,z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        
        selected_zs, not_selected_zs, compare_info = get_comparison(new_zs, args, shuffle = args.shuffle, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)
        continue_zs=[]
        for z in selected_zs:
            if (check_duplicate(z)):
                continue_zs.append(z)
        for z in not_selected_zs:
            if (check_duplicate(z)):
                remained_zs.append(z)
        if(len(continue_zs)<args.n_select_sample):
            length=min(len(remained_zs),args.n_select_sample-len(continue_zs))
            continue_zs=continue_zs+remained_zs[-length:]
            remained_zs=remained_zs[:-length]
        for z in continue_zs:
            if (check(z,args)):
                answers.append(z)

        if(len(answers)==0 and round==max_round):
            answer, _, last_info=get_comparison(continue_zs, args, shuffle = args.shuffle, select_num=1, evaluate_times = args.n_evaluate_time)
            compare_info = compare_info + last_info
            answers=answer
        
        if to_print: 
            print(f'-- new_zs --: {new_zs}\n-- choices --: {continue_zs}')

        print("round:",round)
        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs':new_zs, 'compare_info':compare_info, 'select_zs': continue_zs, 'remain_zs':remained_zs})
        zs = continue_zs
        if(len(continue_zs)==0):
            zs=[x]
        if(len(answers)):
            break
        
    if(len(answers)):
        print('Final answer: ',answers[0])
        return answers[0], {'steps': infos}
    else:
        return "",{'steps': infos}

def back_solve(question ,args, to_print):
    x = question
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    remained_zs=[]
    remained_values=[]
    round = 0
    while round < max_round:
        round += 1
        new_zs = [get_proposals(round,z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        values = get_values(new_zs, args)
        sorted_zs, sorted_values = zip(*sorted(zip(new_zs+remained_zs, values+remained_values), key=lambda x: x[1], reverse=True))
        selected_zs=[]
        selected_values=[]
        num=0
        for z,value in zip(sorted_zs, sorted_values):
            if (check_duplicate(z)) and num<args.n_select_sample:
                selected_zs.append(z)
                selected_values.append(value)
            elif (check_duplicate(z)) and num>=args.n_select_sample:
                remained_zs.append(z)
                remained_values.append(value)
            num+=1
                
        for z in selected_zs:
            if (check(z,args)):
                answers.append(z)
        
        if to_print: 
            print(f'-- new_zs --: {new_zs}\n-- choices --: {selected_zs}')

        print("round:",round)
        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs':new_zs, 'values':values, 'sorted_zs':sorted_zs, 'sorted_values':sorted_values, 'select_zs': selected_zs, 'selected_values': selected_values})
        zs = selected_zs
        if(len(selected_zs)==0):
            zs=[x]
        if(len(answers)):
            break
        
    if(len(answers)):
        print('Final answer: ',answers[0])
        return answers[0], {'steps': infos}
    else:
        return "",{'steps': infos}
