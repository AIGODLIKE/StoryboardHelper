import time

import bpy
from bpy.app.translations import pgettext_iface

from .by_frame import ByFrame
from .by_storyboard import ByStoryboard
from .by_timelines_markers import ByTimelinesMarkers
from .render_output_path import RenderOutputPath
from ...utils import get_pref, is_zh


class RenderStoryboard(
    bpy.types.Operator,
    ByFrame,
    ByStoryboard,
    ByTimelinesMarkers,
    RenderOutputPath,
):
    bl_idname = "render.render_storyboard"
    bl_label = "Render Storyboard"
    # bl_description = "Ctrl: Directly render without previewing"

    timer = None
    start_time = None

    render_data = {}  # {frame:out_name}
    store_data = {}  # store scene data for restore

    preview_count: bpy.props.IntProperty(name="Preview Count", default=10, min=2, max=666, soft_max=20)

    replace_mode: bpy.props.EnumProperty(
        items=[
            ("REPLACE", "Replace", ""),
            ("SELECT_REPLACE", "Select Replace", ""),
        ],
        default="REPLACE",
    )

    def update_storyboard_mode(self, context):
        identity = f"update_{self.storyboard_mode.lower()}"
        print("update_storyboard_mode", identity)
        getattr(self, identity)(context)

    storyboard_mode: bpy.props.EnumProperty(items=[
        ("BY_FRAME", "All frame", ""),
        # ("BY_STORYBOARD", "Storyboard", ""),
        ("BY_TIMELINES_MARKERS", "Timelines markers", ""),
    ],
        default="BY_TIMELINES_MARKERS",
        update=update_storyboard_mode
    )

    def invoke(self, context, event):
        self.start_time = time.time()
        self.render_data = {}
        self.update_storyboard_mode(context)
        return context.window_manager.invoke_props_dialog(self, width=500)

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.exit(context)
            self.report({"INFO"}, "Cancel rendering")
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
                        text = pgettext_iface("The file output path is incorrect, please check!!")
                        self.report({"ERROR"}, text + get_pref().output_file_format)
                        return {"CANCELLED"}
                else:
                    frame = list(self.render_data.keys())[0]
                    context.scene.frame_set(frame)
            else:
                self.exit(context)
                text = pgettext_iface("Render complete")
                self.report({"INFO"}, f"{text} {time.time() - self.start_time}s")
                return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def execute(self, context):
        pref = get_pref()
        if not hasattr(self, "start_time"):
            return {"CANCELLED"}

        self.start_data(context)
        wm = context.window_manager
        self.timer = wm.event_timer_add(pref.delay, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def exit(self, context):
        if self.timer:
            wm = context.window_manager
            wm.event_timer_remove(self.timer)

        context.scene.frame_set(self.store_data["frame"])
        context.space_data.overlay.show_overlays = self.store_data["show_overlays"]
        context.scene.render.filepath = self.store_data["file_path"]

    def start_data(self, context):
        self.store_data = {
            "frame": context.scene.frame_current,
            "file_path": context.scene.render.filepath,
            "show_overlays": context.space_data.overlay.show_overlays
        }
        context.space_data.overlay.show_overlays = False

    def draw(self, context):
        column = self.layout.column(align=True)
        column.operator_context = "EXEC_DEFAULT"

        is_show_zh = is_zh() and context.preferences.view.use_translate_interface
        factor = .1 if is_show_zh else .2
        split = column.split(factor=factor)
        split.label(text="Render frame:")
        split.row().prop(self, "storyboard_mode", expand=True)
        column.separator()

        self.draw_output_path(context, column)
        for index, frame in enumerate(self.render_data.keys()):
            if index >= self.preview_count:
                break
            row = column.row(align=True)
            row.label(text=str(self.get_out_file_path(context, frame)))
        # column.prop(self, "preview_count")
