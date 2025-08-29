import bpy

from .crud import AddTimelineMarker, DeleteTimelineMarker, RenameTimelineMarkers
from .rename import WM_OT_batch_rename, BatchRenameAction
from .render.render_storyboard import RenderStoryboard
from .scale_f_curves import ScaleFCurvesStoryboard

ops_list = [
    AddTimelineMarker,
    DeleteTimelineMarker,
    RenameTimelineMarkers,

    BatchRenameAction,
    WM_OT_batch_rename,

    RenderStoryboard,

    ScaleFCurvesStoryboard,
]

register, unregister = bpy.utils.register_classes_factory(ops_list)
