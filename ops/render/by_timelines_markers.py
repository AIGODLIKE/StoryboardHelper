from ...utils import get_sort_timeline_markers, get_fill_frame


class ByTimelinesMarkers:
    by_timelines_markers = {}

    def update_by_timelines_markers(self, context):
        self.by_timelines_markers = {m.frame: get_fill_frame(context, m.frame) for m in
                                     get_sort_timeline_markers(context)}

    def draw_by_timelines_markers(self, context, layout):
        ...
