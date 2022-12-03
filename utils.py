import os

from PIL import Image, ImageOps
from flask import url_for


def corvert_image(image):
    img = Image.open(image.stream)
    mask = Image.open(os.getcwd() + url_for('static', filename="src/mask.png")).convert('L')
    print(mask)
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))

    output = output.convert('RGB')

    output.putalpha(mask)
    return output