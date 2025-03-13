import bpy


class ScaleFCurvesStoryboard(bpy.types.Operator):
    bl_idname = "anim.scale_f_curves"
    bl_label = "缩放F曲线"
    bl_description = ""

    move_frame_start: bpy.props.BoolProperty(name="Move Frame Range", default=True)
    scale_frame_range: bpy.props.BoolProperty(name="Scale Frame Range", default=True)

    frame_move_to: bpy.props.IntProperty(name="Frame Move to", default=0)
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=1)

    mode: bpy.props.EnumProperty(name="Mode", items=[
        ("ALL", "All", ""),
        ("ONLY_SELECTED", "Only Selected", ""),
    ])

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="Mode")
        row.prop(self, "mode", expand=True)
        row = layout.row(align=True)
        row.prop(self, "scale_factor")
        row.prop(self, "scale_frame_range", icon="PREVIEW_RANGE", text="")

        layout.prop(self, "move_frame_start")
        if self.move_frame_start:
            layout.prop(self, "frame_move_to")

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
        frame_range = scene.frame_end - scene.frame_start

        if self.scale_frame_range:
            scene.frame_end = int(scene.frame_start + frame_range * self.scale_factor)

        ok_set = set()

        def set_action(f_curves: bpy.types.FCurve):
            f_curves.lock = False
            setattr(f_curves, "hide", False)
            ok_set.add(f_curves)
            if f_curves.group:
                for c in f_curves.group.channels:
                    if c not in ok_set:
                        set_action(c)

        # bpy.context.object.animation_data.action.fcurves[0].lock
        # bpy.context.object.animation_data.action.fcurves[0].group.channels[0].group hide
        for obj in context.scene.objects:
            anim = obj.animation_data
            if anim:
                action = obj.animation_data.action
                if action:
                    for f_c in action.fcurves:
                        set_action(f_c)
                    if action.groups:
                        for g in action.groups:
                            g.lock = False
                            for f_c in g.channels:
                                set_action(f_c)

        bpy.ops.graph.select_all(action="SELECT")
        bpy.ops.transform.resize("EXEC_DEFAULT", True,
                                 value=(self.scale_factor, 1, 1),
                                 orient_type='GLOBAL',
                                 proportional_edit_falloff='SMOOTH',
                                 )
        if self.move_frame_start:
            move = self.frame_move_to - scene.frame_start

            bpy.ops.transform.translate(
                value=(move, -0, -0),
                orient_type='GLOBAL',
                proportional_edit_falloff='SMOOTH',
            )
            print("move", move)
            scene.frame_start += move
            scene.frame_end += move

        scene.frame_current = scene.frame_start
        return {"FINISHED"}
