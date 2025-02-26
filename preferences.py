import bpy

from .ui.panel import refresh_panel


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    panel_name: bpy.props.StringProperty(name="Panel Name", default="Storyboard",
                                         update=lambda self, context: refresh_panel())

    sync_timeline_markers_frame: bpy.props.BoolProperty(name="Sync Timeline Markers Frame", default=True)
    sync_timeline_markers_select: bpy.props.BoolProperty(name="Sync Timeline Markers Select", default=True)

    delay: bpy.props.FloatProperty(
        name="Capture Delay",
        description="How much time to wait (seconds) before capturing each frame, to allow the viewport to clean up",
        min=0.001,
        default=0.005,
        max=1
    )

    def draw(self, context):
        column = self.layout.column(align=True)
        column.prop(self, "panel_name")
        column.prop(self, "render_file_prefix")
        column.prop(self, "render_file_suffix")
        column.separator()
        column.prop(self, "sync_timeline_markers_frame")
        column.prop(self, "sync_timeline_markers_select")
        column.separator()
        column.prop(self, "delay")


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
