import bpy

from ...utils import get_fill_frame, get_frames_by_f_curves, get_gp_frames_by_layers


class ByFrame:
    all_frames = {}
    gp_frames = {}
    an_frames = {}

    by_frame_enum = [
        ("ALL", "Start frame..End frame", ""),
        ("GP", "Only GP Frame", ""),
        ("AN", "Only Animation Frame", ""),
        ("CUSTOM", "Custom Frame", ""),
    ]
    by_frame_mode: bpy.props.EnumProperty(items=by_frame_enum, default="ALL", )
    custom_frame: bpy.props.StringProperty(name="Custom Frame", default="1,5..8,10")

    @property
    def parse_custom_frame(self) -> "(bool,dict)":
        frames = []
        is_ok = False
        for i in self.custom_frame.split(","):
            try:
                if ".." in i:
                    a, b = i.split("..")
                    ia, ib = int(a), int(b) + 1
                    for j in range(ia, ib):
                        frames.append(j)
                else:
                    frames.append(int(i))
            except ValueError:
                pass
        frames = sorted(set(frames))
        return is_ok, {i: get_fill_frame(bpy.context, i) for i in frames}

    def update_by_frame(self, context):
        scene = context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        gp_frame_by_layers = get_gp_frames_by_layers(context)
        gp_frames_by_f_curves = get_frames_by_f_curves(context)
        gp_frames = sorted(set(gp_frame_by_layers + gp_frames_by_f_curves))

        self.all_frames = {i: get_fill_frame(context, i) for i in range(frame_start, frame_end)}
        self.gp_frames = {i: get_fill_frame(context, i) for i in gp_frames}
        self.an_frames = {i: get_fill_frame(context, i) for i in get_frames_by_f_curves(context)}

    def draw_by_frame(self, context, layout):
        layout.separator()
        layout.row().prop(self, "by_frame_mode", expand=True)
        if self.by_frame_mode == "CUSTOM":
            layout.separator()
            layout.prop(self, "custom_frame")
            layout.label(text="5..8 : 5,6,7,8 Frame")
