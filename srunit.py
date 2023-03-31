import os
import argparse
from pathlib import Path
import shutil


parser = argparse.ArgumentParser(description="Argparse Tutorial")
parser.add_argument("--dry_run", "-d", action="store_true")
parser.add_argument("--job_name", "-j", default="default")
parser.add_argument("--output_path", "-o", default=None)
parser.add_argument("--gpu_type", "-t", default="A100-80GB")
parser.add_argument("--gpu_num", "-n", default="8")
parser.add_argument("--cpu_num", "-c", default="16")
parser.add_argument("--script_path", "-f", default="finetune.sh")
args = parser.parse_args()


JOB_NAME = args.job_name
OUTPUT_PATH = args.output_path
GPU_TYPE = args.gpu_type
GPU_NUM = args.gpu_num
CPU_NUM = args.cpu_num
SCRIPT_PATH = args.script_path
CHECKPOINTS_PATH = "checkpoints"

dry_run_sbatch = args.dry_run


def update_template():

    TEMPLATE = f"""#!/bin/bash

#SBATCH -J {JOB_NAME} # job name
#SBATCH -o {OUTPUT_PATH}/output_%x.%j.out 
#SBATCH -p {GPU_TYPE} # queue name or partiton name
#SBATCH -t 72:00:00 # Run time (hh:mm:ss)
#SBATCH  --gres=gpu:{GPU_NUM}
#SBATCH  --nodes=1
#SBATCH  --ntasks=1
#SBATCH  --tasks-per-node=1
#SBATCH  --cpus-per-task={CPU_NUM}

srun -l /bin/hostname
srun -l /bin/pwd
srun -l /bin/date

module purge
pip freeze

echo $CONDA_DEFAULT_ENV

date
echo $CUDA_VISIBLE_DEVICES
BASEDIR=$(dirname "$0")
echo "SCRIPT"
cat {RUN_SCRIPT_PATH}
echo "START"
sh {RUN_SCRIPT_PATH} {GPU_NUM} {CHECKPOINTS_PATH}
date
    """

    return TEMPLATE


if __name__ == "__main__":

    exp_root = Path(SCRIPT_PATH).parent
    RUN_ROOT_PATH = exp_root / "runs"

    i = 0
    while os.path.exists(RUN_ROOT_PATH / f"run_{i}"):
        i += 1
    # get output_path by script_path

    RUN_PATH = RUN_ROOT_PATH / f"run_{i}"
    Path.mkdir(RUN_PATH, exist_ok=True, parents=True)

    OUTPUT_PATH = RUN_PATH / "out"
    Path.mkdir(OUTPUT_PATH, exist_ok=True, parents=True)

    RUN_SCRIPT_PATH = RUN_PATH / "finetune.sh"
    shutil.copy2(SCRIPT_PATH, RUN_SCRIPT_PATH)

    if JOB_NAME is None:
        JOB_NAME = exp_root.stem
        JOB_NAME = JOB_NAME + "_" + str(i)

    CHECKPOINTS_PATH = RUN_PATH / "checkpoints"

    TEMPLATE = update_template()
    print(TEMPLATE)

    slurm_script_path = RUN_PATH / "cluster.slurm.sh"
    with open(slurm_script_path, "w") as f:
        f.write(TEMPLATE)

    if not dry_run_sbatch:
        os.system(f"sbatch {slurm_script_path}")
