# Blender Data Generation
* Import FBX from iClone
* Import Missing Files in Blender
* Scene Setup in Blender
* Compositor Setup in Blender
* Render Ground Truth with Cycle Render Engine

###  Additionally - #
* Data Preparation Script
* Neck Bone Adjustment through Iterative Script

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

[//]: # (## Dataset)

[//]: # (We have released the dataset for the 3D models - )

[//]: # ()
[//]: # (https://ieee-dataport.org/documents/c3i-synthetic-human-dataset)

[//]: # (## Citation)

[//]: # (If you find our work useful to your research, please consider citing:)

[//]: # (```)

[//]: # (@data{f6zx-bf29-22,)

[//]: # (doi = {10.21227/f6zx-bf29},)

[//]: # (url = {https://dx.doi.org/10.21227/f6zx-bf29},)

[//]: # (author = {Basak, Shubhajit and Khan, Faisal and Javidnia, Hossein and McDonnell, Rachel and Schukat, Michael and Corcoran, Peter},)

[//]: # (publisher = {IEEE Dataport},)

[//]: # (title = {C3I SYNTHETIC HUMAN DATASET},)

[//]: # (year = {2022} })

[//]: # ()
[//]: # (```)
