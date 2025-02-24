import bpy


class StoryboardPanel(bpy.types.Panel):
    bl_idname = "STORYBOARD_PT_PANEL"
    bl_label = "Storyboard"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Storyboard"
    bl_options = set()

    def draw(self, context):
        from .ui_list import Storyboard_ULList
        from ..ops.crud import AddTimelineMarker, DeleteTimelineMarker, SortTimelineMarkers

        scene = context.scene

        column = self.layout.column(align=True)

        row = column.row(align=True)
        row.template_list(
            Storyboard_ULList.bl_idname, "",
            context.scene, "timeline_markers",
            context.scene, "timeline_markers_index"
        )
        sub_column = row.column(align=True)
        sub_column.operator(AddTimelineMarker.bl_idname, icon="ADD", text="")
        sub_column.operator(DeleteTimelineMarker.bl_idname, icon="REMOVE", text="")
        sub_column.operator(SortTimelineMarkers.bl_idname, icon="SORTSIZE", text="")

        if -1 < scene.timeline_markers_index < len(scene.timeline_markers):
            active = scene.timeline_markers[scene.timeline_markers_index]
            column.prop(active, "name")
            column.prop(active, "notes")


panel_list = [
    StoryboardPanel,
]
register, unregister = bpy.utils.register_classes_factory(panel_list)


def refresh_panel():
    unregister_class()
    from ..utils import get_pref
    panel_name = get_pref().panel_name
    for panel in panel_list:
        panel.bl_category = panel_name
    register()
