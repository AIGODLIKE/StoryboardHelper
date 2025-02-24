import bpy


class AddTimelineMarker(bpy.types.Operator):
    bl_idname = "anim.add_timeline_marker"
    bl_label = "Add Timeline Marker"

    name: bpy.props.StringProperty(name="Name", default="Frame")

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

    def execute(self, context):
        return {"FINISHED"}


class SortTimelineMarkers(bpy.types.Operator):
    bl_idname = "anim.sort_timeline_markers"
    bl_label = "Sort Timeline Markers"

    def execute(self, context):
        return {"FINISHED"}
