import bpy

from .storyboard import RenderStoryboard


class RenderStoryboardByFrame(bpy.types.Operator, RenderStoryboard):
    bl_idname = "render.render_storyboard_by_frame"
    bl_label = "Render Storyboard by frame"
    bl_description = "Ctrl: Directly render without previewing"
