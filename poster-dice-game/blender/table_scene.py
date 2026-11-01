"""The Yoko Ono dice table in Blender: walnut box, green felt with the gold logo, two red casino dice.

Runs headless with the `bpy` package (pip install bpy):
    python table_scene.py --preview    # quick low-res check -> out/table-preview.png
    python table_scene.py              # full render         -> ../photo/table-hero.png
Units are metres. +Y runs away from the camera, toward the far ("opposite") wall.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = "--preview" in sys.argv

# Box interior (felt) and frame, roughly the table in the photo
IN_W, IN_D = 0.60, 0.80
FRAME_T, FRAME_H = 0.032, 0.085
FELT_WALL_T, FELT_WALL_H = 0.006, 0.07
LOGO_W = 0.24                    # printed logo width on the felt
LOGO_Y = 0.13                    # logo centre, toward the far wall
DIE = 0.025                      # die edge (about a ninth of the logo width, as in the video)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64 if PREVIEW else 192
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 16
    scene.cycles.transmission_bounces = 16
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.render.resolution_x, scene.render.resolution_y = (3300, 2400)
    scene.render.resolution_percentage = 25 if PREVIEW else 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Khronos PBR Neutral"
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
    scene.world = world
    return scene


def material(name, build):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    shader = build(nt)
    nt.links.new(shader.outputs[0], out.inputs["Surface"])
    return mat


def principled(nt, **inputs):
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    for k, v in inputs.items():
        p.inputs[k].default_value = v
    return p


def felt_material(with_logo=False):
    def build(nt):
        p = principled(nt, **{"Roughness": 1.0, "Sheen Weight": 0.35, "Sheen Roughness": 0.5,
                              "Sheen Tint": (0.35, 1.0, 0.5, 1)})
        tex = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 900
        noise.inputs["Detail"].default_value = 6
        nt.links.new(tex.outputs["Object"], noise.inputs["Vector"])
        blotch = nt.nodes.new("ShaderNodeTexNoise")
        blotch.inputs["Scale"].default_value = 9
        nt.links.new(tex.outputs["Object"], blotch.inputs["Vector"])
        tint = nt.nodes.new("ShaderNodeMix")
        tint.data_type = "RGBA"
        tint.inputs["A"].default_value = (0.003, 0.095, 0.022, 1)
        tint.inputs["B"].default_value = (0.005, 0.135, 0.032, 1)
        nt.links.new(blotch.outputs["Fac"], tint.inputs["Factor"])
        nt.links.new(tint.outputs["Result"], p.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.25
        bump.inputs["Distance"].default_value = 0.0004
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
        if not with_logo:
            return p
        # Gold print: the logo mask, placed by the floor's own coordinates, mixes metallic gold over the felt
        gold = principled(nt, **{"Base Color": (0.95, 0.72, 0.40, 1), "Metallic": 0.45, "Roughness": 0.42})
        nt.links.new(bump.outputs["Normal"], gold.inputs["Normal"])
        img = nt.nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(os.path.join(HERE, "logo-mask.png"))
        mask_w, mask_h = img.image.size
        logo_h = LOGO_W * mask_h / mask_w
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1 / LOGO_W, 1 / logo_h, 1)
        mapping.inputs["Location"].default_value = (0.5, 0.5 - LOGO_Y / logo_h, 0)
        nt.links.new(tex.outputs["Object"], mapping.inputs["Vector"])
        img.image.colorspace_settings.name = "Non-Color"
        img.extension = "CLIP"
        nt.links.new(mapping.outputs["Vector"], img.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(img.outputs["Color"], mix.inputs["Fac"])
        nt.links.new(p.outputs[0], mix.inputs[1])
        nt.links.new(gold.outputs[0], mix.inputs[2])
        return mix
    return material("Felt with logo" if with_logo else "Felt", build)


def walnut_material():
    def build(nt):
        p = principled(nt, **{"Roughness": 0.38, "Coat Weight": 0.35, "Coat Roughness": 0.15})
        tex = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1.0, 1.0, 18.0)
        nt.links.new(tex.outputs["Object"], mapping.inputs["Vector"])
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "RINGS"
        wave.inputs["Scale"].default_value = 6
        wave.inputs["Distortion"].default_value = 9
        wave.inputs["Detail"].default_value = 4
        nt.links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.09, 0.040, 0.018, 1)
        ramp.color_ramp.elements[1].color = (0.30, 0.15, 0.070, 1)
        nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
        return p
    return material("Walnut", build)


def dice_material():
    def build(nt):
        return principled(nt, **{"Base Color": (1.0, 0.04, 0.05, 1), "Roughness": 0.03,
                                 "Transmission Weight": 1.0, "IOR": 1.49})
    mat = material("Red dice", build)
    nt = mat.node_tree
    absorb = nt.nodes.new("ShaderNodeVolumeAbsorption")
    absorb.inputs["Color"].default_value = (0.92, 0.015, 0.04, 1)
    absorb.inputs["Density"].default_value = 90
    nt.links.new(absorb.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    return mat


def pip_material():
    def build(nt):
        return principled(nt, **{"Base Color": (0.92, 0.91, 0.88, 1), "Roughness": 0.45})
    return material("Pip paint", build)


def box(name, size, loc, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    ob.data.materials.append(mat)
    return ob


def build_table(felt, floor, walnut):
    # Felt floor, a base under it, the walnut frame and the felt-lined inner walls
    box("Felt floor", (IN_W, IN_D, 0.01), (0, 0, -0.005), floor)
    box("Base", (IN_W + 2 * FRAME_T, IN_D + 2 * FRAME_T, 0.02), (0, 0, -0.02), walnut, 0.003)
    hw, hd = IN_W / 2 + FRAME_T / 2, IN_D / 2 + FRAME_T / 2
    z = FRAME_H / 2 - 0.01
    box("Frame left", (FRAME_T, IN_D + 2 * FRAME_T, FRAME_H), (-hw, 0, z), walnut, 0.004)
    box("Frame right", (FRAME_T, IN_D + 2 * FRAME_T, FRAME_H), (hw, 0, z), walnut, 0.004)
    box("Frame far", (IN_W, FRAME_T, FRAME_H), (0, hd, z), walnut, 0.004)
    box("Frame near", (IN_W, FRAME_T, FRAME_H), (0, -hd, z), walnut, 0.004)
    t = FELT_WALL_T / 2
    box("Felt wall left", (FELT_WALL_T, IN_D, FELT_WALL_H), (-IN_W / 2 + t, 0, FELT_WALL_H / 2), felt, 0.002)
    box("Felt wall right", (FELT_WALL_T, IN_D, FELT_WALL_H), (IN_W / 2 - t, 0, FELT_WALL_H / 2), felt, 0.002)
    box("Felt wall far", (IN_W, FELT_WALL_T, FELT_WALL_H), (0, IN_D / 2 - t, FELT_WALL_H / 2), felt, 0.002)
    box("Felt wall near", (IN_W, FELT_WALL_T, FELT_WALL_H), (0, -IN_D / 2 + t, FELT_WALL_H / 2), felt, 0.002)


# Pip centres on a face, in units of the die edge, (u, v) in [-0.5, 0.5]
PIPS = {
    1: [(0, 0)],
    2: [(-0.25, -0.25), (0.25, 0.25)],
    3: [(-0.25, -0.25), (0, 0), (0.25, 0.25)],
    4: [(-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)],
    5: [(-0.25, -0.25), (0.25, -0.25), (0, 0), (-0.25, 0.25), (0.25, 0.25)],
    6: [(-0.25, -0.27), (-0.25, 0), (-0.25, 0.27), (0.25, -0.27), (0.25, 0), (0.25, 0.27)],
}
# Opposite faces add up to 7: +Z 6 / -Z 1, -Y 2 / +Y 5, +X 3 / -X 4
FACES = {
    6: (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))),
    1: (Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, 1, 0))),
    2: (Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))),
    5: (Vector((0, 1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))),
    3: (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
    4: (Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
}


def die(name, loc, rot_z, body, paint):
    """A sharp-edged translucent casino die with painted, slightly sunken pips."""
    bpy.ops.mesh.primitive_cube_add(size=DIE, location=(0, 0, 0))
    cube = bpy.context.object
    cube.name = name
    bev = cube.modifiers.new("Bevel", "BEVEL")
    bev.width = DIE * 0.035
    bev.segments = 3
    cube.data.materials.append(body)
    pip_r, depth = DIE * 0.085, DIE * 0.03
    pips = []
    for n, (normal, u, v) in FACES.items():
        for pu, pv in PIPS[n]:
            centre = normal * (DIE / 2) + u * (pu * DIE) + v * (pv * DIE)
            # A hole cut into the body ...
            bpy.ops.mesh.primitive_cylinder_add(radius=pip_r, depth=depth * 2, vertices=32, location=centre)
            cutter = bpy.context.object
            cutter.rotation_euler = normal.to_track_quat("Z", "Y").to_euler()
            mod = cube.modifiers.new("Pip", "BOOLEAN")
            mod.object = cutter
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            pips.append(cutter)
    bpy.context.view_layer.objects.active = cube
    for mod in list(cube.modifiers):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for cutter in pips:
        # ... then the cutter shrinks into a disc of white paint at the bottom of the hole
        cutter.scale = (0.98, 0.98, 0.45)
        normal = cutter.rotation_euler.to_matrix() @ Vector((0, 0, 1))
        cutter.location -= normal * depth * 0.55
        cutter.data.materials.append(paint)
        cutter.parent = cube
    cube.location = loc
    cube.rotation_euler = (0, 0, math.radians(rot_z))
    return cube


def lights_and_camera(scene):
    # Warm key spot from above, falling off to black at the box edges
    bpy.ops.object.light_add(type="SPOT", location=(0.06, -0.10, 0.85))
    key = bpy.context.object
    key.data.energy = 34
    key.data.color = (1.0, 0.86, 0.68)
    key.data.spot_size = math.radians(32)
    key.data.spot_blend = 1.0
    key.data.shadow_soft_size = 0.12
    key.rotation_euler = (Vector((0, 0.07, 0)) - key.location).to_track_quat("-Z", "Y").to_euler()
    # Low back lights inside the box, to make the red dice glow from behind
    # (kept low and to the sides so they don't mirror in the dice tops)
    for x in (-0.18, 0.18):
        bpy.ops.object.light_add(type="AREA", location=(x, 0.30, 0.05))
        rim = bpy.context.object
        rim.data.energy = 0.8
        rim.data.size = 0.08
        rim.data.color = (1.0, 0.8, 0.6)
        rim.rotation_euler = (Vector((0, 0.03, 0.01)) - rim.location).to_track_quat("-Z", "Y").to_euler()
    # Soft fill from the camera side
    bpy.ops.object.light_add(type="AREA", location=(-0.35, -0.6, 0.45))
    fill = bpy.context.object
    fill.data.energy = 0.8
    fill.data.size = 0.6
    fill.rotation_euler = (Vector((0, 0.05, 0)) - fill.location).to_track_quat("-Z", "Y").to_euler()

    bpy.ops.object.camera_add(location=(0, -0.17, 0.12))
    cam = bpy.context.object
    target = Vector((0, 0.10, 0.0))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 32
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (Vector((0, 0.03, 0.01)) - cam.location).length
    cam.data.dof.aperture_fstop = 8
    scene.camera = cam


def main():
    scene = reset()
    felt, floor, walnut = felt_material(), felt_material(with_logo=True), walnut_material()
    body, paint = dice_material(), pip_material()
    build_table(felt, floor, walnut)
    # Double six, in front of the logo (the logo sits behind the dice from the camera)
    die("Die left", (-0.036, 0.000, DIE / 2), 18, body, paint)
    die("Die right", (0.034, -0.012, DIE / 2), -14, body, paint)
    lights_and_camera(scene)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    target = os.path.join(HERE, "out", "table-preview.png") if PREVIEW else os.path.join(HERE, "..", "photo", "table-hero.png")
    scene.render.filepath = target
    bpy.ops.render.render(write_still=True)
    print("wrote", os.path.relpath(target, HERE))


main()
