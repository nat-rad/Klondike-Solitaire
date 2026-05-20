from PIL import Image
import os

input_folder="cards_cut"
output_folder="cards_120x170"

os.makedirs(output_folder,exist_ok=True)

TARGET_WIDTH=120
TARGET_HEIGHT=170

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".png"):
        input_path=os.path.join(input_folder,filename)
        output_path=os.path.join(output_folder,filename)
        img=Image.open(input_path)
        resized=img.resize((TARGET_WIDTH,TARGET_HEIGHT), Image.NEAREST)
        resized.save(output_path)
        print(f"Resized:{filename}")
print("all resized")