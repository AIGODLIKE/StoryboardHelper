
class WM_OT_batch_rename(Operator):
    """Rename multiple items at once"""

    bl_idname = "wm.batch_rename"
    bl_label = "Batch Rename"

    bl_options = {'UNDO'}

    data_type: EnumProperty(
        name="Type",
        items=(
            ('OBJECT', "Objects", "", 'OBJECT_DATA', 0),
            ('COLLECTION', "Collections", "", 'OUTLINER_COLLECTION', 1),
            ('MATERIAL', "Materials", "", 'MATERIAL_DATA', 2),
            None,
            # Enum identifiers are compared with `object.type`.
            # Follow order in "Add" menu.
            ('MESH', "Meshes", "", 'MESH_DATA', 3),
            ('CURVE', "Curves", "", 'CURVE_DATA', 4),
            ('META', "Metaballs", "", 'META_DATA', 5),
            ('VOLUME', "Volumes", "", 'VOLUME_DATA', 6),
            ('GPENCIL', "Grease Pencils", "", 'OUTLINER_DATA_GREASEPENCIL', 7),
            ('ARMATURE', "Armatures", "", 'ARMATURE_DATA', 8),
            ('LATTICE', "Lattices", "", 'LATTICE_DATA', 9),
            ('LIGHT', "Lights", "", 'LIGHT_DATA', 10),
            ('LIGHT_PROBE', "Light Probes", "", 'OUTLINER_DATA_LIGHTPROBE', 11),
            ('CAMERA', "Cameras", "", 'CAMERA_DATA', 12),
            ('SPEAKER', "Speakers", "", 'OUTLINER_DATA_SPEAKER', 13),
            None,
            ('BONE', "Bones", "", 'BONE_DATA', 14),
            ('NODE', "Nodes", "", 'NODETREE', 15),
            ('SEQUENCE_STRIP', "Sequence Strips", "", 'SEQ_SEQUENCER', 16),
            ('ACTION_CLIP', "Action Clips", "", 'ACTION', 17),
            None,
            ('SCENE', "Scenes", "", 'SCENE_DATA', 18),
            ('BRUSH', "Brushes", "", 'BRUSH_DATA', 19),
        ),
        translation_context=i18n_contexts.id_id,
        description="Type of data to rename",
    )

    data_source: EnumProperty(
        name="Source",
        items=(
            ('SELECT', "Selected", ""),
            ('ALL', "All", ""),
        ),
    )

    actions: CollectionProperty(type=BatchRenameAction)

    @staticmethod
    def _selected_ids_from_outliner_by_type(context, ty):
        return [
            id for id in context.selected_ids
            if isinstance(id, ty)
            if id.is_editable
        ]

    @staticmethod
    def _selected_ids_from_outliner_by_type_for_object_data(context, ty):
        # Include selected object-data as well as the selected ID's.
        from bpy.types import Object
        # De-duplicate the result as object-data may cause duplicates.
        return tuple(set([
            id for id_base in context.selected_ids
            if isinstance(id := id_base.data if isinstance(id_base, Object) else id_base, ty)
            if id.is_editable
        ]))

    @staticmethod
    def _selected_actions_from_outliner(context):
        # Actions are a special case because they can be accessed directly or via animation-data.
        from bpy.types import Action

        def action_from_any_id(id_data):
            if isinstance(id_data, Action):
                return id_data
            # Not all ID's have animation data.
            if (animation_data := getattr(id_data, "animation_data", None)) is not None:
                return animation_data.action
            return None

        return tuple(set(
            action for id in context.selected_ids
            if (action := action_from_any_id(id)) is not None
            if action.is_editable
        ))

    @classmethod
    def _data_from_context(cls, context, data_type, only_selected, *, check_context=False):
        def _is_editable(data):
            return data.id_data.is_editable and not data.id_data.override_library

        mode = context.mode
        scene = context.scene
        space = context.space_data
        space_type = None if (space is None) else space.type

        data = None
        if space_type == 'SEQUENCE_EDITOR':
            data_type_test = 'SEQUENCE_STRIP'
            if check_context:
                return data_type_test
            if data_type == data_type_test:
                data = (
                    context.selected_strips
                    if only_selected else
                    scene.sequence_editor.strips_all,
                    "name",
                    iface_("Strip(s)"),
                )
        elif space_type == 'NODE_EDITOR':
            data_type_test = 'NODE'
            if check_context:
                return data_type_test
            if data_type == data_type_test:
                data = (
                    context.selected_nodes
                    if only_selected else
                    list(space.node_tree.nodes),
                    "name",
                    iface_("Node(s)"),
                )
        elif space_type == 'OUTLINER':
            data_type_test = 'COLLECTION'
            if check_context:
                return data_type_test
            if data_type == data_type_test:
                data = (
                    cls._selected_ids_from_outliner_by_type(context, bpy.types.Collection)
                    if only_selected else
                    scene.collection.children_recursive,
                    "name",
                    iface_("Collection(s)"),
                )
        else:
            if mode == 'POSE' or (mode == 'WEIGHT_PAINT' and context.pose_object):
                data_type_test = 'BONE'
                if check_context:
                    return data_type_test
                if data_type == data_type_test:
                    data = (
                        [pchan.bone for pchan in context.selected_pose_bones]
                        if only_selected else
                        [pbone.bone for ob in context.objects_in_mode_unique_data for pbone in ob.pose.bones],
                        "name",
                        iface_("Bone(s)"),
                    )
            elif mode == 'EDIT_ARMATURE':
                data_type_test = 'BONE'
                if check_context:
                    return data_type_test
                if data_type == data_type_test:
                    data = (
                        context.selected_editable_bones
                        if only_selected else
                        [ebone for ob in context.objects_in_mode_unique_data for ebone in ob.data.edit_bones],
                        "name",
                        iface_("Edit Bone(s)"),
                    )

        if check_context:
            return 'OBJECT'

        object_data_type_attrs_map = {
            'MESH': ("meshes", iface_("Mesh(es)"), bpy.types.Mesh),
            'CURVE': ("curves", iface_("Curve(s)"), bpy.types.Curve),
            'META': ("metaballs", iface_("Metaball(s)"), bpy.types.MetaBall),
            'VOLUME': ("volumes", iface_("Volume(s)"), bpy.types.Volume),
            'GPENCIL': ("grease_pencils", iface_("Grease Pencil(s)"), bpy.types.GreasePencil),
            'ARMATURE': ("armatures", iface_("Armature(s)"), bpy.types.Armature),
            'LATTICE': ("lattices", iface_("Lattice(s)"), bpy.types.Lattice),
            'LIGHT': ("lights", iface_("Light(s)"), bpy.types.Light),
            'LIGHT_PROBE': ("lightprobes", iface_("Light Probe(s)"), bpy.types.LightProbe),
            'CAMERA': ("cameras", iface_("Camera(s)"), bpy.types.Camera),
            'SPEAKER': ("speakers", iface_("Speaker(s)"), bpy.types.Speaker),
        }

        # Finish with space types.
        if data is None:

            if data_type == 'OBJECT':
                data = (
                    (
                        # Outliner.
                        cls._selected_ids_from_outliner_by_type(context, bpy.types.Object)
                        if space_type == 'OUTLINER' else
                        # 3D View (default).
                        context.selected_editable_objects
                    )
                    if only_selected else
                    [id for id in bpy.data.objects if id.is_editable],
                    "name",
                    iface_("Object(s)"),
                )
            elif data_type == 'COLLECTION':
                data = (
                    # Outliner case is handled already.
                    tuple(set(
                        ob.instance_collection
                        for ob in context.selected_objects
                        if ((ob.instance_type == 'COLLECTION') and
                            (collection := ob.instance_collection) is not None and
                            (collection.is_editable))
                    ))
                    if only_selected else
                    [id for id in bpy.data.collections if id.is_editable],
                    "name",
                    iface_("Collection(s)"),
                )
            elif data_type == 'MATERIAL':
                data = (
                    (
                        # Outliner.
                        cls._selected_ids_from_outliner_by_type(context, bpy.types.Material)
                        if space_type == 'OUTLINER' else
                        # 3D View (default).
                        tuple(set(
                            id
                            for ob in context.selected_objects
                            for slot in ob.material_slots
                            if (id := slot.material) is not None and id.is_editable
                        ))
                    )
                    if only_selected else
                    [id for id in bpy.data.materials if id.is_editable],
                    "name",
                    iface_("Material(s)"),
                )
            elif data_type == 'ACTION_CLIP':
                data = (
                    (
                        # Outliner.
                        cls._selected_actions_from_outliner(context)
                        if space_type == 'OUTLINER' else
                        # 3D View (default).
                        tuple(set(
                            action for ob in context.selected_objects
                            if (((animation_data := ob.animation_data) is not None) and
                                ((action := animation_data.action) is not None) and
                                (action.is_editable))
                        ))
                    )
                    if only_selected else
                    [id for id in bpy.data.actions if id.is_editable],
                    "name",
                    iface_("Action(s)"),
                )
            elif data_type == 'SCENE':
                data = (
                    (
                        # Outliner.
                        cls._selected_ids_from_outliner_by_type(context, bpy.types.Scene)
                        if ((space_type == 'OUTLINER') and only_selected) else
                        [id for id in bpy.data.scenes if id.is_editable]
                    ),
                    "name",
                    iface_("Scene(s)"),
                )
            elif data_type == 'BRUSH':
                data = (
                    (
                        # Outliner.
                        cls._selected_ids_from_outliner_by_type(context, bpy.types.Brush)
                        if ((space_type == 'OUTLINER') and only_selected) else
                        [id for id in bpy.data.brushes if id.is_editable]
                    ),
                    "name",
                    iface_("Brush(es)"),
                )
            elif data_type in object_data_type_attrs_map.keys():
                attr, descr, ty = object_data_type_attrs_map[data_type]
                data = (
                    (
                        # Outliner.
                        cls._selected_ids_from_outliner_by_type_for_object_data(context, ty)
                        if space_type == 'OUTLINER' else
                        # 3D View (default).
                        tuple(set(
                            id
                            for ob in context.selected_objects
                            if ob.type == data_type
                            if (id := ob.data) is not None and id.is_editable
                        ))
                    )
                    if only_selected else
                    [id for id in getattr(bpy.data, attr) if id.is_editable],
                    "name",
                    descr,
                )
        data = ([it for it in data[0] if _is_editable(it)], data[1], data[2])

        return data

    @staticmethod
    def _apply_actions(actions, name):
        import string
        import re

        for action in actions:
            ty = action.type
            if ty == 'SET':
                text = action.set_name
                method = action.set_method
                if method == 'NEW':
                    name = text
                elif method == 'PREFIX':
                    name = text + name
                elif method == 'SUFFIX':
                    name = name + text
                else:
                    assert False, "unreachable"

            elif ty == 'STRIP':
                chars = action.strip_chars
                chars_strip = (
                    "{:s}{:s}{:s}"
                ).format(
                    string.punctuation if 'PUNCT' in chars else "",
                    string.digits if 'DIGIT' in chars else "",
                    " " if 'SPACE' in chars else "",
                )
                part = action.strip_part
                if 'START' in part:
                    name = name.lstrip(chars_strip)
                if 'END' in part:
                    name = name.rstrip(chars_strip)

            elif ty == 'REPLACE':
                if action.use_replace_regex_src:
                    replace_src = action.replace_src
                    if action.use_replace_regex_dst:
                        replace_dst = action.replace_dst
                    else:
                        replace_dst = action.replace_dst.replace("\\", "\\\\")
                else:
                    replace_src = re.escape(action.replace_src)
                    replace_dst = action.replace_dst.replace("\\", "\\\\")
                name = re.sub(
                    replace_src,
                    replace_dst,
                    name,
                    flags=(
                        0 if action.replace_match_case else
                        re.IGNORECASE
                    ),
                )
            elif ty == 'CASE':
                method = action.case_method
                if method == 'UPPER':
                    name = name.upper()
                elif method == 'LOWER':
                    name = name.lower()
                elif method == 'TITLE':
                    name = name.title()
                else:
                    assert False, "unreachable"
            else:
                assert False, "unreachable"
        return name

    def _data_update(self, context):
        only_selected = self.data_source == 'SELECT'

        self._data = self._data_from_context(context, self.data_type, only_selected)
        if self._data is None:
            self.data_type = self._data_from_context(context, None, False, check_context=True)
            self._data = self._data_from_context(context, self.data_type, only_selected)

        self._data_source_prev = self.data_source
        self._data_type_prev = self.data_type

    def draw(self, context):
        import re

        layout = self.layout

        split = layout.split(align=True)
        split.row(align=True).prop(self, "data_source", expand=True)
        split.prop(self, "data_type", text="")

        for action in self.actions:
            box = layout.box()
            split = box.split(factor=0.87)

            # Column 1: main content.
            col = split.column()

            # Label's width.
            fac = 0.25

            # Row 1: type.
            row = col.split(factor=fac)
            row.alignment = 'RIGHT'
            row.label(text="Type")
            row.prop(action, "type", text="")

            ty = action.type
            if ty == 'SET':
                # Row 2: method.
                row = col.split(factor=fac)
                row.alignment = 'RIGHT'
                row.label(text="Method")
                row.row().prop(action, "set_method", expand=True)

                # Row 3: name.
                row = col.split(factor=fac)
                row.alignment = 'RIGHT'
                row.label(text="Name")
                row.prop(action, "set_name", text="")

            elif ty == 'STRIP':
                # Row 2: chars.
                row = col.split(factor=fac)
                row.alignment = 'RIGHT'
                row.label(text="Characters")
                row.row().prop(action, "strip_chars")

                # Row 3: part.
                row = col.split(factor=fac)
                row.alignment = 'RIGHT'
                row.label(text="Strip From")
                row.row().prop(action, "strip_part")

            elif ty == 'REPLACE':
                # Row 2: find.
                row = col.split(factor=fac)

                re_error_src = None
                if action.use_replace_regex_src:
                    try:
                        re.compile(action.replace_src)
                    except Exception as ex:
                        re_error_src = str(ex)
                        row.alert = True

                row.alignment = 'RIGHT'
                row.label(text="Find")
                sub = row.row(align=True)
                sub.prop(action, "replace_src", text="")
                sub.prop(action, "use_replace_regex_src", text="", icon='SORTBYEXT')

                # Row.
                if re_error_src is not None:
                    row = col.split(factor=fac)
                    row.label(text="")
                    row.alert = True
                    row.label(text=re_error_src)

                # Row 3: replace.
                row = col.split(factor=fac)

                re_error_dst = None
                if action.use_replace_regex_src:
                    if action.use_replace_regex_dst:
                        if re_error_src is None:
                            try:
                                re.sub(action.replace_src, action.replace_dst, "")
                            except Exception as ex:
                                re_error_dst = str(ex)
                                row.alert = True

                row.alignment = 'RIGHT'
                row.label(text="Replace")
                sub = row.row(align=True)
                sub.prop(action, "replace_dst", text="")
                subsub = sub.row(align=True)
                subsub.active = action.use_replace_regex_src
                subsub.prop(action, "use_replace_regex_dst", text="", icon='SORTBYEXT')

                # Row.
                if re_error_dst is not None:
                    row = col.split(factor=fac)
                    row.label(text="")
                    row.alert = True
                    row.label(text=re_error_dst)

                # Row 4: case.
                row = col.split(factor=fac)
                row.label(text="")
                row.prop(action, "replace_match_case")

            elif ty == 'CASE':
                # Row 2: method.
                row = col.split(factor=fac)
                row.alignment = 'RIGHT'
                row.label(text="Convert To")
                row.row().prop(action, "case_method", expand=True)

            # Column 2: add-remove.
            row = split.split(align=True)
            row.prop(action, "op_remove", text="", icon='REMOVE')
            row.prop(action, "op_add", text="", icon='ADD')

        layout.label(text=iface_("Rename {:d} {:s}").format(len(self._data[0]), self._data[2]), translate=False)

    def check(self, context):
        changed = False
        for i, action in enumerate(self.actions):
            if action.op_add:
                action.op_add = False
                self.actions.add()
                if i + 2 != len(self.actions):
                    self.actions.move(len(self.actions) - 1, i + 1)
                changed = True
                break
            if action.op_remove:
                action.op_remove = False
                if len(self.actions) > 1:
                    self.actions.remove(i)
                changed = True
                break

        if (
                (self._data_source_prev != self.data_source) or
                (self._data_type_prev != self.data_type)
        ):
            self._data_update(context)
            changed = True

        return changed

    def execute(self, context):
        import re

        seq, attr, descr = self._data

        actions = self.actions

        # Sanitize actions.
        for action in actions:
            if action.use_replace_regex_src:
                try:
                    re.compile(action.replace_src)
                except Exception as ex:
                    self.report({'ERROR'}, "Invalid regular expression (find): " + str(ex))
                    return {'CANCELLED'}

                if action.use_replace_regex_dst:
                    try:
                        re.sub(action.replace_src, action.replace_dst, "")
                    except Exception as ex:
                        self.report({'ERROR'}, "Invalid regular expression (replace): " + str(ex))
                        return {'CANCELLED'}

        total_len = 0
        change_len = 0
        for item in seq:
            name_src = getattr(item, attr)
            name_dst = self._apply_actions(actions, name_src)
            if name_src != name_dst:
                setattr(item, attr, name_dst)
                change_len += 1
            total_len += 1

        self.report({'INFO'}, rpt_("Renamed {:d} of {:d} {:s}").format(change_len, total_len, descr))

        return {'FINISHED'}

    def invoke(self, context, event):

        self._data_update(context)

        if not self.actions:
            self.actions.add()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

