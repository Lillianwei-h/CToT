import json
import os
import argparse
from bfs import *
from game24 import Game24Task
from models import gpt_usage
from outcomes import print_outcomes

task = Game24Task()
parser = argparse.ArgumentParser(description='CToT for game24 dataset')

parser.add_argument('func', type=str, help='Function to execute')
parser.add_argument('begin_task', type=int, help='Begin task number')
parser.add_argument('end_task', type=int, help='End task number')
parser.add_argument('--backend', type=str, default='gpt-3.5-turbo-1106', help='OpenAI model')
parser.add_argument('--n_select_sample', type=int, default=3, help='Number of samples to select')
parser.add_argument('--n_evaluate_time', type=int, default=1, help='Number of evaluation times')
parser.add_argument('--n_cot_sample', type=int, default=15, help='Number of CoT samples')
parser.add_argument('--max_round', type=int, default=6, help='Maximum depth of tree')
args = parser.parse_args()
print(args)
logs = []
file = f"logs/{args.func}/start{args.begin_task}_end{args.end_task}_cotsample{args.n_cot_sample}_select{args.n_select_sample}_evaluate{args.n_evaluate_time}.json"
os.makedirs(os.path.dirname(file), exist_ok=True)

for i in range(args.begin_task, args.end_task):
    if args.func == 'direct':
        answer, info = naive_solve(args, task, idx=i, to_print=False)
    elif args.func == 'cot':
        answer, info = cot_solve(args, task, idx=i, to_print=False)
    elif args.func == 'stot':
        answer, info = solve(args, task, idx=i, to_print=False)
    elif args.func == 'ctot':
        answer, info = duel_solve(args, task, idx=i, to_print=False)
    elif args.func == 'back_tot':
        answer, info = back_solve(args, task, idx=i, to_print=False)
    elif args.func == 'c_stot':
        answer, info = compare_solve(args, task, idx=i, to_print=False)
    print("Answers:", answer)
    info.update({"idx": i+1, "ys": answer, "usage_so_far": gpt_usage()})
    logs.append(info)
    with open(file, "w") as f1:
        json.dump(logs, f1, indent=4)
    print_outcomes(file)
