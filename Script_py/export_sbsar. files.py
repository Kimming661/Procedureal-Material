import os
import subprocess

# Path:
sbsmutator_path = r"E:\DDC_install\Substance Automation Toolkit\sbsmutator.exe"
sbs_file = os.path.join("sbs_files", "Brick_color.sbs")
preset_folder = "presets"
output_folder = "output"

# Ensure output folder exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over the json file
for preset_file in os.listdir(preset_folder):
    if preset_file.endswith(".json"):
        preset_path = os.path.join(preset_folder, preset_file)

        name = os.path.splitext(preset_file)[0]
        output_path = os.path.join(output_folder, f"{name}.sbsar")

        command = [
            sbsmutator_path,
            "--input", sbs_file,
            "--input-parameters", preset_path,
            "--output-name", f"{name}.sbsar",
            "--output-path", output_folder,
        ]

        print(f"🚀 Exporting: {output_path} ...")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Successful exporting：{output_path}")
        else:
            print(f"❌ Failure exporting：{output_path}")
            print(result.stderr)
