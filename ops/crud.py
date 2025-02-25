from functools import cache

import bpy

from ..utils import get_sort_timeline_markers, get_active_timeline_marker


class AddTimelineMarker(bpy.types.Operator):
    bl_idname = "anim.add_timeline_marker"
    bl_label = "Add Timeline Marker"

    name: bpy.props.StringProperty(name="Add Name", default="Frame")

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        scene = context.scene

        frame = scene.frame_current
        scene.timeline_markers.new(self.name, frame=frame)
        return {"FINISHED"}


class DeleteTimelineMarker(bpy.types.Operator):
    bl_idname = "anim.delete_timeline_marker"
    bl_label = "Delete Timeline Marker"

    @classmethod
    def poll(cls, context) -> bool:
        return get_active_timeline_marker(context) is not None

    def execute(self, context):
        active = get_active_timeline_marker(context)

        text = bpy.app.translations.pgettext_iface("Deleted timeline marker %s")

        self.report({"INFO"}, text % active.name)

        context.scene.timeline_markers.remove(active)

        return {"FINISHED"}


@cache
def marker_new_name(prefix: str, suffix: str, index: int, length: int) -> str:
    center = f"{index + 1}".zfill(length)
    return prefix + center + suffix


class RenameTimelineMarkers(bpy.types.Operator):
    bl_idname = "anim.rename_timeline_markers"
    bl_label = "Rename Timeline Markers"

    prefix: bpy.props.StringProperty(name="Prefix", default="F_")
    suffix: bpy.props.StringProperty(name="Suffix", default="0")

    int_size: bpy.props.IntProperty(name="Int Size", default=2)

    preview_rename: bpy.props.BoolProperty(name="Preview", default=True)
    preview_count: bpy.props.IntProperty(name="Preview Count", default=10, min=2, max=666, soft_max=20)

    def draw(self, context):
        column = self.layout.column(align=True)
        column.operator_context = "EXEC_DEFAULT"
        column.prop(self, "prefix")
        column.prop(self, "suffix")
        column.prop(self, "int_size")

        column.separator()
        column.separator()

        column.label(text="Preview")
        row = column.row(align=True)
        row.prop(self, "preview_rename")
        if self.preview_rename:
            row.prop(self, "preview_count")
            split = column.split(align=True)
            split_a = split.column(align=True)
            split_b = split.column(align=True)

            split_a.label(text="From")
            split_b.label(text="To")
            for index, marker in enumerate(get_sort_timeline_markers(context)):
                if index >= self.preview_count:
                    break

                left = split_a.row(align=True)
                left.label(text=marker.name)
                left.label(text=f"{marker.frame}F ")
                left.label(text="->")

                split_b.label(text=marker_new_name(self.prefix, self.suffix, index, self.int_size))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        scene = context.scene
        for index, marker in enumerate(get_sort_timeline_markers(context)):
            marker.name = marker_new_name(self.prefix, self.suffix, index, self.int_size)
        return {"FINISHED"}
