import bpy

from .ui.panel import refresh_panel


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    panel_name: bpy.props.StringProperty(name="Panel Name", default="Storyboard",
                                         update=lambda self, context: refresh_panel())

    sync_timeline_markers_frame: bpy.props.BoolProperty(name="Sync Timeline Markers Frame", default=True)
    sync_timeline_markers_select: bpy.props.BoolProperty(name="Sync Timeline Markers Select", default=True)

    def draw(self, context):
        column = self.layout.column(align=True)
        column.prop(self, "panel_name")
        column.prop(self, "render_file_prefix")
        column.prop(self, "render_file_suffix")
        column.separator()
        column.prop(self, "sync_timeline_markers_frame")
        column.prop(self, "sync_timeline_markers_select")


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
