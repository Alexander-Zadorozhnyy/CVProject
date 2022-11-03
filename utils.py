from PIL import Image, ImageOps
from flask import url_for


def corvert_image(image, mimetype):
    img = Image.open(image.stream)
    mask = Image.open(url_for('static', filename="src/mask.png")).convert('L')

    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))

    if mimetype != 'image/png':
        output = output.convert('RGB')

    output.putalpha(mask)
    return output