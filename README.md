# Blender Data Generation

This is the official repository for the paper : [C3I-SynFace: A synthetic head pose and facial 
depth dataset using seed virtual human models.](https://doi.org/10.1016/j.dib.2023.109087) 

* Import FBX from iClone
* Import Missing Files in Blender
* Scene Setup in Blender
* Compositor Setup in Blender
* Render Ground Truth with Cycle Render Engine

###  Additionally - #
* Data Preparation Script
* Neck Bone Adjustment through Iterative Script

* Blender Scenes can be downloaded from - 
https://drive.google.com/file/d/18UF2DQpHQ5N7L9Z-LCcD4P_elj_-LDco/view?usp=sharing

![blenderSetup.png](Assets%2FblenderSetup.png)

![samples.png](Assets%2Fsamples.png)


## Install package within Blender Python

* Open Blender python editor
* Locate the blender python version 
  
  Normally in the <Blender_Root>/<Blender_Version>2.93/python/bin
  
  Run the following scripts from Blender python terminal - 

```shell
# directory - face3d/mesh/cython
import sys 
import os 
import subprocess 
  

python_exe = os.path.join(sys.prefix, 'bin','python3.9')

# Upgrade Pip
subprocess.call([python_exe, "-m", "ensurepip"]) 
subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"]) 

# Install sympy
subprocess.call([python_exe, "-m", "pip", "install", "sympy"]) 

```

## Dataset

The raw dataset can be found in the following path (alternate to Mendeley) - 

3D full body model -

 https://drive.google.com/drive/folders/177Xem5rLg7GYRn6IDwWMwZtBgr57OrtB?usp=share_link

Head Pose dataset - 

https://drive.google.com/drive/folders/10QNIb4Rp9D7SHMbdiK3ecbZFIL_bNOEY?usp=share_link

Face depth Dataset - 

https://drive.google.com/drive/folders/1oleqLbR793xBmw8gF91JTi4TrBJQUMr2?usp=share_link


## Citation

If you find our work useful to your research, please consider citing:

```

@article{basak2023c3i,
  title={C3I-SynFace: A synthetic head pose and facial depth dataset using seed virtual human models.},
  author={Basak, Shubhajit and Khan, Faisal and Javidnia, Hossein and Corcoran, Peter and McDonnell, Rachel and Schukat, Michael},
  journal={Data in Brief},
  pages={109087},
  year={2023},
  publisher={Elsevier}
}


```
