import os
import argparse
from pathlib import Path
import shutil
from string import Template


def main():

    # check if there is custom.conf file under .srunit directory
    custom_config, custom_template = False, False
    custom_config_dir = Path(".srunit")
    if custom_config_dir.is_dir():
        for file in list(custom_config_dir.glob("**/*")):
            if file.suffix == ".conf":
                if custom_config:
                    raise ValueError(
                        "There are more than one custom config files in .srunit directory"
                    )
                custom_config = True
                with open(file, "r") as f:
                    confs = f.read()
            if file.suffix == ".sbatch":
                if custom_template:
                    raise ValueError(
                        "There are more than one custom template files in .srunit directory"
                    )
                custom_template = True
                with open(file, "r") as f:
                    template = f.read()

    # print(custom_config)
    if custom_config:
        print("Custom config file found")
    else:
        print("No custom config file found, using default.conf")

    if custom_template:
        print("Custom template file found")
    else:
        print("No custom template file found, using template.sbatch")

    # if there is no custom config file, use default.conf
    if not custom_config:
        # read cache/default.conf and save its value to `values`
        with open("cache/default.conf", "r") as f:
            confs = f.read()

    if not custom_template:
        with open("template.sbatch", "r") as f:
            template = f.read()

    for conf in confs.split("\n"):
        print(conf)

    defaults = {}
    for conf in confs.split("\n"):
        if len(conf) == 0:
            continue
        key, val = conf.split("=")
        # can we save it into dictionary?
        if val.isdigit():
            val = int(val)
        elif val == "":
            val = None
        defaults[key] = val

    # print(defaults)

    parser = argparse.ArgumentParser(description="SRUNIT v2.0.0")
    parser.add_argument("--dry_run", "-d", action="store_true")
    parser.add_argument("--script_path", "-f", default=None)

    for key, val in defaults.items():
        arg_key = "--" + key.lower().replace("-", "_")
        print(arg_key)
        parser.add_argument(
            arg_key,
            default=val,
        )

    args = parser.parse_args()

    print(args)

    # Essential arguments (required for running the script)
    JOB_NAME = args.job_name
    OUTPUT_PATH = args.output_path
    GPU_TYPE = args.gpu_type
    GPU_NUM = args.gpu_num
    CPU_NUM = args.cpu_num
    SCRIPT_PATH = args.script_path
    CHECKPOINTS_PATH = "checkpoints"
    ADDITIONAL_ARGS = ""

    DRY_RUN = args.dry_run

    exp_root = Path(SCRIPT_PATH).parent
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
        JOB_NAME = exp_root.stem
        JOB_NAME = JOB_NAME + "_" + str(i)

    CHECKPOINTS_PATH = RUN_PATH / "checkpoints"

    values = {}

    # values = {
    #     "JOB_NAME": JOB_NAME,
    #     "OUTPUT_PATH": OUTPUT_PATH,
    #     "GPU_TYPE": GPU_TYPE,
    #     "GPU_NUM": GPU_NUM,
    #     "CPU_NUM": CPU_NUM,
    #     "SCRIPT_PATH": SCRIPT_PATH,
    #     "CHECKPOINTS_PATH": CHECKPOINTS_PATH,
    #     "RUN_SCRIPT_PATH": RUN_SCRIPT_PATH,
    #     "ADDITIONAL_ARGS": ADDITIONAL_ARGS,
    # }

    with open("template.sbatch", "r") as f:
        src = Template(f.read())
        result = src.safe_substitute(values)
        print(result)


if __name__ == "__main__":

    main()
