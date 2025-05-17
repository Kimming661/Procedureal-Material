import unreal
import os
import time

# ===================== Paths =====================
SBSAR_DIR = "/Users/kongjinming/Desktop/R&D/Demo/SD/SBSAR_files"
DEST_PATH = "/Game/Brick"
MASTER_MATERIAL_PATH = "/Script/Engine.Material'/Game/Kim_toolsbag/universalMaterial/M_UniMasterMaterial.M_UniMasterMaterial'"
INSTANCE_FOLDER = f"{DEST_PATH}/Instances"

# Material parameter mapping (needs to be consistent with the parent material)
PARAM_MAPPING = {
    "basecolor": "BaseColor",
    "normal": "Normal",
    "roughness": "Roughness",
    "ao": "AO",
    "metallic": "Metallic"
}

# ===================== instrumented function =====================
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
material_lib = unreal.MaterialEditingLibrary()
editor_lib = unreal.EditorAssetLibrary()

# Make sure the destination folder exists
if not editor_lib.does_directory_exist(INSTANCE_FOLDER):
    editor_lib.make_directory(INSTANCE_FOLDER)

# Import .sbsar files by default (without explicitly calling the Substance factory)
def import_sbsar(filepath, destination):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", filepath)
    task.set_editor_property("destination_path", destination)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

# Find Textures
def find_textures(name, search_path):
    textures = {k: None for k in PARAM_MAPPING.keys()}
    for asset_path in editor_lib.list_assets(search_path, recursive=True):
        asset_name = os.path.basename(asset_path).lower()
        if name.lower() not in asset_name:
            continue
        if "basecolor" in asset_name or "albedo" in asset_name:
            textures["basecolor"] = asset_path
        elif "normal" in asset_name:
            textures["normal"] = asset_path
        elif "roughness" in asset_name:
            textures["roughness"] = asset_path
        elif "ao" in asset_name or "ambientocclusion" in asset_name:
            textures["ao"] = asset_path
        elif "metallic" in asset_name:
            textures["metallic"] = asset_path
    return textures

# Waiting for texture generation
def wait_for_textures(name, search_path, timeout=5):
    for _ in range(timeout * 2):
        textures = find_textures(name, search_path)
        if any(textures.values()):
            return textures
        time.sleep(0.5)
    return textures

# ===================== Mainstream process =====================
for file in os.listdir(SBSAR_DIR):
    if not file.lower().endswith(".sbsar"):
        continue

    name = os.path.splitext(file)[0]
    full_path = os.path.join(SBSAR_DIR, file)
    instance_name = f"MI_{name}"
    instance_path = f"{INSTANCE_FOLDER}/{instance_name}"

    if editor_lib.does_asset_exist(instance_path):
        print(f"already existing {instance_name}，Skipping.")
        continue

    print(f"Importing：{name}.sbsar")
    import_sbsar(full_path, DEST_PATH)

    # Waiting for texture generation
    textures = wait_for_textures(name, DEST_PATH)

    # Load Master Material
    master_mat = editor_lib.load_asset(MASTER_MATERIAL_PATH)
    if not master_mat:
        print(f"Loss of parent material：{MASTER_MATERIAL_PATH}")
        continue

    # Creating material instances
    material_factory = unreal.MaterialInstanceConstantFactoryNew()
    material_instance = asset_tools.create_asset(
        instance_name, INSTANCE_FOLDER,
        unreal.MaterialInstanceConstant,
        material_factory
    )
    material_instance.set_editor_property("parent", master_mat)

    # Binding textures
    for param_key, tex_path in textures.items():
        if tex_path:
            texture = editor_lib.load_asset(tex_path)
            if texture:
                param_name = PARAM_MAPPING[param_key]
                material_lib.set_material_instance_texture_parameter_value(material_instance, param_name, texture)

    # Saved Material Instances
    editor_lib.save_asset(instance_path)
    print(f"Successfully created material instance:{instance_name}")
