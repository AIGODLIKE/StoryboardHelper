import bpy

from ..utils import get_pref, get_active_timeline_marker


class StoryboardTimelineMarkerPanel(bpy.types.Panel):
    bl_idname = "STORYBOARD_TIMELINEMARKER_PT_PANEL"
    bl_label = "Timeline Marker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Storyboard"
    bl_options = set()

    def draw(self, context):
        from .ui_list import StoryboardULList
        from ..ops.crud import AddTimelineMarker, DeleteTimelineMarker, RenameTimelineMarkers
        from ..ops.rename import WM_OT_batch_rename

        pref = get_pref()

        column = self.layout.column(align=True)

        row = column.row(align=True)
        row.template_list(
            StoryboardULList.bl_idname, "",
            context.scene, "timeline_markers",
            pref, "timeline_markers_index"
        )
        sub_column = row.column(align=True)
        sub_column.operator(AddTimelineMarker.bl_idname, icon="ADD", text="")
        sub_column.operator(DeleteTimelineMarker.bl_idname, icon="REMOVE", text="")
        sub_column.operator(RenameTimelineMarkers.bl_idname, icon="SORTSIZE", text="")
        sub_column.prop(pref, "sync_timeline_markers_frame", text="", icon="UV_SYNC_SELECT")
        sub_column.prop(pref, "sync_timeline_markers_select", text="", icon="RESTRICT_SELECT_OFF")

        sub_column.separator()
        sub_column.operator(
            WM_OT_batch_rename.bl_idname,
            text="",
            icon="SORTALPHA",
        ).data_type = "TIMELINE_MARKERS"

        row = column.row(align=True)
        row.operator("screen.keyframe_jump", text="", icon="PREV_KEYFRAME").next = False
        row.operator("screen.keyframe_jump", text="", icon="NEXT_KEYFRAME").next = True

        active = get_active_timeline_marker(context)
        if active is not None:
            column.prop(active, "name")
            if hasattr(active, "notes"):
                column.prop(active, "notes")


class StoryboardFCurvesPanel(bpy.types.Panel):
    bl_idname = "STORYBOARD_FCURVES_PT_PANEL"
    bl_label = "F Curves"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "Storyboard"
    bl_options = set()

    # not found in (
    # 'WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI', 'TOOLS', 'TOOL_PROPS', 'ASSET_SHELF', 'ASSET_SHELF_HEADER',
    # 'PREVIEW', 'HUD', 'NAVIGATION_BAR', 'EXECUTE', 'FOOTER', 'TOOL_HEADER', 'XR')
    def draw(self, context):
        from ..ops.scale_f_curves import ScaleFCurvesStoryboard
        layout = self.layout
        layout.operator(ScaleFCurvesStoryboard.bl_idname)
        # for i in dir(context):
        #     layout.label(text=i)


class StoryboardRenderPanel(bpy.types.Panel):
    bl_idname = "STORYBOARD_RENDER_PT_PANEL"
    bl_label = "Render Out"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Storyboard"
    bl_options = set()

    def draw(self, context):
        from ..ops.render.render_storyboard import RenderStoryboard
        pref = get_pref()

        column = self.layout.column(align=True)
        column.prop(context.scene.render, "filepath")
        column.separator()
        column.prop(pref, "delay")
        column.operator("render.opengl", icon="IMAGE_DATA")
        column.operator(RenderStoryboard.bl_idname, icon="RENDER_ANIMATION")


panel_list = [
    StoryboardTimelineMarkerPanel,
    StoryboardFCurvesPanel,
    StoryboardRenderPanel,
]
register, unregister = bpy.utils.register_classes_factory(panel_list)


def refresh_panel():
    unregister()
    from ..utils import get_pref
    panel_name = get_pref().panel_name
    for panel in panel_list:
        panel.bl_category = panel_name
    register()
