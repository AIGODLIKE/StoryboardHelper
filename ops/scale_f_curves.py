import bpy


class ScaleFCurvesStoryboard(bpy.types.Operator):
    bl_idname = "anim.scale_f_curves"
    bl_label = "缩放F曲线"
    bl_description = ""

    move_frame_start: bpy.props.BoolProperty(name="Move Frame Range", default=True)
    frame_move_to: bpy.props.IntProperty(name="Frame Move to", default=0)
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

        self.frame_move_to = context.scene.frame_start
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        space = context.space_data
        space.pivot_point = "CURSOR"

        space.dopesheet.show_only_selected = self.mode == "ONLY_SELECTED"
        space.dopesheet.show_hidden = True
        space.dopesheet.show_only_errors = False

        scene = context.scene
        scene.tool_settings.use_snap_anim = False
        scene.frame_current = scene.frame_start
        frame_range = scene.frame_start - scene.frame_end

        if self.scale_frame_range:
            scene.frame_end = int(scene.frame_start + frame_range * self.scale_factor)
        bpy.ops.graph.select_all(action="SELECT")
        bpy.ops.transform.resize("EXEC_DEFAULT", True,
                                 value=(self.scale_factor, 1, 1),
                                 orient_type='GLOBAL',
                                 proportional_edit_falloff='SMOOTH',
                                 )
        if self.move_frame_start:
            move = self.frame_move_to - self.scene.frame_start

            scene.frame_start += move
            scene.frame_end += move
            
            bpy.ops.transform.translate(
                value=(move, -0, -0),
                orient_type='GLOBAL',
                proportional_edit_falloff='SMOOTH',
            )

        return {"FINISHED"}
