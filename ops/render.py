import bpy

from ..utils import get_sort_timeline_markers, get_scene_gp_all_frames


class Render(bpy.types.Operator):
    bl_idname = "anim.render_storyboard"
    bl_label = "Render Storyboard"

    timer = None
    markers = []
    frames = []

    render_data = {}  # {frame:out_name}

    def check_timeline_markers_not_match(self) -> bool:
        miss_list = []

        for mark in self.markers:
            if mark not in self.frames:
                miss_list.append(mark)
        is_error = len(miss_list) != 0

        if is_error:
            self.report({"ERROR"}, f"Timeline markers are not match f{miss_list}")

        return is_error

    def init_render_date(self):
        ml = len(self.markers)
        for index, mark in enumerate(self.markers):
            next_mark_frame = self.markers[index + 1] if index < ml else ml + 1

            frame = self.frames.pop(0)
            count = 0
            while frame < next_mark_frame:
                suffix = f"{count}".zfill(2)
                self.render_data[frame] = f"{mark}_{suffix}.jpg"
                count += 1

    def invoke(self, context, event):
        self.markers = get_sort_timeline_markers(context)
        self.frames = get_scene_gp_all_frames(context)

        if self.check_timeline_markers_not_match():
            return {"CANCELLED"}

        self.init_render_date()

        wm = context.window_manager
        self.timer = wm.event_timer_add(addon_prefs.delay, window=context.window)
        wm.modal_handler_add(self)
        return self.execute(context)

    def execute(self, context):
        return {"FINISHED"}


bpy.ops.screen.screenshot(filepath=context.scene.render.frame_path(frame=f_curr))
