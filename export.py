bl_info = {
    "name": "AGR Toolset",
    "author": "filiperino",
    "version": (2, 0, 0),
    "blender": (2, 81, 0),
    "location": "",
    "description": "Toolset for exporting and manipulating AGR",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
    }


# Alot of the code in this script is from the agr addon made by (https://github.com/Darkhandrob)
# I just reworked it to my own needs i guess thats okay


import bpy, time, os
from bpy.types import Menu


def main(context):
    # Ragdollanimation .hide_render is set as True at Frame 1
    # But if he was killed before starting recording, it is also the Ragdoll is False and Run is True
    # Each Type of Model gets its own Array inside the Array


    PlayerAnims = [] # Each type of model gets its own array inside this array

    # Find first Ragdoll and then Run Animation
    for CurrMdl in bpy.data.objects:
        # Find Player Models (which are named tm or ctm)
        if (CurrMdl.name.find("afx.") != -1 and CurrMdl.name.find("tm") != -1):
            
            # Find Ragdoll Animation and Changing Point of hide_render channel
            CurrHideRender = CurrMdl.animation_data.action.fcurves[0].keyframe_points
            if CurrHideRender[1].co[0] > 1.0:
                ChgKeyframe = int(CurrHideRender[1].co[0])
                print("Ragdoll Animation found in "+CurrMdl.name)
                
                # Find Run Animation
                for CurrSecMdl in bpy.data.objects:
                    if CurrMdl.name.find("afx.") != -1:
                        if CurrSecMdl.name.find(CurrMdl.name.split()[1]) != -1 and not CurrMdl == CurrSecMdl: # Dont use the same object-model
                            
                            print(CurrSecMdl.name)
                            SecHideRender = CurrSecMdl.animation_data.action.fcurves[0].keyframe_points
                            print(len(SecHideRender))
                            if len(SecHideRender) >= ChgKeyframe:
                                

                                # Run Animation is shown on the second keyframe and hidden on the ChangingKeyframe
                                # print(SecHideRender[ChgKeyframe].co[0])
                                if SecHideRender[ChgKeyframe].co[1] == 1.0 and SecHideRender[ChgKeyframe-1].co[1] == 0.0:

                                    PlayerAnims.append([CurrSecMdl,CurrMdl]) #Add pair of animations to array
                                    
                                # VERY STUPID WAY TO FIX IK LEAVE ME ALONE
                                else:
                                    if SecHideRender[ChgKeyframe+1].co[1] == 1.0 and SecHideRender[ChgKeyframe].co[1] == 0.0:
                                        PlayerAnims.append([CurrSecMdl,CurrMdl]) #Add pair of animations to array

                                                                                    
    # Edit animation-strips
    for i in range(len(PlayerAnims)):
        print("Death Animation found in "+PlayerAnims[i][0].name+" and corresponding Run Animation found in "+ PlayerAnims[i][1].name+"\n")
        RagdollStart = PlayerAnims[i][1].animation_data.action.fcurves[1].range()[0] 
        PlayerAnims[i][1].keyframe_delete(data_path="hide_render", frame=0.0)
        RunDataAnim = PlayerAnims[i][0].animation_data.action
        RagdollDataAnim = PlayerAnims[i][1].animation_data.action
        
        # Push action down to new strip
        PlayerAnims[i][0].animation_data_clear()
        PlayerAnims[i][0].animation_data_create()
        ComplAnim = PlayerAnims[i][0].animation_data.nla_tracks.new()
        ComplAnim.strips.new(name="RunData", start=0.0, action=RunDataAnim)
        
        # RunAnim already jumps on the frame, where the first keyframe of RagdollAnim is
        ComplAnim.strips[RunDataAnim.name].action_frame_end = RagdollStart - 1
        ComplAnim.strips.new(name="RagdollDataAnim", start=RagdollStart, action=RagdollDataAnim)
        
        # Delete model
        for C in PlayerAnims[i][1].children:
            bpy.data.objects.remove(C)
        bpy.data.objects.remove(PlayerAnims[i][1])
        PlayerAnims[i][0].name = PlayerAnims[i][0].name + "RunAndDeathAnim"
        
    print("Merging Run and Death Animation finished\n")


class MergeAnims(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "myops.merge_anims"
    bl_label = "Merge Anims"


    def execute(self, context):
        main(context)
        return {'FINISHED'}

class AGRToolset_Menu(Menu):
    """Creates a Pie Menu for the toolset"""
    bl_idname = "AGRToolset_Menu"
    bl_label = "Merge Anims"


    def draw(self, context):
        
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("myops.merge_anims")
        pie.operator("export_scene.a2f")





class AGRTOFBX(bpy.types.Operator):
    """Exports AGR players with custom root to FBX format"""   # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "export_scene.a2f"        # unique identifier for buttons and menu items to reference.
    bl_label = "AGR (.fbx)"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}  # enable undo and setting presets for the operator.

    # Properties used by the file browser
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    global_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale everything by this value (0.01 old default, 0.0254 is more accurate)",
        min=0.000001, max=1000000.0,
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
        layout.operator("export_scene.a2f", text="AGR (.fbx)")

    # Open the filebrowser with the custom properties
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # main function
    def execute(self, context):
        # change filepath, if something is inputted in the File Name Box
        if not self.filepath.endswith("\\"):
            self.filepath = self.filepath.rsplit(sep="\\", maxsplit=1)[0] + "\\"

        # clean the collections

        # select and rename hierarchy objects to root
        for CurrentModel in bpy.data.objects:
            if CurrentModel.name.find("player") != -1:
                # select root
                CurrentModel.select_set(1)
                # select children
                for CurrentChildren in CurrentModel.children:
                    CurrentChildren.select_set(1)
                # rename top to player
                CurrentObjectName = CurrentModel.name
                OldName = CurrentModel.name 
                CurrentModel.name = self.root_name
                # export current object as fbx
                fullfiles = self.filepath + "/" + CurrentObjectName + ".fbx"
                if 'afxCam' in bpy.data.objects:
                    if self.custom_frame_range == True:
                        bpy.context.scene.frame_start = 0
                        bpy.context.scene.frame_end = bpy.data.objects["afxCam"].animation_data.action.frame_range[1]
                    else:
                        None
                bpy.ops.export_scene.fbx(
                    filepath = fullfiles,
                    use_selection = True,
                    global_scale=self.global_scale,
                    bake_anim_use_nla_strips = False,
                    bake_anim_use_all_actions = False,
                    bake_anim_simplify_factor = 0,
                    add_leaf_bones=False)
                CurrentModel.name = OldName
                # undo all changes
                bpy.ops.object.select_all(action='DESELECT')

        #export camera
        bpy.ops.object.select_all(action='DESELECT')
        if bpy.data.objects.find("afxCam") != -1:
            bpy.data.objects["afxCam"].select_set(1)
            if self.custom_frame_range == True:
                bpy.context.scene.frame_start = 0
                bpy.context.scene.frame_end = bpy.data.objects["afxCam"].animation_data.action.frame_range[1]
            else:
                None
            fullfiles_cam = self.filepath + "/afxcam.fbx"
            bpy.ops.export_scene.fbx(
                filepath = fullfiles_cam, 
                use_selection = True, 
                global_scale=self.global_scale,
                bake_anim_use_nla_strips = False, 
                bake_anim_use_all_actions = False, 
                bake_anim_simplify_factor = 0,
                add_leaf_bones=False)
            # undo all changes
            bpy.ops.object.select_all(action='DESELECT')

def register():
    bpy.utils.register_class(MergeAnims)
    bpy.utils.register_class(AGRToolset_Menu)
    bpy.utils.register_class(AGRTOFBX)
    bpy.types.TOPBAR_MT_file_export.append(AGRTOFBX.menu_draw_export)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi_mnu = km.keymap_items.new("wm.call_menu_pie", "COMMA", "PRESS", shift=True)
    kmi_mnu.properties.name = AGRToolset_Menu.bl_idname

def unregister():
    bpy.utils.unregister_class(MergeAnims)
    bpy.utils.unregister_class(AGRToolset_Menu)
    bpy.utils.unregister_class(AGRTOFBX)
    bpy.types.TOPBAR_MT_file_export.remove(AGRTOFBX.menu_draw_export)

if __name__ == "__main__":
    register()