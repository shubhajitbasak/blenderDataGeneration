from easydict import EasyDict as edict

config = edict()

# Path to the model directory containing the fbx files
config.modelRoot = r'/mnt/fastssd/synData/FullBodyModels/'
# path to the blender installation
config.blenderPath = r'/mnt/fastssd/blender-2.93.0/blender '
# path to the simple scene environment
config.blendFileSimple = r'/mnt/fastssd/synData/Environments/SimpleScene/simpleScene.blend'