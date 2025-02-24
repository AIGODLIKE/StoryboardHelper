import bpy

from .crud import AddTimelineMarker, DeleteTimelineMarker, SortTimelineMarkers

ops_list = [
    AddTimelineMarker, DeleteTimelineMarker, SortTimelineMarkers
]

register, unregister = bpy.utils.register_classes_factory(ops_list)
