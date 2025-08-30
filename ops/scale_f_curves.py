import bpy
from mathutils import Vector

from ..utils import for_all_action


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
    bl_label = "Scale F Curves"
    bl_options = {"REGISTER", "UNDO"}

    is_designate: bpy.props.BoolProperty(name="Designate Scale Range", default=False)
    is_move_frame: bpy.props.BoolProperty(name="Move Frame Range", default=False)
    is_scale_frame_range: bpy.props.BoolProperty(name="Scale Frame Range", default=True)

    move_frame_to: bpy.props.IntProperty(name="Move Frame to", default=0)

    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=1)

    designate_start: bpy.props.IntProperty(name="Start", default=0)
    designate_end: bpy.props.IntProperty(name="End", default=0)

    @classmethod
    def poll(cls, context):
        area = context.area
        if area and area.type == "GRAPH_EDITOR" and area.ui_type == "FCURVES":
            if getattr(context, "active_editable_fcurve", None):
                return True
            if getattr(context, "selected_editable_fcurves", None):
                return True
            if getattr(context, "editable_fcurves", None):
                return True
        return False

    def draw(self, context):
        from bl_ui.space_dopesheet import dopesheet_filter

        layout = self.layout

        row = layout.row(align=True)
        dopesheet_filter(row, context)
        row.separator()
        row.prop(self, "is_designate")

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
        bpy.ops.graph.reveal(select=False)  # 显示所有通道
        unlock(context)
        self.set_data(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        if self.check(context):
            return {"CANCELLED"}

        self.scale_range(context)
        self.scale_frame(context)
        self.move_frame(context)
        snap_to_int_frame(context)
        self.report({"INFO"}, "Scaling completed with %s frames deleted" % del_frame)
        return {"FINISHED"}

    def move_frame(self, context):
        if self.is_designate:
            return
        if self.is_move_frame:
            scene = context.scene
            move = self.move_frame_to - scene.frame_start
            bpy.ops.transform.translate(value=(move, -0, -0))
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
        bpy.ops.transform.resize("EXEC_DEFAULT", True, value=(self.scale_factor, 1, 1))

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
            self.report({"ERROR"}, "There is an error in the specified frame range")
            return True
        return False
