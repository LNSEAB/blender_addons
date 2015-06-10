# coding : utf-8

import bpy
import bmesh
import io
import sys
import platform

def make_camera(scene) :
    cam = bpy.data.cameras.new( "uv_tmp" )
    cam.type = 'ORTHO'
    cam.ortho_scale = 1.0

    obj_cam = bpy.data.objects.new( "uv_tmp_camera", cam )
    obj_cam.location = 0.5, 0.5, 1.0
    scene.objects.link( obj_cam )
    scene.camera = obj_cam
    
    return cam, obj_cam

def make_wire_material(scene, mesh) :
    mtrl = bpy.data.materials.new( "uv_tmp_wire" )
    mtrl.type = 'WIRE'
    mtrl.use_shadeless = True
    mtrl.diffuse_color = 0, 0, 0

    obj = bpy.data.objects.new( "uv_tmp_wire", mesh )

    base = scene.objects.link( obj )
    base.layers[0] = True

    obj.material_slots[0].link = 'OBJECT'
    obj.material_slots[0].material = mtrl

    return mtrl, obj

def make_materials(scene, mesh, dst_mesh, opacity) :
    solids = []

    for i in range( max( 1, len( mesh.materials ) ) ) :
        solid = bpy.data.materials.new( "uv_tmp_solid" )
        obj = bpy.data.objects.new( "uv_tmp_soild", dst_mesh )
        obj.location = 0, 0, -1
        base = scene.objects.link( obj )
        base.layers[0] = True
        solids.append( ( solid, obj ) )
        dst_mesh.materials.append( solid )

    for i, dst in enumerate( solids ) :
        if mesh.materials and mesh.materials[i] : 
            dst[0].diffuse_color = mesh.materials[i].diffuse_color
        dst[0].use_shadeless = True
        dst[0].use_transparency = True
        dst[0].alpha = opacity

    return solids

def make_uv_mtrl_idx(mesh) :
    uv_layer = None
    if mesh.uv_layers == None or mesh.uv_layers.active == None or mesh.uv_layers.active.data == None :
        raise RuntimeError( mesh.name + " : UV Data None" )

    uv_layer = mesh.uv_layers.active.data

    polys = mesh.polygons

    uv_mtrl_idx = []
    for i, p in enumerate( polys ) :
        start = p.loop_start
        end = start + p.loop_total
        uvs = tuple( ( elem.uv[0], elem.uv[1] ) for elem in uv_layer[start : end] )
        uv_mtrl_idx.append( ( uvs, p.material_index ) )

    return uv_mtrl_idx

def append_faces(src_mesh, mesh, mtrl_offset) :
    faces = make_uv_mtrl_idx( src_mesh )

    vertices = []
    materials = []
    start_loops = []
    total_loops = []
    loops_vertices = []

    v_index = len( mesh.vertices )
    vtx_len = len( mesh.vertices )
    loop_len = len( mesh.loops )
    poly_len = len( mesh.polygons )

    for uvs, idx in faces :
        num_vtx = len( uvs )
        for uv in uvs :
            vertices.append( ( uv[0], uv[1], 0.0 ) )
        start_loops.append( v_index )
        total_loops.append( num_vtx )
        loops_vertices += range( v_index, v_index + num_vtx )
        materials.append( mtrl_offset + idx )
        v_index += num_vtx

    mesh.vertices.add( v_index - vtx_len )
    mesh.loops.add( v_index - vtx_len )
    mesh.polygons.add( len( start_loops ) )

    for i in range( len( vertices ) ) :
        mesh.vertices[vtx_len + i].co = vertices[i]
    for i in range( len( loops_vertices ) ) :
        mesh.loops[loop_len + i].vertex_index = loops_vertices[i]
    for i in range( len( start_loops ) ) :
        mesh.polygons[poly_len + i].loop_start = start_loops[i]
    for i in range( len( total_loops ) ) :
        mesh.polygons[poly_len + i].loop_total = total_loops[i]
    for i in range( len( materials ) ) :
        mesh.polygons[poly_len + i].material_index = materials[i]

def remove_doubles(mesh) :
    bm = bmesh.new()
    bm.from_mesh( mesh )
    bmesh.ops.remove_doubles( bm, verts=bm.verts, dist=0.00001 )
    bm.to_mesh( mesh )
    bm.free()

def render(filepath, size, scene, mesh) :
    scene.render.use_raytrace = False
    scene.render.alpha_mode = 'TRANSPARENT'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.resolution_x = size[0]
    scene.render.resolution_y = size[1]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = filepath

    if size[0] > size[1] :
        scene.render.pixel_aspect_y = size[0] / size[1]
    elif size[0] < size[1] :
        scene.render.pixel_aspect_x = size[1] / size[0]

    scene.frame_start = 1
    scene.frame_end = 1
    
    data_context = { "blend_data" : bpy.context.blend_data, "scene" : scene }
    bpy.ops.render.render( data_context, write_still = True )

def export(**param) :
    old_sysout = None

    if platform.system() == "Windows" :
        old_sysout = sys.stdout
        sys.stdout = io.TextIOWrapper( sys.stdout.buffer, encoding = "cp932" )

    objs = bpy.context.selected_objects

    editing_obj = None
    for obj in objs :
        if obj.mode == "EDIT" :
            bpy.ops.object.mode_set( mode="OBJECT", toggle=False )
            editing_obj = obj
            break
    bpy.data.materials.new( "uv_tmp_solid" )
    filepath = bpy.path.ensure_ext( param["filepath"], ".png" )

    scene = bpy.data.scenes.new( "uv_tmp" )
    mesh = bpy.data.meshes.new( "uv_tmp" )
    cam, obj_cam = make_camera( scene )

    solid_mtrls = []
    mtrl_offset = 0

    for obj in objs :
        try :
            if obj and obj.type == 'MESH' and obj.data.uv_textures :
                solid_mtrls.append( make_materials( scene, obj.data, mesh, param["opacity"] ) )
                append_faces( obj.data, mesh, mtrl_offset )
                mtrl_offset += len( obj.data.materials )
        except RuntimeError as e :
            print( e )

    mesh.update( calc_edges = True )

    wire_mtrl, wire_mtrl_obj = make_wire_material( scene, mesh )

    remove_doubles( mesh )

    render( filepath, param["size"], scene, mesh )

    bpy.data.scenes.remove( scene )

    bpy.data.objects.remove( obj_cam )
    bpy.data.objects.remove( wire_mtrl_obj )
    for sm in solid_mtrls :
        for s in sm :
            bpy.data.objects.remove( s[1] )

    bpy.data.cameras.remove( cam )
    bpy.data.meshes.remove( mesh )
    bpy.data.materials.remove( wire_mtrl )
    
    for sm in solid_mtrls :
        for s in sm :
            bpy.data.materials.remove( s[0] )

    if editing_obj != None :
        bpy.ops.object.mode_set( mode="EDIT", toggle=False )

    if old_sysout != None :
        sys.stdout = old_sysout

    return { 'FINISHED' }
