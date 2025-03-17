from functools import cache

import bpy
from mathutils import Vector


def set_space_data(context):
    space = context.space_data

    space.dopesheet.show_hidden = True
    space.dopesheet.show_only_errors = False


class ScaleFCurvesStoryboard(bpy.types.Operator):
    bl_idname = "anim.scale_f_curves"
    bl_label = "缩放F曲线"
    bl_description = ""
    # bl_operators = {"REGISTER", "UNDO"}

    is_move_frame_start: bpy.props.BoolProperty(name="Move Frame Range", default=True)
    is_scale_frame_range: bpy.props.BoolProperty(name="Scale Frame Range", default=True)

    move_frame_start_to: bpy.props.IntProperty(name="Frame Move to", default=0)
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=1)

    scale_content: bpy.props.EnumProperty(name="Scale Content", items=[
        ("ALL", "All", ""),
        ("ONLY_SELECTED", "Only Selected", ""),
    ])
    scale_range_type: bpy.props.EnumProperty(name="Scale Range Type",
                                             items=[
                                                 ("BY_SCENE_FRAME", "BY Scene Frame Range", ""),
                                                 ("DESIGNATE_SCALE_RANGE", "Designate Scale Range", ""),
                                             ]
                                             )
    scale_axis_frame: bpy.props.IntProperty(name="Scale Axis Frame", default=0)
    designate_scale_start: bpy.props.IntProperty(name="Start", default=0)
    designate_scale_end: bpy.props.IntProperty(name="End", default=0)

    @property
    def is_designate(self) -> bool:
        return self.scale_range_type == "DESIGNATE_SCALE_RANGE"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="Scale Content")
        row.prop(self, "scale_content", expand=True)

        row = layout.row(align=True)
        row.label(text="Scale Range")
        row.prop(self, "scale_range_type", expand=True)
        layout.prop(self, "scale_axis_frame")

        if self.is_designate:
            layout.prop(self, "designate_scale_start")
            layout.prop(self, "designate_scale_end")
        else:
            row = layout.row(align=True)
            row.prop(self, "scale_factor")
            row.prop(self, "is_scale_frame_range", icon="PREVIEW_RANGE", text="")

            layout.prop(self, "is_move_frame_start")
            if self.is_move_frame_start:
                layout.prop(self, "move_frame_start_to")

    def scale_frame_range(self, context):
        """缩放帧区 只有在设置成场景帧时缩放"""
        if self.scale_frame_range and not self.is_designate:
            scene = context.scene
            frame_range = scene.frame_end - scene.frame_start
            scene.frame_end = int(scene.frame_start + frame_range * self.scale_factor)

    def move_frame_start(self, context):
        if self.is_move_frame_start and not self.is_designate:
            scene = context.scene
            move = self.move_frame_start_to - scene.frame_start
            scene.frame_start += move
            scene.frame_end += move

    def invoke(self, context, event):
        bpy.ops.ed.undo_push(message="Push Undo")

        scene = context.scene
        self.scale_axis_frame = scene.frame_current
        self.move_frame_start_to = scene.frame_start
        self.designate_scale_start = scene.frame_start
        self.designate_scale_end = scene.frame_end

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        set_space_data(context)

        # self.scale_frame_range(context)
        # self.move_frame_start(context)
        ok_set = set()
        scene = context.scene

        @cache
        def calculation_frame(frame: float) -> int:
            return int(self.scale_axis_frame + ((frame - self.scale_axis_frame) * self.scale_factor))

        calculation_frame.cache_clear()
        count = 0

        def set_action(f_curves: bpy.types.FCurve):
            # f_curves.lock = False
            # setattr(f_curves, "hide", False)
            ok_set.add(f_curves)

            # 通过计算偏移值并设置为整数
            kl = len(f_curves.keyframe_points) - 1
            c = 0
            for index, keyframe in enumerate(f_curves.keyframe_points):
                ox, oy = keyframe.co_ui
                x = calculation_frame(ox)

                next_kf = f_curves.keyframe_points[index + 1] if index != kl else None

                if next_kf:
                    next_f = calculation_frame(next_kf.co_ui[0])
                    if (ox - next_kf.co_ui[0]) < 0.5 and x == next_f:  # 如果缩放之后两个帧给缩到一个帧内了
                        x -= 1  # 就将帧向前移一个,避免缩放产生的重叠
                        print("就将帧向前移一个,避免缩放产生的重叠", next_kf, next_f, x)

                if self.is_designate:  # 手动设置范围
                    if ox > self.designate_scale_end:
                        continue
                    elif ox < self.designate_scale_start:
                        continue

                c += 1
                keyframe.co_ui = Vector((x, oy))

            # if f_curves.group:
            #     for c in f_curves.group.channels:
            #         if c not in ok_set:
            #             set_action(c)
            f_curves.update()
            # f_curves.update_autoflags()
            return c

        objects = context.scene.objects if self.scale_content == "ALL" else context.selected_objects
        for obj in objects:
            anim = obj.animation_data
            if anim:
                action = obj.animation_data.action
                if action:
                    for f_c in action.fcurves:
                        count += set_action(f_c)
                    if action.groups:
                        for g in action.groups:
                            g.lock = False
                            for f_c in g.channels:
                                count += set_action(f_c)

        self.report({"INFO"}, f"共修改了 {count}个关键帧")
        return {"FINISHED"}
