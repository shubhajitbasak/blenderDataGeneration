import bpy

bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree

# clear default nodes
for node in tree.nodes:
    tree.nodes.remove(node)

basePath = '../data/Data'
filepath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1])
filepath = filepath.replace('Simple', 'Complex/Barbershop')

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

fileOutput_node.file_slots.new("depthExr")
fileOutput_node.file_slots['depthExr'].format.file_format = 'OPEN_EXR'
fileOutput_node.file_slots['depthExr'].format.color_mode = 'RGB'
fileOutput_node.file_slots['depthExr'].format.use_zbuffer = True
fileOutput_node.file_slots['depthExr'].use_node_format = False

links.new(renderLayer_node.outputs[0], fileOutput_node.inputs[0])
links.new(renderLayer_node.outputs[2], fileOutput_node.inputs[1])

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
bpy.context.scene.cycles.aa_samples = 64
bpy.context.scene.cycles.min_transparent_bounces = 32
bpy.context.scene.cycles.light_sampling_threshold = 0
bpy.context.scene.cycles.sample_clamp_indirect = 0

bpy.context.scene.cycles.max_bounces = 32
bpy.context.scene.cycles.diffuse_bounces = 0
bpy.context.scene.cycles.glossy_bounces = 0
bpy.context.scene.cycles.transparent_max_bounces = 16
bpy.context.scene.cycles.transmission_bounces = 16

bpy.context.scene.render.resolution_x = 640
bpy.context.scene.render.resolution_y = 480

bpy.ops.wm.save_mainfile()