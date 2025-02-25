from . import ui, preferences, ops, update

bl_info = {
    "name": "Storyboard",
    "author": "AIGODLIKE Community: 小萌新,卷纸",
    "version": (1, 0, 0),
    "blender": (4, 3, 0),
    "location": "3DView -> N面板 -> Storyboard",
    "description": "Storyboard",
    "category": "AIGODLIKE",
}

mods = [
    preferences,
    update,
    ops,
    ui,
]


def register():
    for mod in mods:
        mod.register()


def unregister():
    for mod in mods:
        mod.unregister()
