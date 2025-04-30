'''
Name: Auto Crop Borders
Author: Oliver Toparti
Owner: Writen for First Class Watches Ltd. 
Description: Python script to automatically crop white borders and transparent backgrounds from images returned from touch up service provider.
'''

from PIL import Image 
import os
import time
import numpy as np
import shutil

def auto_crop_borders(input_path, output_path, threshold=240, crop_transparent=True, make_square=True, padding=200):

    # Attempt to open the image
    try:
        print(f"Opening image: {input_path}")
        # Check if the file exists
        if not os.path.exists(input_path):
            print(f"Error: Input file {input_path} not found.")
            return False # Return Error. 
            
        # Open the image
        img = Image.open(input_path)    
        
        # Convert to RGBA if it's not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array for processing
        img_array = np.array(img)
        
        print("Detecting borders...")
        start_time = time.time()
        
        # Get image dimensions
        height, width, _ = img_array.shape
        
        # Find boundaries by detecting non-white and non-transparent pixels
        def is_background(pixel, threshold):
            # Check for transparency
            if crop_transparent and pixel[3] == 0:  # Alpha channel is 0
                return True
            # Check for white
            return all(value >= threshold for value in pixel[:3])
        
        
        '''
        Finding image boundaries. 
        '''
        
        
        # Find top boundary
        top = 0
        while top < height and all(is_background(img_array[top, col], threshold) for col in range(width)):
            top += 1
        
        # Find bottom boundary
        bottom = height - 1
        while bottom >= 0 and all(is_background(img_array[bottom, col], threshold) for col in range(width)):
            bottom -= 1
        
        # Find left boundary
        left = 0
        while left < width and all(is_background(img_array[row, left], threshold) for row in range(height)):
            left += 1
        
        # Find right boundary
        right = width - 1
        while right >= 0 and all(is_background(img_array[row, right], threshold) for row in range(height)):
            right -= 1
        
        
        '''
        If no boundaries found or image is all background, return the original
        '''
        if top >= bottom or left >= right:
            print("No clear borders detected. Image might be all background or have no borders.")
            img.save(output_path)
            return True
        
        # No margin needed since we'll add padding later
        
        '''
        Crop the image
        '''
        cropped_img = img.crop((left, top, right + 1, bottom + 1))
        
        '''
        Make the image square with padding
        '''
        if make_square:
            cropped_width, cropped_height = cropped_img.size
            
            # Determine the square size (larger dimension + padding on both sides)
            max_dimension = max(cropped_width, cropped_height)
            square_size = max_dimension + (padding * 2)
            
            # Create a new square image with transparent background
            square_img = Image.new('RGBA', (square_size, square_size), (0, 0, 0, 0))
            
            # Calculate position to paste the cropped image centered in the square
            paste_position = (
                padding + (max_dimension - cropped_width) // 2, 
                padding + (max_dimension - cropped_height) // 2
            )
            
            # Paste the cropped image onto the square canvas
            square_img.paste(cropped_img, paste_position)
            cropped_img = square_img
        
        elapsed = time.time() - start_time
        print(f"Borders detected and cropped in {elapsed:.2f} seconds")
        print(f"Original dimensions: {width}x{height}")
        print(f"Output dimensions: {cropped_img.width}x{cropped_img.height}")
        
        # Save the cropped image
        print(f"Saving output to: {output_path}")
        cropped_img.save(output_path)
        print("Done!")
        return True

    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def process_folder(target_dir):
    """
    Process all folders in the target directory.
    Each folder should have a PNG or Transparent_Background folder with images.
    """
    # Get a list of all directories in the target folder
    try:
        folders = [f for f in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, f))]
        
        for folder in folders:
            folder_path = os.path.join(target_dir, folder)
            print(f"\nProcessing folder: {folder}")
            
            # Create a Resized folder if it doesn't exist
            resized_folder = os.path.join(folder_path, "Resized")
            if not os.path.exists(resized_folder):
                os.makedirs(resized_folder)
                print(f"Created folder: {resized_folder}")
            
            # Try to find image containing folders (PNG or Transparent_Background)
            source_images = []
            
            # Check for PNG folder
            png_folder = os.path.join(folder_path, "PNG")
            if os.path.exists(png_folder) and os.path.isdir(png_folder):
                for file in os.listdir(png_folder):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        source_images.append((os.path.join(png_folder, file), file))
            
            # Check for Transparent_Background folder
            transparent_folder = os.path.join(folder_path, "Transparent_ Background")
            if os.path.exists(transparent_folder) and os.path.isdir(transparent_folder):
                for file in os.listdir(transparent_folder):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        source_images.append((os.path.join(transparent_folder, file), file))
            
            # Process images
            for source_path, filename in source_images:
                base_name = os.path.splitext(filename)[0]
                output_filename = f"{base_name}_cropped.png"
                output_path = os.path.join(resized_folder, output_filename)
                
                print(f"\nProcessing: {source_path}")
                auto_crop_borders(source_path, output_path, threshold=240, crop_transparent=True, make_square=True, padding=700)
            
            if not source_images:
                print(f"No images found in {folder_path}")
    
    except Exception as e:
        print(f"Error processing folders: {e}")

if __name__ == "__main__":
    target_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "target")
    print(f"Processing target directory: {target_directory}")
    process_folder(target_directory)
