import bpy

from .utils import get_pref

owner = object()


def update_timeline_markers_index():
    scene = bpy.context.scene
    index = bpy.context.scene.timeline_markers_index

    if -1 < index < len(scene.timeline_markers):
        marker = scene.timeline_markers[index]

        if get_pref().sync_timeline_markers_frame:
            scene.frame_current = marker.frame

        if get_pref().sync_timeline_markers_select:
            for m in scene.timeline_markers:
                m.select = m == marker


bpy.msgbus.subscribe_rna(
    key=(bpy.types.Scene, "timeline_markers_index"),
    owner=owner,
    args=(),
    notify=update_timeline_markers_index,
)


def register():
    ...


def unregister():
    bpy.msgbus.clear_by_owner(owner)
