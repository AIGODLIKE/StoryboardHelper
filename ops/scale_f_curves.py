import bpy


class ScaleFCurvesStoryboard(bpy.types.Operator):
    bl_idname = "anim.scale_f_curves"
    bl_label = "缩放F曲线"
    bl_description = ""

    move_frame_start: bpy.props.BoolProperty(name="Move Frame Range", default=True)
    frame_start: bpy.props.IntProperty(name="Frame Start", default=0)
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=1)
    scale_frame_range: bpy.props.BoolProperty(name="Scale Frame Range")
    mode: bpy.props.EnumProperty(name="Mode", items=[
        ("ALL", "All", ""),
        ("ONLY_SELECTED", "Only Selected", ""),
    ])

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="Mode")
        row.prop(self, "mode", expand=True)
        layout.prop(self, "scale_factor")
        row = layout.row(align=True)
        row.prop(self, "scale_frame_range")
        row.prop(self, "move_frame_start")
        if self.move_frame_start:
            layout.prop(self, "frame_start")

    def invoke(self, context, event):
        bpy.ops.ed.undo_push(message="Push Undo")

        self.frame_start = context.scene.frame_start
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        context.space_data.pivot_point = "CURSOR"
        context.scene.frame_current = context.scene.frame_start

        bpy.ops.graph.select_all(action="SELECT")
        bpy.ops.transform.resize("EXEC_DEFAULT", True,
                                 value=(self.scale_factor, 1, 1), orient_type='GLOBAL',
                                 proportional_edit_falloff='SMOOTH',
                                 )
        # bpy.ops.transform.translate(value=(161.701, 14.9488, 0), orient_type='GLOBAL',
        #                             orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
        #                             mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
        #                             proportional_size=300, use_proportional_connected=False,
        #                             use_proportional_projected=False, snap=True, snap_elements={'VERTEX'},
        #                             use_snap_project=False, snap_target='CLOSEST', use_snap_self=True,
        #                             use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
        # bpy.ops.transform.translate(value=(-395.361, -0, -0), orient_type='GLOBAL',
        #                             orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
        #                             constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
        #                             proportional_edit_falloff='SMOOTH', proportional_size=300,
        #                             use_proportional_connected=False, use_proportional_projected=False, snap=True,
        #                             snap_elements={'VERTEX'}, use_snap_project=False, snap_target='CLOSEST',
        #                             use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True,
        #                             use_snap_selectable=False)

        return {"FINISHED"}
