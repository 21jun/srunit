import os
import argparse
from pathlib import Path
import shutil
from string import Template


with open("cache/default.conf", "r") as f:
    f.read()

parser = argparse.ArgumentParser(description="Argparse Tutorial")
parser.add_argument("--dry_run", "-d", action="store_true")
parser.add_argument("--job_name", "-j", default=None)
parser.add_argument("--output_path", "-o", default=None)
parser.add_argument("--gpu_type", "-t", default="A100-80GB")
parser.add_argument("--gpu_num", "-n", default="8")
parser.add_argument("--cpu_num", "-c", default="16")
parser.add_argument("--script_path", "-f", default="finetune.sh")
parser.add_argument("--add", "-a", default="")
args = parser.parse_args()


JOB_NAME = args.job_name
OUTPUT_PATH = args.output_path
GPU_TYPE = args.gpu_type
GPU_NUM = args.gpu_num
CPU_NUM = args.cpu_num
SCRIPT_PATH = args.script_path
CHECKPOINTS_PATH = "checkpoints"
ADDITIONAL_ARGS = args.add
dry_run = args.dry_run

# Additional


if __name__ == "__main__":

    # Check configuration files (this will overwrite default.conf)
    # find there is .conf file under current directory with .srunit directory and if exists
    # set value `custom_config` to True
    custom_config = False
    for file in os.listdir("."):
        if file.endswith(".conf") and ".srunit" in file:
            custom_config = True
            with open(file, "r") as f:
                f.read()
            break

    # if there is no custom config file, use default.conf
    if not custom_config:
        # read cache/default.conf and save its value to `values`
        with open("cache/default.conf", "r") as f:
            values = f.read()

    exp_root = Path(SCRIPT_PATH).parent
    RUN_ROOT_PATH = exp_root / "runs"

    i = 0
    while os.path.exists(RUN_ROOT_PATH / f"run_{i}"):
        i += 1
    # get output_path by script_path

    RUN_PATH = RUN_ROOT_PATH / f"run_{i}"
    if not dry_run:
        Path.mkdir(RUN_PATH, exist_ok=True, parents=True)

    OUTPUT_PATH = RUN_PATH / "out"
    if not dry_run:
        Path.mkdir(OUTPUT_PATH, exist_ok=True, parents=True)

    RUN_SCRIPT_PATH = RUN_PATH / "finetune.sh"
    if not dry_run:
        shutil.copy2(SCRIPT_PATH, RUN_SCRIPT_PATH)

    if JOB_NAME is None:
        JOB_NAME = exp_root.stem
        JOB_NAME = JOB_NAME + "_" + str(i)

    CHECKPOINTS_PATH = RUN_PATH / "checkpoints"

    print()

    values = {
        "JOB_NAME": JOB_NAME,
        "OUTPUT_PATH": OUTPUT_PATH,
        "GPU_TYPE": GPU_TYPE,
        "GPU_NUM": GPU_NUM,
        "CPU_NUM": CPU_NUM,
        "SCRIPT_PATH": SCRIPT_PATH,
        "CHECKPOINTS_PATH": CHECKPOINTS_PATH,
        "RUN_SCRIPT_PATH": RUN_SCRIPT_PATH,
        "ADDITIONAL_ARGS": ADDITIONAL_ARGS,
    }

    with open("template.sbatch", "r") as f:
        src = Template(f.read())
        result = src.safe_substitute(values)
        print(result)
