import ast
import re

import bpy


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences


def get_language_list() -> list:
    """
    Traceback (most recent call last):
  File "<blender_console>", line 1, in <module>
TypeError: bpy_struct: item.attr = val: enum "a" not found in ('DEFAULT', 'en_US', 'es', 'ja_JP', 'sk_SK', 'vi_VN', 'zh_HANS', 'ar_EG', 'de_DE', 'fr_FR', 'it_IT', 'ko_KR', 'pt_BR', 'pt_PT', 'ru_RU', 'uk_UA', 'zh_TW', 'ab', 'ca_AD', 'cs_CZ', 'eo', 'eu_EU', 'fa_IR', 'ha', 'he_IL', 'hi_IN', 'hr_HR', 'hu_HU', 'id_ID', 'ky_KG', 'nl_NL', 'pl_PL', 'sr_RS', 'sr_RS@latin', 'sv_SE', 'th_TH', 'tr_TR')
    """
    try:
        bpy.context.preferences.view.language = ""
    except TypeError as e:
        matches = re.findall(r'\(([^()]*)\)', e.args[-1])
        return ast.literal_eval(f"({matches[-1]})")


def get_sort_timeline_markers(context: bpy.types.Context) -> list:
    """ERROR 排序出现错误"""
    return sorted(context.scene.timeline_markers, key=lambda m: m.frame)


def get_active_timeline_marker(context: bpy.types.Context) -> "bpy.types.TimelineMarker|None":
    index = get_pref().timeline_markers_index
    scene = context.scene
    if -1 < index < len(scene.timeline_markers):
        return scene.timeline_markers[index]
    return None


def get_scene_gp_all_frames(context: bpy.types.Context) -> "list[int]":
    frames = set()

    for obj in context.scene.objects:
        is_show = (obj.hide_viewport is False) and (obj.hide_get() is False)

        if is_show and obj.type in ("GREASEPENCIL", "GPENCIL") and obj.data:
            for layer in obj.data.layers:
                for frame in layer.frames:
                    frames.add(frame.frame_number)
    return sorted(list(frames))

def get_scene_all_frames(context: bpy.types.Context) -> "list[int]":
    frames = set()

    for obj in context.scene.objects:
        is_show = (obj.hide_viewport is False) and (obj.hide_get() is False)

        if is_show:
            if obj.type in ("GREASEPENCIL", "GPENCIL"):
                for layer in obj.data.layers:
                    for frame in layer.frames:
                        frames.add(frame.frame_number)
            # elif obj.type == "MESH" and obj.animation_data and obj.animation_data.action:
            #     for fc in obj.animation_data.action.fcurves:
            #         ...
    return sorted(list(frames))

def is_zh() -> bool:
    view = bpy.context.preferences.view
    return view.use_translate_interface and view.language in ("zh_HANS", "zh_CN")
