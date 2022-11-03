from PIL import Image, ImageOps


def corvert_image(image, mimetype):
    img = Image.open(image.stream)
    mask = Image.open('static/src/mask.png').convert('L')

    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))

    if mimetype != 'image/png':
        output = output.convert('RGB')

    output.putalpha(mask)
    return output