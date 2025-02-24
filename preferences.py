import bpy

from .ui.panel import refresh_panel


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    panel_name: bpy.props.StringProperty(name="Panel Name", default="Storyboard",
                                         update=lambda self, context: refresh_panel())

    def draw(self, context):
        column = self.layout.column(align=True)
        column.prop(self, "panel_name")


def register():
    bpy.utils.register_class(Preferences)


def unregister():
    bpy.utils.unregister_class(Preferences)
