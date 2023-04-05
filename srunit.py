import os
import argparse
from pathlib import Path
import shutil
from string import Template
from datetime import datetime


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def main():

    # check if there is custom.conf file under .srunit directory
    custom_config, custom_template = False, False
    custom_config_dir = Path(".srunit")
    if custom_config_dir.is_dir():
        for file in list(custom_config_dir.glob("**/*")):
            if file.suffix == ".conf":
                if custom_config:
                    raise ValueError(
                        bcolors.FAIL
                        + "There are more than one custom config files (.conf) in .srunit directory"
                        + bcolors.ENDC
                    )
                custom_config = True
                with open(file, "r") as f:
                    confs = f.read()
                print(bcolors.HEADER + f"Load config: {file}" + bcolors.ENDC)
            if file.suffix == ".sbatch":
                if custom_template:
                    raise ValueError(
                        bcolors.FAIL
                        + "There are more than one custom template files (.sbatch) in .srunit directory"
                        + bcolors.ENDC
                    )
                custom_template = True
                with open(file, "r") as f:
                    template = f.read()
                print(bcolors.HEADER + f"Load template: {file}" + bcolors.ENDC)

    configurations = {}
    for conf in confs.split("\n"):
        if len(conf) == 0:
            continue
        key, val = conf.split("=")
        # can we save it into dictionary?
        if val.isdigit():
            val = int(val)
        elif val == "":
            val = None
        configurations[key] = val

    # print(defaults)

    parser = argparse.ArgumentParser(
        description="srunit-cli", conflict_handler="resolve"
    )
    parser.add_argument("--dry_run", "-d", action="store_true")
    parser.add_argument("--script_path", "-f", default=None)

    for key, val in configurations.items():
        arg_key = "--" + key.lower().replace("-", "_")
        parser.add_argument(
            arg_key,
            default=val,
        )

    parser.add_argument("--gpu_num", "-n", default=configurations["GPU_NUM"])
    parser.add_argument("--gpu_type", "-t", default=configurations["GPU_TYPE"])

    args = parser.parse_args()

    # update configurations with arguments (overwrite default values)
    for arg in vars(args):
        if arg not in configurations:
            print(arg)
            configurations.update({arg.upper(): getattr(args, arg)})

    print(configurations)
    # Essential arguments (required for running the script)
    JOB_NAME = args.job_name
    OUTPUT_PATH = args.output_path
    GPU_TYPE = args.gpu_type
    GPU_NUM = args.gpu_num
    CPU_NUM = args.cpu_num
    SCRIPT_PATH = args.script_path
    ADDITIONAL_ARGS = ""
    EXP_ROOT = None
    DATETIME = datetime.now().strftime("%Y%m%d:%H%M%S")

    DRY_RUN = args.dry_run

    exp_root = Path(SCRIPT_PATH).parent
    EXP_ROOT = exp_root
    RUN_ROOT_PATH = exp_root / "runs"

    # get run number (run_0, run_1, ...)
    i = 0
    while os.path.exists(RUN_ROOT_PATH / f"run_{i}"):
        i += 1
    # get output_path by script_path

    # create run directory
    RUN_PATH = RUN_ROOT_PATH / f"run_{i}"
    if not DRY_RUN:
        Path.mkdir(RUN_PATH, exist_ok=True, parents=True)

    # create output directory (under run directory for each run `out`)
    OUTPUT_PATH = RUN_PATH / "out"
    if not DRY_RUN:
        Path.mkdir(OUTPUT_PATH, exist_ok=True, parents=True)

    # copy script to run directory

    RUN_SCRIPT_PATH = RUN_PATH / "finetune.sh"
    if not DRY_RUN:
        shutil.copy2(SCRIPT_PATH, RUN_SCRIPT_PATH)

    # set default job name if not specified (for sbatch)
    if JOB_NAME is None:
        JOB_NAME = EXP_ROOT.stem
        JOB_NAME = JOB_NAME + "_" + str(i)

    configurations.update(
        {
            "JOB_NAME": JOB_NAME,
            "OUTPUT_PATH": OUTPUT_PATH,
            "DATETIME": DATETIME,
            "RUN_PATH": RUN_PATH,
            "GPU_TYPE": GPU_TYPE,
            "CPU_NUM": CPU_NUM,
            "GPU_NUM": GPU_NUM,
            "RUN_SCRIPT_PATH": RUN_SCRIPT_PATH,
            "ADDITIONAL_ARGS": ADDITIONAL_ARGS,
            "EXP_ROOT": EXP_ROOT,
            "EXP_NAME": EXP_ROOT.stem,
        }
    )
    # print(configurations)
    values = {}
    for key, val in configurations.items():
        if val is None:
            val = getattr(args, key, "")
        values[key] = val

    src = Template(template=template)
    result = src.safe_substitute(values)
    # print(result)
    if DRY_RUN:
        print(bcolors.WARNING + "Dry run mode. Not submitting the job." + bcolors.ENDC)
        print(
            bcolors.WARNING
            + f"This script will create a slurm script under `{RUN_PATH}` directory."
            + bcolors.ENDC
        )
        print(result)
    else:
        print(bcolors.OKGREEN + "Submitting the job..." + bcolors.ENDC)
        print(bcolors.OKBLUE + f"Job name: {JOB_NAME}" + bcolors.ENDC)
        slurm_script_path = RUN_PATH / "cluster.slurm.sh"
        with open(slurm_script_path, "w") as f:
            f.write(result)
        os.system(f"sbatch {slurm_script_path}")


if __name__ == "__main__":

    main()
