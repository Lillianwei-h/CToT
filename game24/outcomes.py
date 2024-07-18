import json
import os

def print_outcomes(task_name):
    path=task_name
    out_path=f'outcomes/{task_name}.txt'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(path, 'r') as file:
        data = json.load(file)

    with open(out_path, 'w') as file:
        for task in data:
            if any("Answer" in s for s in task["ys"]):
                file.write("------------------------------------------------------------\n")
                file.write("idx: " + str(task["idx"]) + "\n")
                file.write("x: " + task["steps"][0]["x"] + "\n")
                file.write("Answers:\n")
                file.write("------------------------------\n")
                for i in task["ys"]:
                    if ("Answer" in i):
                        file.write(i + "\n")
                file.write("------------------------------\n")
                file.write("cost: " + str(task["usage_so_far"]["cost"]) + "\n")
                file.write("------------------------------------------------------------\n")
        file.write("Total costs:" + str(data[len(data)-1]["usage_so_far"]["cost"]))

