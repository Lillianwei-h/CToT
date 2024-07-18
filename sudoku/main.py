import argparse
import os
import json
from tot import *
from cot import *


def main():
    parser = argparse.ArgumentParser(description='CToT for sudoku dataset')

    parser.add_argument('func', type=str, help='Function to execute')
    parser.add_argument('begin_task', type=int, help='Begin task number')
    parser.add_argument('end_task', type=int, help='End task number')
    parser.add_argument('puzzle_size', type=int, help='The size of the sudoku puzzle')
    parser.add_argument('--backend', type=str, default='gpt-3.5-turbo-1106', help='OpenAI model')
    parser.add_argument('--n_generate_sample', type=int, default=5, help='Number of samples to generate')
    parser.add_argument('--n_select_sample', type=int, default=6, help='Number of samples to select')
    parser.add_argument('--n_evaluate_time', type=int, default=3, help='Number of evaluation times')
    parser.add_argument('--n_cot_sample', type=int, default=15, help='Number of CoT samples')
    parser.add_argument('--max_round', type=int, default=15, help='Maximum depth of tree')
    parser.add_argument('--shuffle', action='store_true', help='Whether to shuffle during comparison')
    args = parser.parse_args()
    run(args,1)

def run(args,i):
    print('*****************************')
    print(args)
    print('*****************************')
    args.dataset=args.puzzle_size

    problem_file = f'data/{args.puzzle_size}x{args.puzzle_size}_sudoku_puzzles.json'
    f = open(problem_file)
    with open(problem_file, 'r') as f:
        questions = json.load(f)
    
    file = f'logs/{args.func}/{args.dataset}x{args.dataset}_cot_{args.n_cot_sample}_tot_generate{args.n_generate_sample}_select{args.n_select_sample}_evaluate{args.n_evaluate_time}_shuffle{args.shuffle}({i}).json'

    os.makedirs(os.path.dirname(file), exist_ok=True)
    
    logs=[]
    total = 0
    correct_list = []   
    for i in range(args.begin_task,args.end_task,1):
        question=questions[i]
        print('*************************')
        print(f"{i+1}st data")
        if args.func == 'direct':
            answer, info = naive_solve(question, args, to_print=False)
        if args.func == 'cot':
            answer, info = cot_solve(question, args, to_print=False)
        elif args.func == 'stot':
            answer, info = solve(question, args, to_print=False)
        elif args.func == 'c_stot':
            answer, info = compare_solve(question, args, to_print=False)
        elif args.func == 'back_tot':
            answer, info = back_solve(question, args, to_print=False)
        elif args.func == 'ctot':
            answer, info = duel_solve(question, args, to_print=False)

        info.update({'idx': i+1, 'answer': answer,'usage_so_far': gpt_usage()})
        logs.append(info)
        with open(file, 'w') as f:
            json.dump(logs, f, indent=4)

        if(answer==""):
            pass
        elif check(answer,args):
            correct_list.append(i+1)
        total += 1 
        
    accuracy = (len(correct_list) * 1.0 / total) * 100
    print(f"accuracy : {accuracy}%")
    logs.append({'test amount':args.end_task-args.begin_task,'correct list':correct_list, 'accuracy':f'{accuracy}%'})
    with open(file, 'w') as f:
            json.dump(logs, f, indent=4)

if __name__ == "__main__":
    main()