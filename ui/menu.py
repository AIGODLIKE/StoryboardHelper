import bpy


class StoryboardMenu(bpy.types.Menu):
    bl_idname = "STORYBOARD_MT_menu"
    bl_label = "Storyboard"

    def draw(self, context):
        from ..ops.rename import WM_OT_batch_rename
        from ..ops.crud import RenameTimelineMarkers,ClearTimelineMarker
        column = self.layout.column()

        column.operator(ClearTimelineMarker.bl_idname, icon="X")
        column.operator(RenameTimelineMarkers.bl_idname, icon="SORTSIZE")
        column.operator(
            WM_OT_batch_rename.bl_idname,
            icon="SORTALPHA",
        ).data_type = "TIMELINE_MARKERS"


register, unregister = bpy.utils.register_classes_factory([StoryboardMenu,])
