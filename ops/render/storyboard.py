import os
import time

import bpy

from ...utils import get_pref


class RenderStoryboard:


    def execute(self, context):
        pref = get_pref()
        if not hasattr(self, "start_time"):
            return {"CANCELLED"}

        self.start_data(context)
        wm = context.window_manager
        self.timer = wm.event_timer_add(pref.delay, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.stop(context)
            self.report({"INFO"}, f"Cancel rendering")
            return {"CANCELLED"}

        if event.type == "TIMER":
            scene = context.scene
            frame_current = scene.frame_current

            if self.render_data:
                if frame_current in self.render_data:
                    bpy.ops.render.opengl()
                    try:
                        if 'Render Result' in bpy.data.images:
                            bpy.data.images['Render Result'].save_render(self.get_out_file_path(context, frame_current))
                            self.render_data.pop(frame_current)
                    except RuntimeError:
                        text = bpy.app.translations.pgettext_iface("The file output path is incorrect, please check!!")
                        self.report({"ERROR"}, text + get_pref().output_file_format)
                        return {"CANCELLED"}
                else:
                    frame = list(self.render_data.keys())[0]
                    context.scene.frame_set(frame)
            else:
                self.stop(context)
                text = bpy.app.translations.pgettext_iface("Render complete")
                self.report({"INFO"}, f"{text} {time.time() - self.start_time}s")
                return {"FINISHED"}
        return {"RUNNING_MODAL"}
