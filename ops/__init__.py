import bpy

from .crud import AddTimelineMarker, DeleteTimelineMarker, RenameTimelineMarkers
from .rename import WM_OT_batch_rename, BatchRenameAction
from .render import RenderStoryboard

ops_list = [
    AddTimelineMarker,
    DeleteTimelineMarker,
    RenameTimelineMarkers,

    BatchRenameAction,
    WM_OT_batch_rename,

    RenderStoryboard,
]

register, unregister = bpy.utils.register_classes_factory(ops_list)
