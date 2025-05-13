import unreal
import os
import time

# ===================== Setting =====================
# After manually importing .sbsar, the texture resources will be generated under this virtual path
# (make sure it's consistent)
DEST_PATH = "/Game/Brick"
MASTER_MATERIAL_PATH = "/Script/Engine.Material'/Game/Kim_toolsbag/universalMaterial/M_UniMasterMaterial.M_UniMasterMaterial'"
INSTANCE_FOLDER = f"{DEST_PATH}/Instances"

# Material parameter mapping: maps the texture keyword to the parent material parameter name
# (please adjust according to your parent material parameter)
PARAM_MAPPING = {
    "basecolor": "BaseColor",
    "normal": "Normal",
    "roughness": "Roughness",
    "ao": "AO",
    "metallic": "Metallic"
}

# SBSAR name list: here you fill in the prefix of the .sbsar file you have manually imported, e.g. “Brick01”
# If the mapping is named “Brick_INST_ao”, the prefix of the generated mapping should be filled in here,
# such as “Brick” or “Brick01”.
SBSAR_NAMES = ["Brick_01", "Brick_03"]

# ===================== Tool Preparation =====================
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
material_lib = unreal.MaterialEditingLibrary()
editor_lib = unreal.EditorAssetLibrary()

# Ensure that the material instance save directory exists
if not editor_lib.does_directory_exist(INSTANCE_FOLDER):
    editor_lib.make_directory(INSTANCE_FOLDER)


# ===================== Function Definition =====================

# Find Maps
def find_textures(name_prefix, search_path):
    textures = {k: None for k in PARAM_MAPPING.keys()}
    # Iterate over all resources under the specified virtual path (recursive)
    for asset_path in editor_lib.list_assets(search_path, recursive=True):
        asset_name = os.path.basename(asset_path).lower()
        # Filter by prefix, e.g. resources starting with “brick” or “brick01”
        if not asset_name.startswith(name_prefix.lower()):
            continue
        # Match posting types based on keywords included
        if "base" in asset_name or "albedo" in asset_name:
            textures["basecolor"] = asset_path
        elif "nrm" in asset_name or "normal" in asset_name:
            textures["normal"] = asset_path
        elif "rough" in asset_name or "roughness" in asset_name:
            textures["roughness"] = asset_path
        elif "ao" in asset_name or "ambientocclusion" in asset_name:
            textures["ao"] = asset_path
        elif "metal" in asset_name or "metallic" in asset_name:
            textures["metallic"] = asset_path
    return textures


# Waiting for texture generation
def wait_for_textures(name_prefix, search_path, timeout=5):
    for _ in range(timeout * 2):
        textures = find_textures(name_prefix, search_path)
        # If at least one of the mappings is found, return
        if any(value is not None for value in textures.values()):
            return textures
        time.sleep(0.5)
    return textures


# ===================== Main Workflow =====================
for sbsar_name in SBSAR_NAMES:
    # Here, sbsar_name is the prefix used for texture generation, e.g. “Brick”
    # (Assuming the generated mapping name is something like “Brick_INST_ao” etc.)
    instance_name = f"MI_{sbsar_name}"
    instance_path = f"{INSTANCE_FOLDER}/{instance_name}"

    if editor_lib.does_asset_exist(instance_path):
        unreal.log_warning(f"⚠️ Material Instance {instance_name} Already exist, skip")
        continue

    unreal.log("🎯 Start processing the mapping, prefix：" + sbsar_name)
    textures = wait_for_textures(sbsar_name, DEST_PATH)
    unreal.log("🧪The path of the found texture:" + str(textures))

    # Check if at least one mapping is found
    if not any(textures.values()):
        unreal.log_error(f"❌ Not found textures，prefix：{sbsar_name}")
        continue

    # Load the parent material
    # (make sure the parent material path is correct and does not contain illegal characters)
    master_mat = editor_lib.load_asset(MASTER_MATERIAL_PATH)
    if not master_mat:
        unreal.log_error("❌ Master material lost：" + MASTER_MATERIAL_PATH)
        continue

    # Creating material instances
    material_factory = unreal.MaterialInstanceConstantFactoryNew()
    material_instance = asset_tools.create_asset(
        instance_name, INSTANCE_FOLDER,
        unreal.MaterialInstanceConstant,
        material_factory
    )
    if material_instance is None:
        unreal.log_error("❌ Failed to create material instance：" + instance_name)
        continue

    material_instance.set_editor_property("parent", master_mat)

    # Binding maps
    for param_key, tex_path in textures.items():
        if tex_path is None:
            unreal.log_warning(f"🚫 Texture {param_key} Not found，skipping blinding.")
            continue
        texture = editor_lib.load_asset(tex_path)
        if texture:
            # Use the mapping table to get the correct parameter names
            param_name = PARAM_MAPPING[param_key]
            material_lib.set_material_instance_texture_parameter_value(material_instance, param_name, texture)
            unreal.log("🧷 Setting textures parameters " + param_name + " Corresponding texture: " + os.path.basename(tex_path))
        else:
            unreal.log_warning("🚫 Failed to load texture: " + tex_path)

    # Save Material Example
    editor_lib.save_asset(instance_path)
    unreal.log("✅ Successfully created material instance:" + instance_name)