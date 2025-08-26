import bpy


class RenderStoryboardByFrame(bpy.types.Operator):
    bl_idname = "render.render_storyboard_by_frame"
    bl_label = "Render Storyboard by frame"
    bl_description = "Ctrl: Directly render without previewing"

    def execute(self, context):
        return {"FINISHED"}
