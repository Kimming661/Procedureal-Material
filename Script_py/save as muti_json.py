import json
import os

# Multi-group brick parameters（Brick01、Brick02、Brick03...）
all_parameters = [
    {
        "Add_grass": False,
        "Small_bricks_ColorChanging": [0.18, 0.2, 0.25],
        "Brick_size_Outside": 42,
        "Brick_size_middle": 19,
        "Brick_size_inside": 9
    },
    {
        "Add_grass": True,
        "Small_bricks_ColorChanging": [0.6, 0.2, 0.25],
        "Brick_size_Outside": 48,
        "Brick_size_middle": 35,
        "Brick_size_inside": 9
    },
    {
        "Add_grass": False,
        "Small_bricks_ColorChanging": [0.1, 0.1, 0.1],
        "Brick_size_Outside": 50,
        "Brick_size_middle": 25,
        "Brick_size_inside": 12
    }
]

# Create bricks folder (if it doesn't exist)
output_folder = os.path.join(os.path.dirname(__file__), "bricks")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Create folder：{output_folder}")
else:
    print(f"Folder already exists：{output_folder}")

# Save each set of parameters as a separate JSON file
for i, params in enumerate(all_parameters, start=1):
    filename = f"Brick{i:02d}.json"
    filepath = os.path.join(output_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"parameters": params}, f, indent=4)

    print(f"Save：{filepath}")
