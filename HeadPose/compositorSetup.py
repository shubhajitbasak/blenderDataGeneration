import bpy

bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree

# clear default nodes
for node in tree.nodes:
    tree.nodes.remove(node)

basePath = '/mnt/fastssd/Shubhajit_Stuff/dataCreation/Data/'
filepath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1])
# filepath = filepath.replace('Simple','Textured')

# create Render Layer node
renderLayer_node = tree.nodes.new('CompositorNodeRLayers')
renderLayer_node.location = 0, 0

# create Normalize node
normalize_node = tree.nodes.new('CompositorNodeNormalize')
normalize_node.location = 200, 0

# create output node
comp_node = tree.nodes.new('CompositorNodeComposite')
comp_node.location = 400, 0

# link nodes
links = tree.links
links.new(renderLayer_node.outputs[2], normalize_node.inputs[0])

links.new(normalize_node.outputs[0], comp_node.inputs[0])

# create output node
fileOutput_node = tree.nodes.new('CompositorNodeOutputFile')
fileOutput_node.location = 400, -100
fileOutput_node.base_path = filepath
fileOutput_node.format.color_mode = 'RGB'
fileOutput_node.file_slots[0].path = f'rgb'
fileOutput_node.file_slots[0].format.file_format = 'JPEG'
fileOutput_node.file_slots[0].use_node_format = False
links.new(renderLayer_node.outputs[0], fileOutput_node.inputs[0])

# setup render params
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.render.resolution_x = 640
bpy.context.scene.render.resolution_y = 480

# save blender file
bpy.ops.wm.save_mainfile()
