
# ICML'24 : Generating Chain-of-Thoughts with a Pairwise-Comparison Approach to Searching for the Most Promising Intermediate Thought
-----------------------------

## Set environment

Python 3.8 and above is recommended.
After creating your python environment, you need to install the following packages.
```bash
pip install openai numpy sympy pandas
```

## Set api key

Put your OpenAI api key in `api_key.yaml`.

## Run

### AQuA

```bash
cd aqua
python main.py <method> <begin_task_idx> <end_task_idx>
# for example
python main.py ctot 0 10
```

### Game24

```bash
cd game24
python main.py <method> <begin_task_idx> <end_task_idx>
# for example
python main.py ctot 0 10
```

### Sudoku

```bash
cd sudoku
python main.py <method> <begin_task_idx> <end_task_idx> <puzzle_size>
# for example
python main.py ctot 0 10 3
```

### Others
There are other algorithms you can try by setting the 'method' parameter, including `direct`, `cot(CoT)`, `stot(SToT)`, `c_stot(Comp-SToT)`, `backtot(Back-SToT)`.

You can change the optional arguments: `backend`, `n_generate_sample`, `n_select_sample`, `n_evaluate_time`, `max_round`, `n_cot_sample`(for SC-CoT).

To find more information, you can:
```bash
python main.py --help
```

## Citation
If you find this work is relevant with your research or applications, please feel free to cite our work!
```
@inproceedings{CToT,
  title={Generating Chain-of-Thoughts with a Pairwise-Comparison Approach to Searching for the Most Promising Intermediate Thought},
  author={Zhang, Zhen-Yu and Han, Siwei and Yao, Huaxiu and Niu, Gang and Sugiyama, Masashi},
  booktitle={Proceedings of the 41st International Conference on Machine Learning (ICML 2020)},
  year={2024},
}
```
