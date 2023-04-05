# srunit

Automate your SLURM cluster...

# Installation


1. Clone Project

```
git clone https://github.com/21jun/srunit.git
```

2. Install with `pip install -e .`

# How to use it?

0. configure `.srunit/xxx.conf`, .`srunit/xxx.sbatch` for purpose 
    
    All variable written in `xxx.sbatch` script must be specified in `xxx.conf` 
    
    except following variables (these variables are automatically generated)
    ```
    JOB_NAME,
    OUTPUT_PATH,
    DATETIME,
    RUN_PATH,
    RUN_SCRIPT_PATH,
    ADDITIONAL_ARGS,
    EXP_ROOT,
    EXP_ROOT.stem,
    ```
1. place your shell script under experiments directory
<img width="308" alt="image" src="https://user-images.githubusercontent.com/29483429/230043610-dee61aa2-b473-4ce8-a1bc-ef28d801d1d5.png">

2. run `srunit` with -f flag to specify your shell script

`srunit -t A100-80GB -n 4 -f exp/v1/el/finetune_template.sh`

tip. you can use -d flag to make dry run (create sbatch scirpt only)

`srunit -t A100 -n 4 -f exp/v1/el/finetune_template.sh -d`

output log:
```sh
Load template: .srunit/cluster.sbatch
Load config: .srunit/1.conf
{'JOB_NAME': 'sl_0', 'OUTPUT_PATH': PosixPath('tasks/train/asr/finetune/commonvoice12/exp/phoneme-CTC-cv-mono-phoneme-level-ascii/recipes/sl/runs/run_0/out'), 'GPU_TYPE': '3090', 'GPU_NUM': 8, 'CPU_NUM': 16, 'DRY_RUN': False, 'SCRIPT_PATH': 'tasks/train/asr/finetune/commonvoice12/exp/phoneme-CTC-cv-mono-phoneme-level-ascii/recipes/sl/finetune_asr.sh', 'DATETIME': '20230405:183810', 'RUN_PATH': PosixPath('tasks/train/asr/finetune/commonvoice12/exp/phoneme-CTC-cv-mono-phoneme-level-ascii/recipes/sl/runs/run_0'), 'RUN_SCRIPT_PATH': PosixPath('tasks/train/asr/finetune/commonvoice12/exp/phoneme-CTC-cv-mono-phoneme-level-ascii/recipes/sl/runs/run_0/finetune.sh'), 'ADDITIONAL_ARGS': '', 'EXP_ROOT': PosixPath('tasks/train/asr/finetune/commonvoice12/exp/phoneme-CTC-cv-mono-phoneme-level-ascii/recipes/sl'), 'EXP_NAME': 'sl'}
Submitting the job...
Job name: sl_0
Submitted batch job 20926
```

3. check your `sbatch` script and output files under `runs` dir

<img width="346" alt="image" src="https://user-images.githubusercontent.com/29483429/230043920-87308159-7420-4d15-88b6-548f631fa46b.png">

`run_x` : x is incremental number


