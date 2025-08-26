import bpy


class RenderStoryboard:
    markers_dict = {}
    frames = []

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
    enabled_nb_tm_format: bpy.props.BoolProperty(default=True)
    enabled_frame: bpy.props.BoolProperty(default=True)
    enabled_frame_int: bpy.props.BoolProperty(default=True)
    enabled_file_suffix: bpy.props.BoolProperty(default=True)
    enabled_camera: bpy.props.BoolProperty(default=True)

    def get_out_file_path(self, context: bpy.types.Context, frame: int):
        pref = get_pref()
        file_format = pref.output_file_format

        nb = self.render_data[frame]
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
