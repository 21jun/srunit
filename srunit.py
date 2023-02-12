import os
import argparse
from pathlib import Path


parser = argparse.ArgumentParser(description="Argparse Tutorial")
parser.add_argument("--dry_run", "-d", action="store_true")
parser.add_argument("--job_name", default="default")
parser.add_argument("--output_path", "-o", default=None)
parser.add_argument("--gpu_type", "-t", default="A100")
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
cat {SCRIPT_PATH}
echo "START"
sh {SCRIPT_PATH} {GPU_NUM}
date
    """

    return TEMPLATE


if __name__ == "__main__":

    # get output_path by script_path
    exp_root = Path(SCRIPT_PATH).parent
    OUTPUT_PATH = exp_root / "out"
    Path.mkdir(OUTPUT_PATH, exist_ok=True, parents=True)

    i = 1
    while os.path.exists(exp_root / f"cluster.slurm.{i}.sh"):
        i += 1

    JOB_NAME = exp_root.stem
    JOB_NAME = JOB_NAME + "_" + str(i)

    TEMPLATE = update_template()
    print(TEMPLATE)

    slurm_script_path = exp_root / f"cluster.slurm.{i}.sh"
    with open(slurm_script_path, "w") as f:
        f.write(TEMPLATE)

    if not dry_run_sbatch:
        os.system(f"sbatch {slurm_script_path}")
