from models import *
import itertools
import json
import random
from collections import Counter
import re

def read_data(args):
    questions = []
    answers = []
    decoder = json.JSONDecoder()
    if args.dataset == "aqua":
      with open(args.dataset_path) as f:
        lines = f.readlines()
        for line in lines:
          json_res = decoder.raw_decode(line)[0]
          choice = "(" + "(".join(json_res["options"])
          choice = choice.replace("(", " (").replace(")", ") ")
          choice = "Answer Choices:" + choice
          questions.append(json_res["question"].strip() + " " + choice)
          answers.append(json_res["correct"])
    return questions, answers

def get_proposals(z, args):
    system_prompt = '''You are a heuristic assistant. 
        Help me solve the given question by giving me only the next step. 
        However, when the final step leads you to the final answer, give me the alphabet of your choice and print "###" before it. 
        For example: ###A, which should be at the last line.'''
    proposals=[]
    for _ in range(args.n_generate_sample):
        proposal = gpt(z, system_prompt = system_prompt, model=args.backend)
        proposals.append(proposal)
    return [z + _ + '\n' for _ in proposals]

def get_value(z, backend, evaluate_times):
    system_prompt = "You should give a score between 0 to 2 to evaluate if the given thought steps to the question is correct. 0 means incorrect. 1 means maybe correct. 2 means definitely correct. You must only reply with 0 or 1 or 2.\n"+z
    values=[]
    for _ in range (evaluate_times):
        value_outputs = gpt(z, system_prompt = system_prompt, model=backend)
        value = value_outputs[0]
        numbers = re.findall(r'\d+', value)
        if(len(numbers)>0):
            values.append(int(numbers[0]))
        else:
            values.append(1)
    value = sum(values)/len(values)
    return value

def get_values(zs, backend, evaluate_times):
    values = []
    for z in zs:
        value = get_value(z, backend, evaluate_times)
        values.append(value)
    return values

def compare(pair, backend, evaluate_times):
    compare_prompt=[]
    compare_prompt.append("You are a logical student. You should judge which of the two reasoning steps is better. You must only reply 1 or 2. If both inputs are equal, randomly print 1 or 2. Don't explain or reply anything else.\n")
    compare_prompt.append("Find out which of the two analysis is better. You must only reply 1 or 2.If both inputs are equal, randomly print 1 or 2. Don't explain or reply anything else.\n")
    compare_prompt.append("Compare the two analysis and find which is better. You must only reply 1 or 2. If both inputs are equal, randomly print 1 or 2. Don't explain or reply anything else.\n")

    value_outputs = []
    for i in range (evaluate_times):
        value_output=gpt(f"1: {pair[0]}\n2: {pair[1]}", system_prompt = compare_prompt[i], model=backend)
        value_outputs.append(value_output[0])
    print(value_outputs)
    values = []
    for value_output in value_outputs:
        numbers = re.findall(r'\d+', value_output)
        if(len(numbers)):
            values.append(numbers[0])
        else:
            values.append(random.randint(1, 2))
    counter = Counter(values)
    result = counter.most_common(1)[0][0]
    return int(result) - 1

def get_comparison(zs, backend, shuffle, select_num=3, evaluate_times = 1):
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
            result = compare(pair, backend, evaluate_times)
            new_zs.append(pair[result])
            not_selected_zs.append(pair[1-result])
            compare_info.append(f"Compare {pair[0]} and {pair[1]}, choose {result+1}.\n")
        current_zs = new_zs
    return current_zs, not_selected_zs, compare_info

def solve(question ,args, to_print):
    x = question
    x = "Q: " + x + "\n" + "Steps: \n" 
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    round = 0
    while round < max_round:
        round += 1
        new_zs = [get_proposals(z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        current_answers=[]
        continue_zs=[]
        values = get_values(new_zs, backend=args.backend, evaluate_times = args.n_evaluate_time)
        sorted_new_zs, sorted_values = zip(*sorted(zip(new_zs, values), key=lambda x: x[1], reverse=True))
        selected_zs = sorted_new_zs[:args.n_select_sample]
        
        for z in selected_zs:
            last_line = z.strip().split('\n')[-1]
            if ("###" in last_line):
                current_answers.append(z)
            else:
                continue_zs.append(z)
        answers=answers+current_answers
        
        if to_print: 
            print(f'-- new_zs --: {sorted_new_zs}\n-- sol values --: {sorted_values}\n-- choices --: {selected_zs}\n--answers--: {answers}')
        print("answers:",answers)

        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs': new_zs, 'values': values, 'selected_zs': selected_zs, 'continue_zs':continue_zs, 'answers': answers})
        zs = continue_zs
        if(len(zs)==0):
            break

    answer_list=[]
    pattern = r'###\W*(\w)'
    for whole_answer in answers:
        match = re.search(pattern, whole_answer)
        if match:
            answer = match.group(1)
            answer_list.append(answer)
    
    if(len(answer_list)==0):
        return "",{'steps': infos}
    
    final_ans=Counter(answer_list).most_common(1)[0][0]
    print('Final answer: ',final_ans)
    return final_ans, {'steps': infos}

def compare_solve(question ,args, to_print):
    x = question
    x = "Q: " + x + "\n" + "Steps: \n" 
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    round = 0
    while round < max_round:
        round += 1
        new_zs = [get_proposals(z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        current_answers=[]
        continue_zs=[]
        
        selected_zs, not_selected_zs, compare_info = get_comparison(new_zs, backend=args.backend, shuffle = args.shuffle, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)
        for z in selected_zs:
            last_line = z.strip().split('\n')[-1]
            if ("###" in last_line):
                current_answers.append(z)
            else:
                continue_zs.append(z)
        answers=answers+current_answers
        
        if to_print: 
            print(f'-- new_zs --: {new_zs}\n-- choices --: {selected_zs}\n--answers--: {answers}')
        print("answers:",answers)

        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs': new_zs, 'selected_zs': selected_zs, 'continue_zs':continue_zs, 'compare_info':compare_info, 'answers': answers})
        zs = continue_zs
        if(len(zs)==0):
            break

    answer_list=[]
    pattern = r'###\W*(\w)'
    for whole_answer in answers:
        match = re.search(pattern, whole_answer)
        if match:
            answer = match.group(1)
            answer_list.append(answer)
    
    if(len(answer_list)==0):
        return "",{'steps': infos}
    
    final_ans=Counter(answer_list).most_common(1)[0][0]
    print('Final answer: ',final_ans)
    return final_ans, {'steps': infos}

def back_solve(question ,args, to_print):
    x = question
    x = "Q: " + x + "\n" + "Steps: \n" 
    print(x) 
    max_round=args.max_round
    zs = [x]
    remained_zs = []
    remained_values=[]
    infos = []
    answers=[]
    round = 0
    while round < max_round:
        current_answers=[]
        round += 1
        new_zs = [get_proposals(z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        
        values = get_values(new_zs, backend=args.backend, evaluate_times = args.n_evaluate_time)
        sorted_zs, sorted_values = zip(*sorted(zip(new_zs+remained_zs, values+remained_values), key=lambda x: x[1], reverse=True))
        
        remained_zs=[]
        remained_values=[]
        selected_zs = []
        selected_values=[]
        ans_num=0
        zs_num=0
        for z,value in zip(sorted_zs,sorted_values):
            last_line = z.strip().split('\n')[-1]
            if ("###" in last_line and ans_num<args.n_select_sample):
                current_answers.append(z)
                ans_num+=1
            elif("###" not in last_line and zs_num<args.n_select_sample):
                selected_zs.append(z)
                selected_values.append(value)
                zs_num+=1
            else:
                remained_zs.append(z)
                remained_values.append(value)

        answers=answers+current_answers

        if to_print: 
            print(f'-- new_zs --: {new_zs}\n -- choices --: {selected_zs}\n--answers--: {answers}')
        print("round:",round)
        
        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs':new_zs, 'values':values, 'sorted_zs':sorted_zs, 'sorted_values': sorted_values,'selected_zs': selected_zs, 'selected_values':selected_values, 'answers': answers})
        zs = selected_zs
        if(len(zs)==0 and len(remained_zs)==0):
            break
        

    answer_list=[]
    pattern = r'###\W*(\w)'
    for whole_answer in answers:
        match = re.search(pattern, whole_answer)
        if match:
            answer = match.group(1)
            answer_list.append(answer)
    if len(answer_list):
        final_ans=Counter(answer_list).most_common(1)[0][0]
    else:
        return "", {'steps': infos}

    print('Final answer: ',final_ans)
    return final_ans, {'steps': infos}

def duel_solve(question ,args, to_print):
    x = question
    x = "Q: " + x + "\n" + "Steps: \n" 
    print(x) 
    max_round=args.max_round
    zs = [x]
    infos = []
    answers=[]
    to_check_answer=[]
    round = 0
    while round < max_round:
        current_answers=[]
        remained_zs=[]
        round += 1
        new_zs = [get_proposals(z,args) for z in zs]
        new_zs = list(itertools.chain(*new_zs))
        
        selected_zs, not_selected_zs, compare_info = get_comparison(new_zs, backend=args.backend, shuffle = args.shuffle, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)
        selected_ans, not_selected_ans, compare_info_ans = get_comparison(to_check_answer, backend=args.backend, shuffle = args.shuffle, select_num=args.n_select_sample, evaluate_times = args.n_evaluate_time)
        to_check_answer=[]
        continue_zs = []
        for z in selected_zs:
            last_line = z.strip().split('\n')[-1]
            if ("###" in last_line):
                current_answers.append(z)
            else:
                continue_zs.append(z)
        for z in not_selected_zs:
            last_line = z.strip().split('\n')[-1]
            if ("###" in last_line):
                to_check_answer.append(z)
            else:
                remained_zs.append(z)
        answers=answers+current_answers+selected_ans
        to_check_answer = to_check_answer+not_selected_ans
        
        if(len(continue_zs)<args.n_select_sample):
            length=min(len(remained_zs),args.n_select_sample-len(continue_zs))
            continue_zs=continue_zs+remained_zs[-length:]
            remained_zs=remained_zs[:-length]
        
        if to_print: 
            print(f'-- new_zs --: {new_zs}\n-- continue_zs --: {continue_zs}\n-- choices --: {selected_zs}\n--answers--: {answers}')
        print("round:",round)
        
        infos.append({'round': round, 'x': x, 'zs': zs, 'new_zs':new_zs, 'continue_zs': continue_zs, 'compare_info':compare_info+compare_info_ans, 'select_zs': selected_zs, 'to_check_answers':to_check_answer,'answers': answers})
        zs = continue_zs
        if(len(zs)==0 and len(to_check_answer)==0):
            break
        

    answer_list=[]
    pattern = r'###\W*(\w)'
    for whole_answer in answers:
        match = re.search(pattern, whole_answer)
        if match:
            answer = match.group(1)
            answer_list.append(answer)
    
    if len(answer_list):
        final_ans=Counter(answer_list).most_common(1)[0][0]
    else:
        return "", {'steps': infos}

    print('Final answer: ',final_ans)
    return final_ans, {'steps': infos}