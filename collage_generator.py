from PIL import Image, ImageDraw
import os
import math

OUTPUT_SIZE = 1200

def create_heart_mask(size):

    mask = Image.new(
        "L",
        (size, size),
        0
    )

    pixels = mask.load()


    for y in range(size):

        for x in range(size):

            # מרכז הקואורדינטות
            nx = (
                2 * x - size
            ) / (size * 0.85)


            ny = (
                2 * y - size
            ) / (size * 0.85)


            # תיקון יחס גובה
            ny *= 1.15


            heart = (
                nx**2 + ny**2 - 1
            )**3 - nx**2 * ny**3


            if heart <= 0:

                pixels[x,y] = 255


    return mask

def crop_to_fill(image, width, height):
    """
    חיתוך תמונה בלי עיוות
    """

    img_ratio = image.width / image.height

    target_ratio = width / height


    if img_ratio > target_ratio:

        new_height = height
        new_width = int(height * img_ratio)

    else:

        new_width = width
        new_height = int(width / img_ratio)


    image = image.resize(
        (new_width, new_height),
        Image.LANCZOS
    )


    left = (new_width - width) // 2
    top = (new_height - height) // 2


    return image.crop(
        (
            left,
            top,
            left + width,
            top + height
        )
    )


def create_collage(image_paths,x=0,y=0,scale=1):
    images = []

    for path in image_paths:

        try:

            img = Image.open(path)

            img = img.convert("RGB")

            images.append(img)


        except Exception:

            continue



    if len(images) == 0:

        raise Exception(
            "No images found"
        )



    canvas = Image.new(
        "RGB",
        (
            OUTPUT_SIZE,
            OUTPUT_SIZE
        ),
        "white"
    )



    count = len(images)


    cols = math.ceil(
        math.sqrt(count)
    )

    rows = math.ceil(
        count / cols
    )



    cell_width = OUTPUT_SIZE // cols
    cell_height = OUTPUT_SIZE // rows



    for index, img in enumerate(images):

        row = index // cols
        col = index % cols


        img = crop_to_fill(
            img,
            cell_width,
            cell_height
        )


        x = col * cell_width
        y = row * cell_height


        canvas.paste(
            img,
            (
                x,
                y
            )
        )


    canvas = apply_transform(
        canvas,
        x,
        y,
        scale
    )
    mask = create_heart_mask(
        OUTPUT_SIZE
    )
    mask = mask.transpose(
        Image.Transpose.FLIP_TOP_BOTTOM
    )

    result = Image.new(
        "RGB",
        (
            OUTPUT_SIZE,
            OUTPUT_SIZE
        ),
        "white"
    )


    result.paste(
        canvas,
        (
            0,
            0
        ),
        mask
    )



    os.makedirs(
        "static/output",
        exist_ok=True
    )

    result = result.convert("RGB")
    result.save(
        "static/output/collage.png",
        format="PNG",
        optimize=True
    )


    return (
        "static/output/collage.png"
    )


def create_grid(image_paths):

    images = []


    for path in image_paths:

        try:

            img = Image.open(path)

            img = img.convert("RGB")

            images.append(img)

        except Exception:

            continue


    if len(images) == 0:
        raise Exception("No images found")


    size = 1200


    cols = math.ceil(
        math.sqrt(len(images))
    )

    rows = math.ceil(
        len(images) / cols
    )


    cell_width = size // cols
    cell_height = size // rows


    canvas = Image.new(
        "RGB",
        (
            size,
            size
        ),
        "white"
    )


    for index, img in enumerate(images):

        row = index // cols
        col = index % cols


        img = crop_to_fill(
            img,
            cell_width,
            cell_height
        )


        canvas.paste(
            img,
            (
                col * cell_width,
                row * cell_height
            )
        )


    os.makedirs(
        "static/temp",
        exist_ok=True
    )


    path = "static/temp/grid.png"


    canvas.save(
        path
    )


    return path

def save_heart_overlay():

    mask = create_heart_mask(
        OUTPUT_SIZE
    )
    mask = mask.transpose(
        Image.Transpose.FLIP_TOP_BOTTOM
    )

    overlay = Image.new(
        "RGBA",
        (
            OUTPUT_SIZE,
            OUTPUT_SIZE
        ),
        (
            255,
            255,
            255,
            255
        )
    )


    pixels = overlay.load()
    mask_pixels = mask.load()


    for y in range(OUTPUT_SIZE):

        for x in range(OUTPUT_SIZE):

            # בתוך הלב = שקוף
            if mask_pixels[x, y] == 255:

                pixels[x, y] = (
                    255,
                    255,
                    255,
                    0
                )


    os.makedirs(
        "static/temp",
        exist_ok=True
    )


    path = "static/temp/heart_overlay.png"


    overlay.save(
        path
    )


    return path
def apply_transform(image, x, y, scale):

    w, h = image.size


    new_w = int(w * scale)
    new_h = int(h * scale)


    image = image.resize(
        (
            new_w,
            new_h
        ),
        Image.LANCZOS
    )


    canvas = Image.new(
        "RGB",
        (
            OUTPUT_SIZE,
            OUTPUT_SIZE
        ),
        "white"
    )


    # כמו CSS scale מהמרכז

    base_x = (
        OUTPUT_SIZE - new_w
    ) // 2


    base_y = (
        OUTPUT_SIZE - new_h
    ) // 2


    canvas.paste(
        image,
        (
            base_x + int(x),
            base_y + int(y)
        )
    )


    return canvas
