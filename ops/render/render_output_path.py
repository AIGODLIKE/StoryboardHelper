import os

import bpy

from ...utils import get_pref, is_zh


class RenderOutputPath:
    enabled_folder: bpy.props.BoolProperty(default=True)
    enabled_scene: bpy.props.BoolProperty(default=True)
    enabled_view_layer: bpy.props.BoolProperty(default=True)
    enabled_frame: bpy.props.BoolProperty(default=True)
    enabled_frame_int: bpy.props.BoolProperty(default=True)
    enabled_file_suffix: bpy.props.BoolProperty(default=True)
    enabled_camera: bpy.props.BoolProperty(default=True)
    enabled_nb_tm_format: bpy.props.BoolProperty(default=True)
    expand_path: bpy.props.BoolProperty(default=True)

    def get_out_file_path(self, context: bpy.types.Context, frame: int):
        pref = get_pref()
        file_format = pref.output_file_format

        out_path = context.scene.render.frame_path(frame=frame)
        folder = os.path.dirname(out_path)

        frame_str, suffix = os.path.basename(out_path).split(".")

        view_layer = context.view_layer.name
        scene = context.scene
        camera = context.scene.camera.name

        if getattr(self, "name_mode", None) == "SELECT_REPLACE":
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

            if self.enabled_nb_tm_format is False:
                file_format = file_format.replace("$NB_TM_FORMAT", "").replace("格式", "")
        nb = getattr(self, "render_data", None)[frame]
        return (file_format
                .replace("$FOLDER", folder).replace("文件夹", folder)
                .replace("$SCENE", scene.name).replace("场景", scene.name)
                .replace("$VIEW_LAYER", view_layer).replace("视图层", view_layer)
                .replace("$FRAME", frame_str).replace("填充帧", frame_str)
                .replace("$FRAME_INT", str(frame)).replace("帧", str(frame))
                .replace("$FILE_SUFFIX", suffix).replace("后缀", suffix)
                .replace("$CAMERA", camera).replace("相机", camera)
                .replace("$NB_TM_FORMAT", nb).replace("格式", nb)
                )

    def draw_output_path(self, context, layout: bpy.types.UILayout):
        pref = get_pref()
        file_format = pref.output_file_format

        frame = context.scene.frame_current
        out_path = context.scene.render.frame_path(frame=frame)
        folder = os.path.dirname(out_path)

        frame_str, suffix = os.path.basename(out_path).split(".")

        view_layer = context.view_layer.name
        scene = context.scene
        camera = context.scene.camera.name

        column = layout.column(align=True)
        column.prop(self, "expand_path", text="Folder split by \\" if self.expand_path else "Path")
        column = layout.column(align=True)

        for a, b, text, prop, value in [
            ("文件夹", "$FOLDER", "Folder for rendering output", "enabled_folder", folder),
            ("场景", "$SCENE", "Scene name", "enabled_scene", scene.name),
            ("视图层", "$VIEW_LAYER", "View layer name", "enabled_view_layer", view_layer),
            ("格式", "$NB_TM_FORMAT", "F_560_01，F_560_02", "enabled_nb_tm_format", "F_560_02"),
            ("帧", "$FRAME_INT", "Frame int 1,2", "enabled_frame", str(frame)),
            ("填充帧", "$FRAME", "Fill 1 -> 0001,2 -> 0002", "enabled_frame_int", frame_str),
            ("后缀", "$FILE_SUFFIX", "Output file suffix", "enabled_file_suffix", suffix),
            ("相机", "$CAMERA", "Current camera name", "enabled_camera", camera),
        ]:
            row = column.row(align=True)
            row.label(text=text)
            if is_zh() and context.preferences.view.use_translate_interface:
                row.label(text=a)
                row.separator()
            row.label(text=b)
            row.label(text=value)
            if getattr(self, "name_mode", None) == "SELECT_REPLACE":
                row.prop(self, prop, text="")

        layout.label(text="Tips: Some attributes will only change during rendering")
        layout.prop(get_pref(), "output_file_format")
