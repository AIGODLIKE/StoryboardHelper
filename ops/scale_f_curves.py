import bpy
from mathutils import Vector


def set_data(context):
    space = context.space_data
    space.pivot_point = "CURSOR"

    space.dopesheet.show_hidden = True
    space.dopesheet.show_only_errors = False
    scene = context.scene
    scene.tool_settings.use_snap_anim = True


class ScaleFCurvesStoryboard(bpy.types.Operator):
    bl_idname = "anim.scale_f_curves"
    bl_label = "缩放F曲线"
    bl_description = ""

    move_frame_start: bpy.props.BoolProperty(name="Move Frame Range", default=True)
    scale_frame_range: bpy.props.BoolProperty(name="Scale Frame Range", default=True)

    frame_move_to: bpy.props.IntProperty(name="Frame Move to", default=0)
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=1)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "scale_factor")
        row.prop(self, "scale_frame_range", icon="PREVIEW_RANGE", text="")

        box = layout.box()
        box.prop(self, "move_frame_start")
        if self.move_frame_start:
            box.prop(self, "frame_move_to")

    def invoke(self, context, event):
        bpy.ops.ed.undo_push(message="Push Undo")

        self.frame_move_to = context.scene.frame_start
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        set_data(context)

        ok_set = set()

        def set_action(f_curves: bpy.types.FCurve):
            f_curves.lock = False
            setattr(f_curves, "hide", False)
            ok_set.add(f_curves)
            if f_curves.group:
                for c in f_curves.group.channels:
                    if c not in ok_set:
                        set_action(c)

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

        bpy.ops.graph.reveal(select=False)  # 显示所有通道
        bpy.ops.graph.select_all(action="SELECT")
        bpy.ops.transform.resize("EXEC_DEFAULT", True,
                                 value=(self.scale_factor, 1, 1), orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=300,
                                 use_proportional_connected=False, use_proportional_projected=False, snap=True,
                                 snap_elements={'VERTEX'}, use_snap_project=False, snap_target='CLOSEST',
                                 use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True,
                                 use_snap_selectable=False
                                 )

        ok_set = set()

        def snap(c_f):
            if c_f not in ok_set:
                for index, keyframe in enumerate(c_f.keyframe_points):
                    x, y = keyframe.co_ui
                    keyframe.co_ui = Vector((int(x), y))

            ok_set.add(c_f)
            if c_f.group:
                for c in c_f.group.channels:
                    if c not in ok_set:
                        snap(c)
            c_f.update()

        for obj in context.scene.objects:
            anim = obj.animation_data
            if anim:
                action = obj.animation_data.action
                if action:
                    for f_c in action.fcurves:
                        snap(f_c)
                    if action.groups:
                        for g in action.groups:
                            g.lock = False
                            for f_c in g.channels:
                                snap(f_c)
                    action.update_tag()

        return {"FINISHED"}

    def move_frame(self, context):
        if self.move_frame_start:
            move = self.frame_move_to - scene.frame_start
            bpy.ops.transform.translate(value=(-124.993, -0, -0), orient_type='GLOBAL',
                                        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), )

            bpy.ops.transform.translate(
                value=(move, -0, -0), orient_matrix_type='GLOBAL',
                constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
                proportional_edit_falloff='SMOOTH', proportional_size=300,
                use_proportional_connected=False, use_proportional_projected=False, snap=True,
                snap_elements={'VERTEX'}, use_snap_project=False, snap_target='CLOSEST',
                use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True,
                use_snap_selectable=False
            )
            scene.frame_start += move
            scene.frame_end += move

    def scale_range(self, context):
        frame_range = scene.frame_end - scene.frame_start

        if self.scale_frame_range:
            scene.frame_end = int(scene.frame_start + frame_range * self.scale_factor)
