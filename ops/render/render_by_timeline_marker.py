import bpy

from .storyboard import RenderStoryboard
from ...utils import get_sort_timeline_markers, get_scene_gp_all_frames


class RenderStoryboardByTimelineMarker(bpy.types.Operator, RenderStoryboard):
    bl_idname = "render.render_storyboard"
    bl_label = "Render Storyboard"
    # bl_description = "Ctrl: Directly render without previewing"

    markers_dict = {}

    def init_render_date(self):
        """
        [1, 10, 50, 60, 70, 80, 90, 150, 170, 190, 210, 250, 270, 280, 290, 320, 340, 350, 370, 390, 410, 430, 440, 450,
         480, 500, 520, 540, 560]
        [1, 10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 95, 100, 105, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200,
         210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 375, 380, 385, 390, 395,
         400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 565, 570, 575]"""
        markers_sort_list = sorted(self.markers_dict.keys())

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

    def start(self, context, event):
        self.markers_dict = {m.frame: m.name for m in get_sort_timeline_markers(context)}
        self.frames = get_scene_gp_all_frames(context)
        print("self.frames：", len(self.frames), "self.markers", len(self.markers_dict))
        self.init_render_date()
        print("self.render_data", self.render_data)
        if event.ctrl:
            return self.execute(context)
