import itertools
from functools import partial
from models import gpt
import random
from collections import Counter
from game24 import get_current_numbers
import re

def get_value(task, x, y, evaluate_times, backend, cache_value=True):
    value_prompt = task.value_prompt_wrap(x, y)
    if cache_value and value_prompt in task.value_cache:
        return task.value_cache[value_prompt]
    values=[]
    for _ in range (evaluate_times):
        value_outputs = gpt(value_prompt, model=backend)
        value = task.value_outputs_unwrap(x, y, value_outputs)
        if cache_value:
            task.value_cache[value_prompt] = value
        values.append(value)
    value = sum(values)/len(values)
    return value

def get_values(task, x, ys, evaluate_times, backend, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:
        if y in local_value_cache:
            value = 0
        else:    
            value = get_value(task, x, y, evaluate_times=evaluate_times, backend=backend, cache_value=cache_value)
            local_value_cache[y] = value
        values.append(value)
    return values

def compare(task, x, pair, evaluate_times, backend):
    num=[get_current_numbers(pair[0]),get_current_numbers(pair[1])]
    values = []
    for i in range (evaluate_times):
        compare_prompt = task.compare_prompt_wrap(x, num, i)
        value_output=gpt(compare_prompt, model = backend)
        number = re.findall(r'\d+', value_output[0])
        if(len(number) and number[0] in [1,2]):
            values.append(number[0])
        else:
            values.append(random.randint(1, 2))
    counter = Counter(values)
    result = counter.most_common(1)[0][0]
    return int(result) - 1

def get_comparison(task, x, ys, backend, select_num=1, evaluate_times = 1):
    compare_info = []
    not_selected_ys = []
    current_ys = ys
    while len(current_ys) > select_num:
        idx1, idx2 = random.sample(current_ys, 2)
        pair=[idx1, idx2]
        result = compare(task, x, pair, evaluate_times, backend)
        not_selected_ys.append(pair[1-result])
        current_ys.remove(pair[1-result])
        compare_info.append(f"Compare {pair[0]} and {pair[1]}, choose {pair[result]}.\n")
    return current_ys, not_selected_ys, compare_info

def get_proposals(task, x, y, args): 
    propose_prompt = task.propose_prompt_wrap(x, y)
    proposals = gpt(propose_prompt, model=args.backend).split('\n')
    return [y + _ + '\n' for _ in proposals]

def solve(args, task, idx, to_print=True):
    print("Index:",idx+1)
    x = task.get_input(idx)
    print("Task:",x)
    ys = [''] 
    infos = []
    for step in range(task.steps):
        new_ys = [get_proposals(task, x, y, args) for y in ys]
        new_ys = list(itertools.chain(*new_ys))
        
        values = get_values(task, x, new_ys, evaluate_times = args.n_evaluate_time, backend = args.backend)

        sorted_new_ys, sorted_values = zip(*sorted(zip(new_ys, values), key=lambda x: x[1], reverse=True))
        select_new_ys = sorted_new_ys[:args.n_select_sample]

        if to_print: 
            print(f'-- new_ys --: {sorted_new_ys}\n-- sol values --: {sorted_values}\n-- choices --: {select_new_ys}\n')
        
        infos.append({'step': step+1, 'x': x, 'ys': ys, 'new_ys': new_ys, 'values': values, 'select_new_ys': select_new_ys})
        ys = select_new_ys
    
    if to_print: 
        print(ys)
    return ys, {'steps': infos}

def compare_solve(args, task, idx, to_print=True):
    x = task.get_input(idx)
    print("Index:",idx+1)
    print("Task:",x)
    ys = ['']
    infos = []
    answers=[]
    for step in range(task.steps):
        new_ys = [get_proposals(task, x, y, args) for y in ys]
        new_ys = list(itertools.chain(*new_ys))
        continue_ys=[]
        for y in new_ys:
            last_line = y.strip().split('\n')[-1]
            if 'left: ' in last_line:
                nums = last_line.split('left: ')[-1].split(')')[0]
                numlist = nums.split()
                if len(numlist)!=1 or nums=='24':
                    continue_ys.append(y)
            else:
                answers.append(y)
        selected_ys, not_selected_ys, compare_info = get_comparison(task, x, continue_ys, backend=args.backend, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)

        if to_print: 
            print(f'-- new_ys --: {new_ys}\n-- choices --: {selected_ys}\n')
        
        infos.append({'step': step+1, 'x': x, 'ys': ys, 'new_ys': new_ys, 'compare_info': compare_info, 'selected_ys': selected_ys})
        ys = selected_ys
        if(len(ys)==0):
            break
    if to_print: 
        print(ys)
    return answers, {'steps': infos}


def back_solve(args, task, idx, to_print=True):
    print("Index: ",idx+1)
    x = task.get_input(idx)
    print("Task:",x)
    ys = ['']
    remained_ys = []
    remain_values = []
    infos = []
    round = 0
    while round < args.max_round:
        round += 1
        new_ys = [get_proposals(task, x, y, args) for y in ys]
        new_ys = list(itertools.chain(*new_ys))
        values = get_values(task, x, new_ys, evaluate_times = args.n_evaluate_time, backend = args.backend)
        new_ys = new_ys + remained_ys
        values = values + remain_values

        sorted_new_ys, sorted_values = zip(*sorted(zip(new_ys, values), key=lambda x: x[1], reverse=True))
        select_new_ys = sorted_new_ys[:args.n_select_sample]

        remained_ys = [item for item in new_ys if item not in select_new_ys and values[new_ys.index(item)]>0.001]
        remain_values = [values[new_ys.index(item)] for item in remained_ys]

        if to_print: 
            print(f'-- new_ys --: {sorted_new_ys}\n-- sol values --: {sorted_values}\n-- choices --: {select_new_ys}\n')
        
        infos.append({'round': round, 'x': x, 'ys': ys, 'new_ys': new_ys, 'values': values, 'select_new_ys': select_new_ys})
        ys = select_new_ys
        
        flag = False
        for y in ys:
            if ("Answer" in y):
                flag = True
                break
        if(flag):
            break
    
    if to_print: 
        print(ys)
    return ys, {'steps': infos}

def duel_solve(args, task, idx, to_print=True):
    x = task.get_input(idx)
    print("idx:",idx+1)
    print("Task:",x)
    ys = ['']
    remained_ys = []
    infos = []
    round = 0
    answers=[]
    while round < args.max_round:
        round += 1
        new_ys = [get_proposals(task, x, y, args) for y in ys]
        new_ys = list(itertools.chain(*new_ys))
        continue_ys=[]
        for y in new_ys:
            last_line = y.strip().split('\n')[-1]
            if 'left: ' in last_line:
                nums = last_line.split('left: ')[-1].split(')')[0]
                numlist = nums.split()
                if len(numlist)!=1 or nums=='24':
                    continue_ys.append(y)
            elif 'Answer' in last_line:
                continue_ys.append(y)

        if(len(continue_ys)<2*args.n_select_sample):
            length=min(len(remained_ys),2*args.n_select_sample-len(continue_ys))
            continue_ys=continue_ys+remained_ys[-length:]
            remained_ys=remained_ys[:-length]

        selected_ys, not_selected_ys, compare_info = get_comparison(task, x, continue_ys, backend=args.backend, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)
        remained_ys=remained_ys+not_selected_ys
        
        temp=[]
        for y in selected_ys:
            last_line = y.strip().split('\n')[-1]
            if 'Answer' in last_line:
                if '24' in last_line:
                    answers.append(y)
            else:
                temp.append(y)
        selected_ys=temp

        if to_print: 
            print(f'-- new_ys --: {new_ys}\n-- choices --: {continue_ys}\n')
        
        infos.append({'round': round, 'x': x, 'ys': ys, 'new_ys': new_ys, 'select_ys': selected_ys, 'compare_info':compare_info})
        ys = selected_ys
        if(len(ys)==0):
            ys=['']
        print("round:",round)
        if len(answers):
            break
    
    if(len(answers)):
        print("Get answer.")
        return answers, {'steps': infos}
    else:
        return [""],{'steps': infos}
    
def cot_solve(args, task, idx, to_print=True):
    print("Index:",idx+1)
    x=task.get_input(idx)
    y=""
    answers=[]
    cot_prompt = task.cot_prompt_wrap(x, y)
    for i in range (args.n_cot_sample):
        answer= gpt(cot_prompt, model = args.backend)
        answers.append(answer.split('Answer: ')[-1])
    final_ans=Counter(answers).most_common(1)[0][0]

    info={"question":x, "answers":answers,"final answer":final_ans}
    print(f'final answer:{final_ans}')
    return final_ans,info

def naive_solve(args, task, idx, to_print=True):
    x=task.get_input(idx)
    print("Index:",idx+1)
    print("Question: ",x)
    y=""
    naive_prompt = task.standard_prompt_wrap(x, y)
    answer= gpt(naive_prompt, model=args.backend)
    info={"question":x, "final answer":answer}
    return answer,info