import os
import time

import bpy

from ..utils import get_sort_timeline_markers, get_scene_gp_all_frames, get_pref


class RenderStoryboard(bpy.types.Operator):
    bl_idname = "render.render_storyboard"
    bl_label = "Render Storyboard"
    bl_description = "Ctrl: Directly render without previewing"

    timer = None
    start_time = None

    markers_dict = {}
    frames = []

    render_data = {}  # {frame:out_name}
    data = {}  # store data for restore

    preview_count: bpy.props.IntProperty(name="Preview Count", default=10, min=2, max=666, soft_max=20)

    name_mode: bpy.props.EnumProperty(
        items=[
            ("REPLACE", "替换", ""),
            ("SELECT_REPLACE", "选择替换", ""),
        ]
    )
    enabled_folder: bpy.props.BoolProperty(default=True)
    enabled_scene: bpy.props.BoolProperty(default=True)
    enabled_view_layer: bpy.props.BoolProperty(default=True)
    enabled_nb_tm_format: bpy.props.BoolProperty(default=True)
    enabled_frame: bpy.props.BoolProperty(default=True)
    enabled_frame_int: bpy.props.BoolProperty(default=True)
    enabled_file_suffix: bpy.props.BoolProperty(default=True)
    enabled_camera: bpy.props.BoolProperty(default=True)

    def check_timeline_markers_not_match(self) -> bool:
        miss_list = []

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
        # print("markers_sort_list", markers_sort_list)

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

    def draw(self, context):
        pref = get_pref()

        column = self.layout.column(align=True)
        column.operator_context = "EXEC_DEFAULT"
        column.prop(self, "preview_count")

        column.row().prop(self, "name_mode", expand=True)

        box_column = column.box().column(align=True)

        box_column.label(text="文件夹需要以\\拆分")
        for text, prop in {
            "文件夹 -> $FOLDER -> 渲染输出的文件夹": "enabled_folder",
            "场景 -> $SCENE -> 场景名称": "enabled_scene",
            "视图层 -> $VIEW_LAYER -> 视图层名称": "enabled_view_layer",
            "格式 -> $NB_TM_FORMAT -> F_560_01，F_560_02": "enabled_nb_tm_format",
            "帧 -> $FRAME_INT -> 帧数 1,2": "enabled_frame",
            "填充帧 -> $FRAME -> 填充0 0001,0002": "enabled_frame_int",
            "后缀 -> $FILE_SUFFIX -> 输出文件后缀": "enabled_file_suffix",
            "相机 -> $CAMERA -> 当前相机名称": "enabled_camera",
        }.items():
            row = box_column.row(align=True)
            row.label(text=text)
            if self.name_mode == "SELECT_REPLACE":
                row.prop(self, prop, text="")

        box_column.label(text="Tips: 部分属性在渲染时才会改变")
        column.prop(pref, "output_file_format")
        for index, frame in enumerate(self.render_data.keys()):
            if index >= self.preview_count:
                break

            row = column.row(align=True)
            # row.label(text=str(index))
            row.label(text=str(self.get_out_file_path(context, frame)))

    def invoke(self, context, event):
        self.save_data(context)

        self.render_data = {}
        self.markers_dict = {m.frame: m.name for m in get_sort_timeline_markers(context)}
        self.frames = get_scene_gp_all_frames(context)
        self.start_time = time.time()

        if self.check_timeline_markers_not_match():
            self.restore_date(context)
            return {"CANCELLED"}
        # print([m.frame for m in self.markers][:])
        # print("frames", self.frames)
        print("self.frames：", len(self.frames), "self.markers", len(self.markers_dict))
        self.init_render_date()
        print("self.render_data", self.render_data)
        if event.ctrl:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=500)

    def execute(self, context):
        pref = get_pref()
        if hasattr(self, "start_time") is False:
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
                    # bpy.ops.screen.screenshot(filepath=out_path)
                    bpy.ops.render.opengl()
                    try:
                        if 'Render Result' in bpy.data.images:
                            bpy.data.images['Render Result'].save_render(self.get_out_file_path(context, frame_current))
                            self.render_data.pop(frame_current)
                    except RuntimeError:
                        self.report({"ERROR"}, "文件输出路径错误,请检查！！" + get_pref().output_file_format)
                        return {"CANCELLED"}
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

    def get_out_file_path(self, context: bpy.types.Context, frame: int):
        pref = get_pref()
        file_format = pref.output_file_format

        nb = self.render_data[frame]
        # frame_name = f"{frame_current}".zfill(4)
        out_path = context.scene.render.frame_path(frame=frame)
        folder = os.path.dirname(out_path)

        frame_str, suffix = os.path.basename(out_path).split(".")

        view_layer = context.view_layer.name
        scene = context.scene
        camera = context.scene.camera.name

        if self.name_mode == "SELECT_REPLACE":
            if self.enabled_folder is False:
                file_format = file_format.replace("$FOLDER", "").replace("文件夹", "")
            if self.enabled_scene is False:
                file_format = file_format.replace("$SCENE", "").replace("场景", "")
            if self.enabled_view_layer is False:
                file_format = file_format.replace("$VIEW_LAYER", "").replace("视图层", "")
            if self.enabled_nb_tm_format is False:
                file_format = file_format.replace("$NB_TM_FORMAT", "").replace("格式", "")
            if self.enabled_frame is False:
                file_format = file_format.replace("$FRAME", "").replace("填充帧", "")
            if self.enabled_frame_int is False:
                file_format = file_format.replace("$FRAME_INT", str("")).replace("帧", "")
            if self.enabled_file_suffix is False:
                file_format = file_format.replace("$FILE_SUFFIX", "").replace("后缀", "")
            if self.enabled_camera is False:
                file_format = file_format.replace("$CAMERA", "").replace("相机", "")

        return (file_format
                .replace("$FOLDER", folder).replace("文件夹", folder)
                .replace("$SCENE", scene.name).replace("场景", scene.name)
                .replace("$VIEW_LAYER", view_layer).replace("视图层", view_layer)
                .replace("$NB_TM_FORMAT", nb).replace("格式", nb)
                .replace("$FRAME", frame_str).replace("填充帧", frame_str)
                .replace("$FRAME_INT", str(frame)).replace("帧", str(frame))
                .replace("$FILE_SUFFIX", suffix).replace("后缀", suffix)
                .replace("$CAMERA", camera).replace("相机", camera)
                )
