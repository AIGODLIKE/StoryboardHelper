import bpy

from .crud import AddTimelineMarker, DeleteTimelineMarker, RenameTimelineMarkers
from .rename import WM_OT_batch_rename, BatchRenameAction
from .render.render_by_frame import RenderStoryboardByFrame
from .render.render_by_timeline_marker import RenderStoryboardByTimelineMarker
from .scale_f_curves import ScaleFCurvesStoryboard

ops_list = [
    AddTimelineMarker,
    DeleteTimelineMarker,
    RenameTimelineMarkers,

    BatchRenameAction,
    WM_OT_batch_rename,

    RenderStoryboardByFrame,
    RenderStoryboardByTimelineMarker,

    ScaleFCurvesStoryboard,
]

register, unregister = bpy.utils.register_classes_factory(ops_list)
