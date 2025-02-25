import bpy


class Storyboard_ULList(bpy.types.UIList):
    bl_idname = "STORYBOARD_UL_LIST"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.label(text=item.name, translate=False)
        row.prop(item, "frame")
        row.prop(item, "select", text="", icon="RESTRICT_SELECT_OFF" if item.select else "RESTRICT_SELECT_ON")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname).values()
        sort = sorted(items, key=lambda x: x.frame)
        flt_neworder = [sort.index(i) for i in items]

        return [self.bitflag_filter_item] * len(items), flt_neworder


ui_list = [
    Storyboard_ULList,
]

register, unregister = bpy.utils.register_classes_factory(ui_list)
