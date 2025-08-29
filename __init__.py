from . import ui, preferences, ops, update, res

bl_info = {
    "name": "Storyboard Helper",
    "author": "Niceboat Animation、小萌新、JuanZhi、只剩一瓶辣椒酱",
    "version": (1, 0, 4),
    "blender": (4, 3, 0),
    "location": "3DView -> N Panel -> Storyboard",
    "description": "Storyboard Helper",
    "category": "ACGGIT",
}

mods = [
    preferences,
    update,
    ops,
    ui,
    res,
]


def register():
    for mod in mods:
        mod.register()


def unregister():
    for mod in mods:
        mod.unregister()
