import bpy

from ...utils import get_sort_timeline_markers, get_scene_gp_all_frames, get_pref
from .storyboard import RenderStoryboard

class RenderStoryboardByTimelineMarker(bpy.types.Operator,RenderStoryboard):
    bl_idname = "render.render_storyboard_by_timeline_marker"
    bl_label = "Render Storyboard"
    bl_description = "Ctrl: Directly render without previewing"

    markers_dict = {}

    enabled_nb_tm_format: bpy.props.BoolProperty(default=True)

    def get_out_file_path(self, context: bpy.types.Context, frame: int):
        file_format = super().output_file_format
        if self.enabled_nb_tm_format is False:
            file_format = file_format.replace("$NB_TM_FORMAT", "").replace("格式", "")
        nb = self.render_data[frame]
        return file_format.replace("$NB_TM_FORMAT", nb).replace("格式", nb)

    def check_timeline_markers_not_match(self) -> bool:
        miss_list = []
        print("check_timeline_markers_not_match", self.markers_dict)

        if len(self.markers_dict) == 0:
            self.report({"ERROR"}, "Time stamp not found")
            return True
        elif len(self.frames) == 0:
            self.report({"ERROR"}, "No frames found for rendering")
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

        if self.check_timeline_markers_not_match():
            self.restore_date(context)
            return {"CANCELLED"}
        print("self.frames：", len(self.frames), "self.markers", len(self.markers_dict))
        self.init_render_date()
        print("self.render_data", self.render_data)
        if event.ctrl:
            return self.execute(context)

