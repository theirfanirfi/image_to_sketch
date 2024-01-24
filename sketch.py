import cv2
import os
import uuid
import numpy as np


def label_device_with_resized_image(device_image_path, label_image_path, output_path, scale_factor):
    
     # Read the device image and the label image
    device_image = cv2.imread(device_image_path)
    label_image = cv2.imread(label_image_path)

    # Resize the label image based on the scale factor
    label_image_resized = cv2.resize(label_image, None, fx=scale_factor, fy=scale_factor)

    # Get the position to place the label image on the cup image
    position = (
        float((device_image.shape[1] - label_image_resized.shape[1]) / 2.3),
        float((device_image.shape[0] - label_image_resized.shape[0]) / 2)
    )

    # Replace the corresponding region in the cup image with the label image
    device_image[int(position[1]):int(position[1] + label_image_resized.shape[0]),
              int(position[0]):int(position[0] + label_image_resized.shape[1])] = label_image_resized
    
    # Save the result to the specified output path
    cv2.imwrite(output_path, device_image)

    





def convert_to_sketch_and_save(image_path, output_folder):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted_image = cv2.bitwise_not(gray_image)

    # Blur the inverted image using GaussianBlur
    blurred_image = cv2.GaussianBlur(inverted_image, (111, 111), 0)

    # Invert the blurred image
    inverted_blurred_image = cv2.bitwise_not(blurred_image)

    # Perfect sketch is the combination of the inverted blurred image and the original image
    perfect_sketch = cv2.divide(gray_image, inverted_blurred_image, scale=220.0)


    # Merge the sketch and alpha channel to make it transparent
    sketched_with_alpha = cv2.merge([perfect_sketch, perfect_sketch, perfect_sketch])

    # Generate a random filename
    random_filename = str(uuid.uuid4())[:8] + '.png'

    # Save the sketched image with transparency to the specified output folder with the random filename
    output_path = os.path.join(output_folder, random_filename)
    cv2.imwrite(output_path, sketched_with_alpha)

    return output_path