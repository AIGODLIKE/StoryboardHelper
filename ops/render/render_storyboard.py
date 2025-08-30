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

    store_data = {}  # store scene data for restore

    preview_count: bpy.props.IntProperty(name="Preview Count", default=5, min=2, max=30, soft_max=20)

    replace_mode: bpy.props.EnumProperty(
        items=[
            ("REPLACE", "Replace", ""),
            ("SELECT_REPLACE", "Select Replace", ""),
        ],
        default="REPLACE",
    )

    storyboard_mode: bpy.props.EnumProperty(items=[
        ("BY_FRAME", "All frame", ""),
        ("BY_STORYBOARD", "Storyboard", ""),
        ("BY_TIMELINES_MARKERS", "Timelines markers", ""),
    ],
        default="BY_TIMELINES_MARKERS",
    )

    @property
    def render_data(self) -> dict:  # {frame:out_name}
        if self.storyboard_mode == "BY_FRAME":
            bm = self.by_frame_mode
            if bm == "GP":
                return self.gp_frames
            elif bm == "AN":
                return self.an_frames
            return self.all_frames
        elif self.storyboard_mode == "BY_STORYBOARD":
            return self.by_storyboard
        elif self.storyboard_mode == "BY_TIMELINES_MARKERS":
            return self.by_timelines_markers
        return {}

    def invoke(self, context, event):
        self.start_time = time.time()
        self.update_by_frame(context)
        self.update_by_timelines_markers(context)
        self.update_by_storyboard(context)
        pref = get_pref()
        return context.window_manager.invoke_props_dialog(self, width=pref.render_width)

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
        getattr(self, f"draw_{self.storyboard_mode.lower()}")(context, column)
        column.separator()
        self.draw_output_path(context, column)
        self.preview_render(context, column)

    def preview_render(self, context, layout):
        column = layout.column(align=True)
        output_paths = self.render_data.keys()
        preview_count = self.preview_count
        folding_count = len(output_paths) - preview_count

        if folding_count > 0:
            column.prop(self, "preview_count")

        for index, frame in enumerate(output_paths):
            if index >= self.preview_count:
                break
            row = column.row(align=True)
            row.label(text=str(self.get_out_file_path(context, frame)))
        if folding_count > 0:
            row = column.row(align=True)
            row.label(text=f"{folding_count}...")
        if len(output_paths) == 0:
            cc = column.column()
            cc.alert = True
            cc.label(text="No frames found for rendering")
            if self.storyboard_mode != "BY_FRAME":
                cc.label(text="Please add a timeline markers")
