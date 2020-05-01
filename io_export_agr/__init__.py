import bpy
import sys
import os
from bpy.types import Menu
from . import export_agr

bl_info = {
    "name": "Export AGR",
    "author": "filiperino",
    "version": (1, 1, 1),
    "blender": (2, 82, 0),
    "location": "File > Export",
    "description": "Utility for exporting and manipulating AGR",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
    }

"""
Alot of the code in this script is from the agr addon made by Darkhandrob (https://github.com/Darkhandrob).
I just reworked it to my own needs I guess that's okay.
"""


class AgrtoFbx(bpy.types.Operator):

    """Exports AGR players with custom root to FBX format"""   # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "io_export_agr.agrtofbx"        # unique identifier for buttons and menu items to reference.
    bl_label = "AGR (.fbx)"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}  # enable undo and setting presets for the operator.

    # Properties used by the file browser
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    global_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale everything by this value (0.01 old default, 0.0254 is more accurate)",
        min=0.0001, max=100.0,
        soft_min=0.001, soft_max=1.0,
        default=0.01,
    )

    custom_frame_range: bpy.props.BoolProperty(
        name="Custom frame range",
        description="Whether set frame range from action length or use the one set by the user",
        default=True,
    )

    root_name: bpy.props.StringProperty(
        name="Root Name",
        description="Set the root bone name for each player",
        default="player",
    )



    def menu_draw_export(self, context):
        layout = self.layout
        layout.operator("io_export_agr.agrtofbx", text="AGR (.fbx)")

    # Open the filebrowser with the custom properties
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # main function
    def execute(self, context):
        export_agr.AgrtoFbx(self, context)
        return {'FINISHED'}

class MergeAnims(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "io_export_agr.merge_anims"
    bl_label = "Merge Anims"

    def execute(self, context):
        export_agr.MergeAnims(self, context)
        return {'FINISHED'}

class io_export_agr_menu(Menu):
    """Creates a Pie Menu for the toolset"""
    bl_idname = "AGRToolset_Menu"
    bl_label = "Merge Anims"


    def draw(self, context):
        
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("io_export_agr.merge_anims")
        pie.operator("io_export_agr.agrtofbx")



classes = (
    io_export_agr_menu,
    AgrtoFbx,
    MergeAnims,
)

def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi_mnu = km.keymap_items.new("wm.call_menu_pie", "COMMA", "PRESS", shift=True)
    kmi_mnu.properties.name = io_export_agr_menu.bl_idname


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)
    #bpy.context.window_manager.keyconfigs.addon.keymaps.


if __name__ == "__main__":
    unregister()
    register()