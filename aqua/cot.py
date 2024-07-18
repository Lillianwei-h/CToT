from models import *
from collections import Counter

def get_cot_outcome(z,args):
    prompt = "Here is a question. You should work on it step by step. And you should print '###' before giving the final answer. Your answer must be only the alphabet of your choice. For example: ###A"
    outcome = gpt(prompt, z, model=args.backend)
    return outcome

def get_naive_outcome(z,args):
    prompt = "You should solve the following question. And you should print '###' before giving the final answer. Your answer must be only the alphabet of your choice. For example: ###A"
    outcome = gpt(prompt, z, model=args.backend)
    return outcome

def cot_solve(question ,args, to_print):
    x = question
    x = "Q: " + x + "\n"
    print(x) 
    outcomes=[]
    answers=[]
    for _ in range (args.n_cot_sample):
        outcome = get_cot_outcome(x,args)
        outcomes.append(outcome)
        last_line = outcome.strip().split('\n')[-1]
        answer=last_line.split('###')[-1]
        answers.append(answer)
    final_ans=Counter(answers).most_common(1)[0][0]

    info={"answers":outcomes}
    print(f'final answer:{final_ans}')
    return final_ans,info

def naive_solve(question ,args, to_print):
    x = question
    x = "Q: " + x + "\n"
    print(x) 
    outcome = get_naive_outcome(x,args)
    last_line = outcome.strip().split('\n')[-1]
    answer=last_line.split('###')[-1]
    info={}
    print(f'final answer:{answer}')
    return answer,info