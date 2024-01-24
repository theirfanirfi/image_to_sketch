import cv2
import numpy as np
from PIL import Image
import uuid

def convert_to_sketch(image_path):
    print(image_path)
    # Read the image
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted_gray = cv2.bitwise_not(gray)

    # Apply GaussianBlur to the inverted image
    blurred = cv2.GaussianBlur(inverted_gray, (111, 111), 0)

    # Invert the blurred image
    inverted_blurred = cv2.bitwise_not(blurred)

    # Sketch is the combination of the original and inverted blurred image
    sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
    cv2.imwrite(image_path, sketch)
    return image_path

def place_sketch_on_object(sketch_path, object_path, output_path):
    # Open the images
    obj_image = Image.open(object_path)
    sketch_image = Image.open(sketch_path)

    # Get dimensions of ImageA (obj)
    width_obj, height_obj = obj_image.size
    print('obj ', width_obj, height_obj)

    # Resize ImageB (sketch) to fit within ImageA (obj)
    sketch_image = sketch_image.resize((width_obj//2, height_obj//2))

    # Calculate position to center ImageB (sketch) in ImageA (obj)
    left = (width_obj - sketch_image.width) // 2
    top = (height_obj - sketch_image.height) // 2

    print('sketch ', )

    # Paste ImageB (sketch) onto ImageA (obj) at the calculated position
    obj_image.paste(sketch_image, (left, top))
    random_filename = str(uuid.uuid4())[:8] + '.png'
    # Save the result
    obj_image.save(output_path+"/"+random_filename)

# if __name__ == "__main__":
#     # Paths to your input and output images
#     input_image_path = "./user_1_image_IMG_20231206_1851221.jpg"
#     object_image_path = "./user_1_image_IMG_20231206_185122.jpg"
#     output_image_path = "./image.png"

#     # Convert the input image to a sketch
#     sketch = convert_to_sketch(input_image_path)

#     # Save the sketch
#     cv2.imwrite("sketch.png", sketch)

#     # Place the sketch on the object image and save the result
#     place_sketch_on_object("sketch.png", object_image_path, output_image_path)
