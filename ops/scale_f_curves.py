import bpy
from mathutils import Vector


def for_all_action(context, func) -> int:
    count = 0
    ok_set = set()
    for obj in context.scene.objects:
        anim = obj.animation_data
        if anim:
            action = obj.animation_data.action
            if action:
                for f_c in action.fcurves:
                    func(f_c)
                    ok_set.add(f_c)
                    count += 1
                if action.groups:
                    for g in action.groups:
                        g.lock = False
                        for f_c in g.channels:
                            func(f_c)
                            ok_set.add(f_c)
                            count += 1
                action.update_tag()
    return count


def unlock(context):
    def set_action(f_curves: bpy.types.FCurve):
        f_curves.lock = False
        setattr(f_curves, "hide", False)

    for_all_action(context, set_action)


del_frame = 0


def snap_to_int_frame(context):
    global del_frame
    del_frame = 0

    def snap(c_f):
        global del_frame
        sort_frame = sorted(c_f.keyframe_points, key=lambda k: k.co_ui[0])
        snap_keyframe = set()
        fl = len(c_f.keyframe_points)
        for index, keyframe in enumerate(sort_frame):
            x, y = keyframe.co_ui
            ix = int(x)
            while True:
                if ix not in snap_keyframe:
                    keyframe.co_ui = Vector((ix, y))
                    snap_keyframe.add(ix)
                    break
                else:
                    ix += 1
        del_frame += fl - len(c_f.keyframe_points)
        c_f.update()

    for_all_action(context, snap)


class ScaleFCurvesStoryboard(bpy.types.Operator):
    bl_idname = "anim.scale_f_curves"
    bl_label = "缩放F曲线"
    bl_options = {"REGISTER", "UNDO"}

    is_designate: bpy.props.BoolProperty(name="Designate Scale Range", default=False)
    is_move_frame: bpy.props.BoolProperty(name="Move Frame Range", default=False)
    is_scale_frame_range: bpy.props.BoolProperty(name="Scale Frame Range", default=True)

    move_frame_to: bpy.props.IntProperty(name="Move Frame to", default=0)

    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=1)

    designate_start: bpy.props.IntProperty(name="Start", default=0)
    designate_end: bpy.props.IntProperty(name="End", default=0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "is_designate")
        row = layout.row(align=True)
        row.prop(self, "scale_factor")
        if self.is_designate:
            column = layout.column(align=True)
            column.prop(self, "designate_start")
            column.prop(self, "designate_end")
        else:
            row.prop(self, "is_scale_frame_range", icon="PREVIEW_RANGE", text="")

            box = layout.box()
            box.prop(self, "is_move_frame")
            if self.is_move_frame:
                box.prop(self, "move_frame_to")

    def invoke(self, context, event):
        # bpy.ops.ed.undo_push(message="Push Undo")
        self.set_data(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        unlock(context)
        if self.check(context):
            return {"CANCELLED"}

        self.scale_range(context)
        self.scale_frame(context)
        self.move_frame(context)
        snap_to_int_frame(context)
        self.report({"INFO"}, f"缩放完成 有{del_frame}帧被删除")
        return {"FINISHED"}

    def move_frame(self, context):
        if self.is_designate:
            return
        if self.is_move_frame:
            scene = context.scene
            move = self.move_frame_to - scene.frame_start
            bpy.ops.transform.translate(
                value=(move, -0, -0),
                # orient_matrix_type='GLOBAL',
                # constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
                # proportional_edit_falloff='SMOOTH', proportional_size=300,
                # use_proportional_connected=False, use_proportional_projected=False, snap=True,
                # snap_elements={'VERTEX'}, use_snap_project=False, snap_target='CLOSEST',
                # use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True,
                # use_snap_selectable=False
            )
            scene.frame_start += move
            scene.frame_end += move
            scene.frame_current += move

    def scale_range(self, context):
        if self.is_designate:
            return
        if self.is_scale_frame_range:
            scene = context.scene
            scene.frame_start = int(
                scene.frame_current + ((scene.frame_start - scene.frame_current) * self.scale_factor))
            scene.frame_end = int(scene.frame_current + ((scene.frame_end - scene.frame_current) * self.scale_factor))

    def scale_frame(self, context):
        bpy.ops.graph.reveal(select=False)  # 显示所有通道
        bpy.ops.graph.select_all(action="SELECT")
        if self.is_designate:
            self.select_designate_frame(context)
        bpy.ops.transform.resize("EXEC_DEFAULT", True,
                                 value=(self.scale_factor, 1, 1),
                                 # orient_type='GLOBAL',
                                 # orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 # constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
                                 # proportional_edit_falloff='SMOOTH', proportional_size=300,
                                 # use_proportional_connected=False, use_proportional_projected=False, snap=True,
                                 # snap_elements={'VERTEX'}, use_snap_project=False, snap_target='CLOSEST',
                                 # use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True,
                                 # use_snap_selectable=False
                                 )

    def select_designate_frame(self, context):
        """选择指定的帧"""

        def select_designate(fc: bpy.types.FCurve):
            start, end = self.designate_start, self.designate_end
            for index, keyframe in enumerate(fc.keyframe_points):
                x, y = keyframe.co_ui
                keyframe.select_control_point = start < x < end
                keyframe.select_left_handle = keyframe.select_right_handle = False

        for_all_action(context, select_designate)

    def set_data(self, context):
        space = context.space_data
        space.pivot_point = "CURSOR"

        space.dopesheet.show_hidden = True
        space.dopesheet.show_only_errors = False

        scene = context.scene
        # scene.tool_settings.use_snap_anim = True
        self.designate_start = scene.frame_start
        self.designate_end = scene.frame_end

    def check(self, context):
        if self.designate_start >= self.designate_end:
            self.report({"ERROR"}, "指定的帧范围出现错误")
            return True
