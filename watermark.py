import os
import argparse
from PIL import Image, UnidentifiedImageError

def add_watermark(directory, logo_path, position, new_directory, padding, scale):
    """
    Add a watermark to images in the specified directory.
    
    Args:
    - directory (str): The directory containing images to be watermarked.
    - logo_path (str): Path to the watermark logo.
    - position (str): Position of the watermark on the image.
    - new_directory (str): Directory to save watermarked images.
    - padding (int): Padding around the logo in pixels.
    """
    EXTS = ('.jpg', '.jpeg', '.png')

    try:
        original_logo = Image.open(logo_path)
    except UnidentifiedImageError:
        print(f"Failed to read logo from {logo_path}. Ensure it's a valid image format.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Using os.walk() to make folder image search recursive
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(EXTS) and filename != os.path.basename(logo_path):

                if('_WM' in filename):
                    continue

                full_path = os.path.join(dirpath, filename)
                try:
                    image = Image.open(full_path)
                except UnidentifiedImageError:
                    print(f"Skipped {filename}. Unsupported image format.")
                    continue
                except Exception as e:
                    print(f"An error occurred while processing {filename}: {e}")
                    continue
                
                full_path = os.path.join(dirpath, filename)
                image = Image.open(full_path)
                width, height = image.size
                logo_width, logo_height = original_logo.size

                
                shorter_side = min(width, height)
                new_logo_width = int(shorter_side * scale/100)
                logo_aspect_ratio = original_logo.width / original_logo.height
                new_logo_height = int(new_logo_width / logo_aspect_ratio)

                # if new_logo_height > int(new_logo_height / logo_aspect_ratio):
                #     new_logo_height = int( float(new_logo_height) * .75)

                # Resize the logo and its mask
                logo = original_logo.resize((new_logo_width, new_logo_height), resample=Image.Resampling.BICUBIC)

                paste_x, paste_y = 0, 0

                if position == 'topleft':
                    paste_x, paste_y = padding, padding
                elif position == 'topright':
                    paste_x, paste_y = width - new_logo_width - padding, padding
                elif position == 'bottomleft':
                    paste_x, paste_y = padding, height - new_logo_height - padding
                elif position == 'bottomright':
                    paste_x, paste_y = width - new_logo_width - padding, height - new_logo_height - padding
                elif position == 'center':
                    paste_x, paste_y = (width - new_logo_width) // 2, (height - new_logo_height) // 2

                try:
                    logo = logo.convert("RGBA")
                    alpha_channel = logo.getchannel('A')
                    new_alpha = alpha_channel.point(lambda i: 128 if i>0 else 0)
                    logo.putalpha(new_alpha)
                    image = image.convert('RGBA')
                    image.alpha_composite(logo, (paste_x, paste_y))
                except Exception as e:
                    print(f"An error occurred: {e}")

                # Determine the relative path
                relative_path = os.path.relpath(dirpath, directory)
                save_directory = new_directory if new_directory else directory
                final_save_directory = os.path.join(save_directory, relative_path)

                # Ensure the new directory exists
                if not os.path.exists(final_save_directory):
                    os.makedirs(final_save_directory)

                fn: str = filename
                spl = fn.split(".")
                ext = spl.pop()
                fn = "".join(spl) + "_WM." + ext

                new_image_path = os.path.join(final_save_directory, fn)
                # Check if the image mode is 'RGBA' and convert it to 'RGB'
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                image.save(new_image_path)
                print('Added watermark to ' + new_image_path)
                
    original_logo.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to add watermarks to images. Given a directory, this will traverse through all its images and apply the specified watermark. The resulting watermarked images can be saved in the same directory or a new specified directory, maintaining the original directory structure.")

    parser.add_argument('--dir', 
                        help="Directory containing the images you want to watermark. The script will search recursively within this directory.",
                        default=r'',
                        metavar='SourceDirectory', required=False)

    parser.add_argument('--logo', 
                        help="Path to the logo image that will be used as the watermark.",
                        default="",
                        metavar='WatermarkLogoPath')

    parser.add_argument('--pos', 
                        choices=['topleft', 'topright', 'bottomleft', 'bottomright', 'center'], 
                        default='bottomleft',
                        help="Specifies the position of the watermark on the image. Default is 'bottomleft'.")

    parser.add_argument('--new_dir',
                        default=None, 
                        help="An optional directory where the watermarked images will be saved. If not provided, watermarked images will use originals in the source directory. The original directory structure will be maintained.",
                        metavar='DestinationDirectory')

    parser.add_argument('--padding', 
                        type=int, 
                        default=0,
                        help="Specifies the padding (in pixels) around the watermark, useful when watermark is positioned at the corners. Default is 0, meaning no padding.")
    parser.add_argument('--scale',
                        type=float, 
                        default=30,
                        help="Resize the watermark based on a percentage of the image's width. E.g., for 10% of the image's width, provide 10.")


    args = parser.parse_args()

    add_watermark(args.dir, args.logo, args.pos, args.new_dir, args.padding, args.scale)
