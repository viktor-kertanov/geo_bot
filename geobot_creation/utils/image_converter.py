import os
from glob import glob
from os.path import isfile

from PIL import Image


def convert_png_to_jpg(images_path, remove_original=False):
    # converting png images to jpeg images,
    # taking care of the alpha-layers and filling the transparency with white
    new_file_ext = ".jpeg"
    for image in images_path:
        new_img_name = image.replace(".png", new_file_ext)
        if isfile(new_img_name):
            # if the image already exists we move to the next flag
            print(
                f"Moving to next image as we already have this one::\
                     {new_img_name}"
            )
            continue

        original_img = Image.open(image)
        if original_img.mode in ("RGB", "P", "L"):
            output_img = original_img.convert("RGB")
            output_img.save(new_img_name, format="JPEG", quality=95)
        else:
            original_img.load()  # required for png.split()
            output_img = Image.new("RGB", original_img.size, (255, 255, 255))
            output_img.paste(
                original_img, mask=original_img.split()[3]
            )  # 3 is the alpha channel
            output_img.save(new_img_name, format="JPEG", quality=95)

        if isfile(new_img_name):
            print(f"Successfully created image:: {new_img_name}")
        if remove_original:
            print("Removing the original image")
            os.remove(image)

    return images_path


if __name__ == "__main__":
    images_folder = "telegram_geobot/country_data/images/"
    original_imgs = glob(f"{images_folder}**/*.png")
