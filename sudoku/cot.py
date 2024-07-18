from models import *
from collections import Counter

def get_cot_outcome(z,args):
    input = f"This is a {args.puzzle_size}x{args.puzzle_size} two-dimensional array represents a matrix, \
        where some numbers are already given, and '*' represents the numbers that need to be filled in. \
        You should replace all the '*' by a number between 1 to {args.puzzle_size} and make sure each number appears once and only once in each row or column. \
        Don't change the given number.\
        You should work on it step by step. And you should print '###' before giving the final answer.\
        For example: ###[[1, 2, 3], [3, 1, 2], [2, 3, 1]]\n\
        Question: " + z
    outcome = gpt(input, model=args.backend)
    return outcome

def get_naive_outcome(z,args):
    input = f"This is a {args.puzzle_size}x{args.puzzle_size} two-dimensional array represents a matrix, \
        where some numbers are already given, and '*' represents the numbers that need to be filled in. \
        You should replace all the '*' by a number between 1 to {args.puzzle_size} and make sure each number appears once and only once in each row or column. \
        Don't change the given number.\
        You should print '###' before giving the final answer.\
        For example: ###[[1, 2, 3], [3, 1, 2], [2, 3, 1]]\n\
        Question: " + z
    outcome = gpt(input, model=args.backend)
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

    info={"answers":outcomes,"final answer":final_ans}
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