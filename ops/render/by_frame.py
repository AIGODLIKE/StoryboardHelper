from ...utils import get_fill_frame


class ByFrame:
    by_frame = {}


    def update_by_frame(self, context):
        scene = context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end
        self.by_frame = {i: get_fill_frame(context, i) for i in range(frame_start, frame_end)}
