import threading
import argparse
import os
from tot import *
from cot import *

def main():
    parser = argparse.ArgumentParser(description='CToT for aqua dataset')

    parser.add_argument('func', type=str, help='Function to execute')
    parser.add_argument('begin_task', type=int, help='Begin task number')
    parser.add_argument('end_task', type=int, help='End task number')
    parser.add_argument('--thread_n', type=int, default=1, help='Number of threads')
    parser.add_argument('--backend', type=str, default='gpt-3.5-turbo-1106', help='OpenAI model')
    parser.add_argument('--n_generate_sample', type=int, default=3, help='Number of samples to generate')
    parser.add_argument('--n_select_sample', type=int, default=1, help='Number of samples to select')
    parser.add_argument('--n_evaluate_time', type=int, default=1, help='Number of evaluation times')
    parser.add_argument('--n_cot_sample', type=int, default=15, help='Number of CoT samples')
    parser.add_argument('--max_round', type=int, default=3, help='Maximum depth of tree')
    parser.add_argument('--shuffle', action='store_true', help='Whether to shuffle during comparison')
    parser.add_argument('--dataset_path', type=str, default='./data/test.jsonl', help='Path to the dataset')
    args = parser.parse_args()

    run(args,1)

def run(args,id):

    print('*****************************')
    print(args)
    print('*****************************')

    log_file = f"logs/{args.func}/{args.begin_task}-{args.end_task}_cot_{args.n_cot_sample}_tot_generate{args.n_generate_sample}_select{args.n_select_sample}_evaluate{args.n_evaluate_time}_shuffle{args.shuffle}({id}).json"
    result_file = f"results/{args.func}.jsonl"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    os.makedirs(os.path.dirname(result_file), exist_ok=True)

    with open(args.dataset_path, "r", encoding="utf-8") as input_file:
        lines = input_file.readlines()
    total_num = args.end_task - args.begin_task
    chunks = [
        lines[args.begin_task+i : args.begin_task+i + total_num // args.thread_n]
        for i in range(0, total_num, total_num // args.thread_n)
    ]
    dics = [{} for _ in range(args.thread_n)]

    threads = []
    for i in range(args.thread_n):
        thread = threading.Thread(target=process_data, args=(args, chunks[i], dics, i))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    result_dict = {}
    result_dict['id']=id
    result_dict["begin"]=args.begin_task
    result_dict["end"]=args.end_task
    result_dict["generate"]=args.n_generate_sample
    result_dict["select"]=args.n_select_sample
    result_dict["evaluate"]=args.n_evaluate_time
    result_dict["n_cot"]=args.n_cot_sample
    result_dict['correct_list']=[]
    result_dict['correct_num']=0
    result_dict.update(gpt_usage())
    infos=[]
    for d in dics:
        infos.extend(d['infos'])
        result_dict['correct_list'].extend(d['correct_list'])
    result_dict['correct_num']=len(result_dict['correct_list'])
    result_dict['accuracy'] = result_dict['correct_num'] * 1.0 / total_num
    print("Accuracy:",result_dict['accuracy'])
    
    with open(log_file, 'w') as f:
        json.dump(infos, f, indent=4)
    with open(result_file, 'a') as f:
        f.write(json.dumps(result_dict) + "\n")

def process_data(args, lines, dics, index):
    i=0
    thread_n=len(lines)
    infos=[]
    correct_list=[]
    for line in lines:
        data = json.loads(line)
        choice = "(" + "(".join(data["options"])
        choice = choice.replace("(", " (").replace(")", ") ")
        choice = "Answer Choices:" + choice
        question = data["question"].strip() + " " + choice + "\nSteps:\n"
        standard_answer = data["correct"]

        print('*************************')
        print(f"No. {i+thread_n*index} data")
        if args.func == 'direct':
            answer, info = naive_solve(question, args, to_print=False)
        elif args.func == 'cot':
            answer, info = cot_solve(question, args, to_print=False)
        elif args.func == 'stot':
            answer, info = solve(question, args, to_print=False)
        elif args.func == 'c_stot':
            answer, info = compare_solve(question, args, to_print=False)
        elif args.func == 'backtot':
            answer, info = back_solve(question, args, to_print=False)
        elif args.func == 'ctot':
            answer, info = duel_solve(question, args, to_print=False)

        print("Correct answer:",standard_answer)
        info.update({'idx': i+thread_n*index, 'answer': answer, 'correct answer': standard_answer,'usage_so_far': gpt_usage(args.backend)})
        infos.append(info)
        if standard_answer in answer:
            correct_list.append(i+thread_n*index)
        i+=1

    dics[index]={'infos':infos, 'correct_list':correct_list}

if __name__ == "__main__":
    main()
