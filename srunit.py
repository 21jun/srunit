import os
import argparse
from pathlib import Path
import shutil
from string import Template




def main():

    # check if there is a.conf file under .srunit directory
    # if exists, set value `custom_config` to True
    custom_config = False
    custom_config_dir = Path(".srunit")
    if custom_config_dir.is_dir():
        custom_config = True
        for file in list(custom_config_dir.glob('**/*')):
            if file.suffix == ".conf":
                with open(file, "r") as f:
                    values = f.read()
                break

    # print(custom_config)
    if custom_config:
        print("Custom config file found")
    else:
        print("No custom config file found")
    # if there is no custom config file, use default.conf
    if not custom_config:
        # read cache/default.conf and save its value to `values`
        with open("cache/default.conf", "r") as f:
            values = f.read()

    for value in values.split("\n"):
        print(value)

    defaults ={}
    for value in values.split("\n"):
        if len(value) == 0:
            continue
        key, val = value.split("=")
        # can we save it into dictionary?
        if val.isdigit():
            val = int(val)
        elif val == "":
            val = None
        defaults[key] = val

    # print(defaults)


    parser = argparse.ArgumentParser(description="Argparse Tutorial")
    parser.add_argument("--dry_run", "-d", action="store_true")

    for key, val in defaults.items():
        arg_key = "--" + key.lower().replace("-","_")
        print(arg_key)
        parser.add_argument(arg_key, default=val)

    args = parser.parse_args()

    print(args)

    JOB_NAME = args.job_name
    OUTPUT_PATH = args.output_path
    GPU_TYPE = args.gpu_type
    GPU_NUM = args.gpu_num
    CPU_NUM = args.cpu_num
    SCRIPT_PATH = args.script_path
    CHECKPOINTS_PATH = "checkpoints"
    ADDITIONAL_ARGS = ""
    DRY_RUN = args.dry_run

    # Additional

    exp_root = Path(SCRIPT_PATH).parent
    RUN_ROOT_PATH = exp_root / "runs"

    i = 0
    while os.path.exists(RUN_ROOT_PATH / f"run_{i}"):
        i += 1
    # get output_path by script_path

    RUN_PATH = RUN_ROOT_PATH / f"run_{i}"
    if not DRY_RUN:
        Path.mkdir(RUN_PATH, exist_ok=True, parents=True)

    OUTPUT_PATH = RUN_PATH / "out"
    if not DRY_RUN:
        Path.mkdir(OUTPUT_PATH, exist_ok=True, parents=True)

    RUN_SCRIPT_PATH = RUN_PATH / "finetune.sh"
    if not DRY_RUN:
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



if __name__ == "__main__":

   main()