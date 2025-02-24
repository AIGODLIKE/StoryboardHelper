from . import panel, ui_list

modules = [
    panel,
    ui_list
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()
