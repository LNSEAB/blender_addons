# coding : utf-8

bl_info = {
    "name" : "Nclr UV Layout",
    "author" : "LNSEAB",
    "version" : ( 1, 0 ),
    "blender" : ( 2, 74, 0 ),
    "location" : "Image-Window > UVs > Nclr Export UV Layout",
    "description" : "",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Import-Export",
}

import bpy

text_dir = {
    "ja_JP" : {
        ( "*", "Export UV Layout of Selected Objects" ) : "選択したオブジェクトのUVレイアウトをエクスポート"
    }
}

class nclr_export_uv_layout(bpy.types.Operator) :
    """Export UV Layout of Selected Objects"""

    bl_idname = "uv.export_uv_layout"
    bl_label = "Export UV Layout of Selected Objects"
    bl_options = { 'REGISTER', 'UNDO' }

    filepath = bpy.props.StringProperty(
        subtype = 'FILE_PATH'
    )

    check_exisiting = bpy.props.BoolProperty(
        name = "Check Exisiting",
        default = True,
        options = { 'HIDDEN' }
    )
    
    size = bpy.props.IntVectorProperty(
        size = 2,
        default = ( 1024, 1024 ),
        min = 8,
        max = 32768,
    )

    opacity = bpy.props.FloatProperty(
        name = "Fill Opacity",
        default = 0.25,
        min = 0.0,
        max = 1.0
    )

    def execute(self, context) :
        from . import impl
        return impl.export(
            filepath=self.filepath,
            size=self.size,
            opacity=self.opacity
        )

    def check(self, context) :
        filepath = bpy.path.ensure_ext( self.filepath, ".png" )
        if filepath != self.filepath :
            self.filepath = filepath
            return True
        else :
            return False

    def invoke(self, context, event) :
        import os
        self.filepath = os.path.splitext( bpy.data.filepath )[0]
        context.window_manager.fileselect_add( self )
        return { 'RUNNING_MODAL' }

def menu_func(self, context) :
    self.layout.operator( nclr_export_uv_layout.bl_idname, text=bpy.app.translations.pgettext( "Export UV Layout of Selected Objects" ) )

def register() :
    bpy.utils.register_module( __name__ )
    bpy.app.translations.register( __name__, text_dir )
    bpy.types.IMAGE_MT_uvs.append( menu_func )

def unregister() :
    bpy.utils.unregister_module( __name__ )
    bpy.app.translations.unregister( __name__ )
    bpy.types.IMAGE_MT_uvs.remove( menu_func )

if __name__ == "__main__" :
    register()
