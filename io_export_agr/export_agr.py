import bpy, time, os

def MergeAnims(self, context):
    PlayerAnims = [] # Each type of model gets its own array inside this array

    # Find first Ragdoll and then Run Animation
    for CurrMdl in bpy.data.objects:
        # Find Player Models (which are named tm or ctm)
        if (CurrMdl.name.find("afx.") != -1 and CurrMdl.name.find("tm_") != -1):
            
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
                                elif SecHideRender[ChgKeyframe+1].co[1] == 1.0 and SecHideRender[ChgKeyframe].co[1] == 0.0:
                                    PlayerAnims.append([CurrSecMdl,CurrMdl]) #Add pair of animations to array
                                else:
                                    if SecHideRender[ChgKeyframe-1].co[1] == 1.0 and SecHideRender[ChgKeyframe].co[1] == 0.0:
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
    return {'FINISHED'}

#class AgrtoFbx(bpy.types.Operator):
def AgrtoFbx(self, context):

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