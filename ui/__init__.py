from . import panel, ui_list, menu

modules = [
    menu,
    panel,
    ui_list
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()
