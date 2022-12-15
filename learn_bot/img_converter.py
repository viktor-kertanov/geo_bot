import os
from os.path import isfile, join
from PIL import Image

def convert_png_to_jpg():
    #converting png images to jpeg images, taking care of the alpha-layers and filling the transparency with white
    images_dir = "data/country_images/"
    images = [f'{images_dir}{f}' for f in os.listdir(images_dir) if isfile(join(images_dir, f)) and '.png' in f]
    new_file_ext = '.jpeg'
    for image in images:
        new_img_name = image.replace('.png', new_file_ext)
        if isfile(new_img_name):
            #if the image already exists we move to the next flag
            print(f"Moving to next image as we already have this one:: {new_img_name}")
            continue
        
        original_img = Image.open(image)
        if original_img.mode in ('RGB','P', 'L'):
            output_img = original_img.convert('RGB')
            output_img.save(new_img_name, format='JPEG', quality=95)
        else:
            original_img.load() # required for png.split()
            output_img = Image.new("RGB", original_img.size, (255, 255, 255))
            output_img.paste(original_img, mask=original_img.split()[3]) # 3 is the alpha channel
            output_img.save(new_img_name, format='JPEG', quality=95)
        
        print(f'Successfully created image:: {new_img_name}')
    
    return images

if __name__ == '__main__':

    print('Helo Bot!')