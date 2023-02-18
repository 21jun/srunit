# srunit

# Installation


1. Clone Project

```
git clone https://github.com/21jun/srunit.git
```

2. Set alias on ~/.bashrc

```
echo alias srunit=\"python ~/___YOUR_PATH___/srunit/srunit.py" >> ~/.bashrc
```
or 

```
vim ~/.bashrc

(Add line below at the end of file.)

alias srunit=\"python ~/___YOUR_PATH___/srunit/srunit.py" >> ~/.bashrc
```



3. Initialize 

`source ~/.bashrc` for initialize

# How to use it?

1. place your shell script under experiments directory
<img width="364" alt="image" src="https://user-images.githubusercontent.com/29483429/219865452-6b25caae-f820-4838-9cd3-12f4a42918ef.png">

2. run `srunit` with -f flag to specify your shell script

`srunit -t A100 -n 4 -f exp/v1/el/finetune_template.sh`

tip. you can use -d flag to make dry run (create sbatch scirpt only)

`srunit -t A100 -n 4 -f exp/v1/el/finetune_template.sh -d`

output log:
```sh
#!/bin/bash

#SBATCH -J default # job name
#SBATCH -o exp/v1/el/runs/run_1/out/output_%x.%j.out 
#SBATCH -p A100 # queue name or partiton name
#SBATCH -t 72:00:00 # Run time (hh:mm:ss)
#SBATCH  --gres=gpu:4
#SBATCH  --nodes=1
#SBATCH  --ntasks=1
#SBATCH  --tasks-per-node=1
#SBATCH  --cpus-per-task=16

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
cat exp/v1/el/runs/run_1/finetune.sh
echo "START"
sh exp/v1/el/runs/run_1/finetune.sh 4 exp/v1/el/runs/run_1/checkpoints
date
    
Submitted batch job 9919
```

3. check your `sbatch` script and output files under `runs` dir

<img width="302" alt="image" src="https://user-images.githubusercontent.com/29483429/219865617-e6a337e6-e6d6-42da-ad94-5876cc20f049.png">

`run_x` : x is incremental number


