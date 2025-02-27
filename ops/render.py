import time

import bpy

from ..utils import get_sort_timeline_markers, get_scene_gp_all_frames, get_pref


class RenderStoryboard(bpy.types.Operator):
    bl_idname = "render.render_storyboard"
    bl_label = "Render Storyboard"

    timer = None
    start_time = None

    markers_dict = {}
    frames = []

    render_data = {}  # {frame:out_name}
    data = {}  # store data for restore

    def check_timeline_markers_not_match(self) -> bool:
        miss_list = []

        if len(self.markers_dict) == 0:
            self.report({"ERROR"}, "未找到时间戳")
            return True
        elif len(self.frames) == 0:
            self.report({"ERROR"}, "未找到需要渲染的帧")
            return True

        for mark_frame in self.markers_dict.keys():
            if mark_frame not in self.frames:
                miss_list.append(self.markers_dict[mark_frame])
        is_error = len(miss_list) != 0

        if is_error:
            text = bpy.app.translations.pgettext("Timeline markers are not match %s") % miss_list
            self.report({"ERROR"}, text)

        return is_error

    def init_render_date(self):
        """
        [1, 10, 50, 60, 70, 80, 90, 150, 170, 190, 210, 250, 270, 280, 290, 320, 340, 350, 370, 390, 410, 430, 440, 450,
         480, 500, 520, 540, 560]
        [1, 10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 95, 100, 105, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200,
         210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 375, 380, 385, 390, 395,
         400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 565, 570, 575]"""
        markers_sort_list = sorted(self.markers_dict.keys())
        print("markers_sort_list", markers_sort_list)

        zfill_count = 2

        if len(markers_sort_list) == 1:
            mark_name = self.markers_dict[markers_sort_list[0]]
            for index, frame in self.frames:
                suffix = f"{index + 1}".zfill(zfill_count)
                self.render_data[frame] = f"{mark_name}_{suffix}"

        a_m_f = markers_sort_list.pop(0)
        b_m_f = markers_sort_list.pop(0)
        while True:
            count = 1
            while self.frames:
                frame = self.frames[0]

                marker_name = self.markers_dict[a_m_f]

                suffix = f"{count}".zfill(zfill_count)
                out_name = f"{marker_name}_{suffix}"

                if frame == a_m_f:  # 是当前时间戳
                    self.render_data[frame] = out_name
                    self.frames.pop(0)
                    count += 1
                elif b_m_f and frame == b_m_f:
                    a_m_f = b_m_f
                    b_m_f = markers_sort_list.pop(0) if markers_sort_list else None
                    break
                else:  # 界于两个时间戳之间
                    self.render_data[frame] = out_name
                    self.frames.pop(0)
                    count += 1
            if not self.frames:
                return

    def execute(self, context):
        pref = get_pref()

        self.save_data(context)

        self.render_data = {}
        self.markers_dict = {m.frame: m.name for m in get_sort_timeline_markers(context)}
        self.frames = get_scene_gp_all_frames(context)
        self.start_time = time.time()

        if self.check_timeline_markers_not_match():
            self.restore_date(context)
            return {"CANCELLED"}
        # print([m.frame for m in self.markers][:])
        print("frames", self.frames)
        print("self.frames：", len(self.frames), "self.markers", len(self.markers_dict))
        self.init_render_date()
        print("self.render_data", self.render_data)

        return {"CANCELLED"}

        wm = context.window_manager
        self.timer = wm.event_timer_add(pref.delay, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.stop(context)
            self.report({"INFO"}, f"取消渲染")
            return {"CANCELLED"}

        if event.type == "TIMER":
            scene = context.scene
            frame_current = scene.frame_current

            if self.render_data:
                if frame_current in self.render_data:
                    name = self.render_data.pop(frame_current)
                    frame_name = f"{frame_current}".zfill(4)
                    out_path = context.scene.render.frame_path(frame=frame_current).replace(f"{frame_name}", name)
                    print(name, "out_path", out_path)
                    # bpy.ops.screen.screenshot(filepath=out_path)
                    bpy.ops.render.opengl()
                    if 'Render Result' in bpy.data.images:
                        bpy.data.images['Render Result'].save_render(out_path)
                else:
                    frame = list(self.render_data.keys())[0]
                    context.scene.frame_set(frame)
            else:
                self.stop(context)
                self.report({"INFO"}, f"Render complete {time.time() - self.start_time}s")
                return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def stop(self, context):
        # Stop timer
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

        self.restore_date(context)

    def save_data(self, context):
        self.data = {
            "frame": context.scene.frame_current,
            "file_path": context.scene.render.filepath,
            "show_overlays": context.space_data.overlay.show_overlays
        }
        context.space_data.overlay.show_overlays = False

    def restore_date(self, context):
        context.scene.frame_set(self.data["frame"])
        context.space_data.overlay.show_overlays = self.data["show_overlays"]
        context.scene.render.filepath = self.data["file_path"]
