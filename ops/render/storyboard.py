import os
import time

import bpy

from ...utils import get_pref


class RenderStoryboard:
    frames = []

    timer = None
    start_time = None

    render_data = {}  # {frame:out_name}
    data = {}  # store data for restore

    preview_count: bpy.props.IntProperty(name="Preview Count", default=10, min=2, max=666, soft_max=20)

    name_mode: bpy.props.EnumProperty(
        items=[
            ("REPLACE", "Replace", ""),
            ("SELECT_REPLACE", "Select Replace", ""),
        ]
    )
    enabled_folder: bpy.props.BoolProperty(default=True)
    enabled_scene: bpy.props.BoolProperty(default=True)
    enabled_view_layer: bpy.props.BoolProperty(default=True)
    enabled_frame: bpy.props.BoolProperty(default=True)
    enabled_frame_int: bpy.props.BoolProperty(default=True)
    enabled_file_suffix: bpy.props.BoolProperty(default=True)
    enabled_camera: bpy.props.BoolProperty(default=True)

    def start(self, context, event):
        ...

    def get_out_file_path(self, context: bpy.types.Context, frame: int):
        pref = get_pref()
        file_format = pref.output_file_format

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
                .replace("$FRAME", frame_str).replace("填充帧", frame_str)
                .replace("$FRAME_INT", str(frame)).replace("帧", str(frame))
                .replace("$FILE_SUFFIX", suffix).replace("后缀", suffix)
                .replace("$CAMERA", camera).replace("相机", camera)
                )

    def draw(self, context):
        pref = get_pref()

        column = self.layout.column(align=True)
        column.operator_context = "EXEC_DEFAULT"
        column.prop(self, "preview_count")

        column.row().prop(self, "name_mode", expand=True)

        box_column = column.box().column(align=True)

        box_column.label(text="Folder split by \\")
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

        box_column.label(text="Tips: Some attributes will only change during rendering")
        column.prop(pref, "output_file_format")
        for index, frame in enumerate(self.render_data.keys()):
            if index >= self.preview_count:
                break
            row = column.row(align=True)
            row.label(text=str(self.get_out_file_path(context, frame)))

    def invoke(self, context, event):
        self.frames = []
        self.start_time = time.time()
        self.start_data(context)
        self.render_data = {}
        if res := self.start(context, event):
            return res
        return context.window_manager.invoke_props_dialog(self, width=500)

    def execute(self, context):
        pref = get_pref()
        if not hasattr(self, "start_time"):
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
                    bpy.ops.render.opengl()
                    try:
                        if 'Render Result' in bpy.data.images:
                            bpy.data.images['Render Result'].save_render(self.get_out_file_path(context, frame_current))
                            self.render_data.pop(frame_current)
                    except RuntimeError:
                        text = bpy.app.translations.pgettext_iface("The file output path is incorrect, please check!!")
                        self.report({"ERROR"}, text + get_pref().output_file_format)
                        return {"CANCELLED"}
                else:
                    frame = list(self.render_data.keys())[0]
                    context.scene.frame_set(frame)
            else:
                self.stop(context)
                text = bpy.app.translations.pgettext_iface("Render complete")
                self.report({"INFO"}, f"{text} {time.time() - self.start_time}s")
                return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def stop(self, context):
        # Stop timer
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

        self.restore_date(context)

    def start_data(self, context):
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
