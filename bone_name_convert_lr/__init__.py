# coding : utf-8

bl_info = {
    "name" : "Convert _L_R at bone names (en<->jp)",
    "author" : "LNSEAB",
    "version" : ( 1, 0 ),
    "blender" : ( 2, 73, 0 ),
    "location" : "View3D > Object > Apply",
    "category" : "Object"
}

import bpy
import re

target_pairs = [( "_L", "左" ), ( "_R", "右" )]

def split_extract_number(name) :
    m = re.search( "(\.[0-9]+)$", name )
    if( m == None ) :
        return ( name, "" )
    return ( name[0:m.start()], m.group( 0 ) )

def convert_lr_en_to_jp(self, context) :
    for arm in bpy.data.armatures :
        for b in arm.bones :
            for t in target_pairs :
                sn = split_extract_number( str( b.name ) )
                if sn[0].endswith( t[0] ) :
                    b.name = t[1] + sn[0].rstrip( t[0] ) + sn[1]
                    break

def convert_lr_jp_to_en(self, context) :
    for arm in bpy.data.armatures :
        for b in arm.bones :
            for t in target_pairs :
                sn = split_extract_number( str( b.name ) )
                if sn[0].startswith( t[1] ) :
                    b.name = sn[0].lstrip( t[1] ) + t[0] + sn[1]
                    break

class bone_convert_lr_en_to_jp(bpy.types.Operator) :
    """Convert _L_R at bone names (English -> Japanese)"""
    bl_idname = "bone.convert_lr_en_to_jp"
    bl_label = "Convert_LR_en_to_jp"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context) :
        convert_lr_en_to_jp(self, context)
        return { 'FINISHED' }

class bone_convert_lr_jp_to_en(bpy.types.Operator) :
    """Convert _L_R at bone names (Japanese -> English)"""
    bl_idname = "bone.convert_lr_jp_to_en"
    bl_label = "Convert_LR_jp_to_en"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context) :
        convert_lr_jp_to_en(self, context)
        return { 'FINISHED' }

text_dir = {
    "en_EN" : { 
        ( "*", "conv_lr_enjp" ) : "Convert _L_R at bone names (En->Jp)",
        ( "*", "conv_lr_jpen" ) : "Convert _L_R at bone names (Jp->En)"
    },
    "ja_JP" : {
        ( "*", "conv_lr_enjp" ) : "ボーン名の「_L_R」を「左右」に変換",
        ( "*", "conv_lr_jpen" ) : "ボーン名の「左右」を「_L_R」に変換"
    }
}

def get_menu_text(name) :
    if bpy.context.user_preferences.system.use_international_fonts :
        return bpy.app.translations.pgettext( name )

    return text_dir["en_EN"][( "*", name )]

def invoke_convert_lr_en_to_jp(self, context) :
    self.layout.operator( bone_convert_lr_en_to_jp.bl_idname, text=get_menu_text( "conv_lr_enjp" ) )

def invoke_convert_lr_jp_to_en(self, context) :
    self.layout.operator( bone_convert_lr_jp_to_en.bl_idname, text=get_menu_text( "conv_lr_jpen" ) )

def register() :
    bpy.utils.register_class( bone_convert_lr_en_to_jp )
    bpy.utils.register_class( bone_convert_lr_jp_to_en )
    bpy.app.translations.register( __name__, text_dir )
    bpy.types.VIEW3D_MT_object_apply.append( invoke_convert_lr_en_to_jp )
    bpy.types.VIEW3D_MT_object_apply.append( invoke_convert_lr_jp_to_en )

def unregister() :
    bpy.utils.unregister_class( bone_convert_lr_en_to_jp )
    bpy.utils.unregister_class( bone_convert_lr_jp_to_en )
    bpy.app.translations.unregister( __name__ )
    bpy.types.VIEW3D_MT_object_apply.remove( invoke_convert_lr_en_to_jp )
    bpy.types.VIEW3D_MT_object_apply.remove( invoke_convert_lr_jp_to_en )

if __name__ == "__main__" :
    register()
