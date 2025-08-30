import bpy

from ...utils import get_fill_frame, get_all_gp_frames, get_frames


class ByFrame:
    all_frames = {}
    gp_frames = {}
    an_frames = {}

    by_frame_enum = [
        ("ALL", "Start frame..End frame", ""),
        ("GP", "Only GP Frame", ""),
        ("AN", "Only Animation Frame", ""),
    ]
    by_frame_mode: bpy.props.EnumProperty(items=by_frame_enum, default="ALL", )

    def update_by_frame(self, context):
        scene = context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end
        self.all_frames = {i: get_fill_frame(context, i) for i in range(frame_start, frame_end)}
        self.gp_frames = {i: get_fill_frame(context, i) for i in get_all_gp_frames(context)}
        self.an_frames = {i: get_fill_frame(context, i) for i in get_frames(context)}

    def draw_by_frame(self, context, layout):
        layout.separator()
        layout.row().prop(self, "by_frame_mode", expand=True)
