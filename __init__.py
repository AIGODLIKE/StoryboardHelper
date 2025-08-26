from . import ui, preferences, ops, update, res

bl_info = {
    "name": "Storyboard",
    "author": "ACGGIT、小萌新、卷纸",
    "version": (1, 0, 3),
    "blender": (4, 3, 0),
    "location": "3DView -> N面板 -> Storyboard",
    "description": "Storyboard",
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
