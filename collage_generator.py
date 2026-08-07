from PIL import Image
import os
import math


OUTPUT_SIZE = 1200

def parse_transform(transform):

    if not transform or "matrix" not in transform:
        return 1, 0, 0


    values = transform.replace(
        "matrix(",
        ""
    ).replace(
        ")",
        ""
    ).split(",")


    scale = float(values[0])

    x = -float(values[4])/scale

    y = -float(values[5])/scale


    return scale, x, y

def create_heart_mask(size):

    mask = Image.new(
        "L",
        (size, size),
        0
    )

    pixels = mask.load()


    for y in range(size):

        for x in range(size):

            nx = (
                2 * x - size
            ) / (size * 0.85)


            ny = (
                2 * y - size
            ) / (size * 0.85)


            ny *= 1.15


            heart = (
                nx**2 + ny**2 - 1
            )**3 - nx**2 * ny**3


            if heart <= 0:
                pixels[x, y] = 255


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
        (
            new_width,
            new_height
        ),
        Image.LANCZOS
    )


    left = (
        new_width - width
    ) // 2


    top = (
        new_height - height
    ) // 2


    return image.crop(
        (
            left,
            top,
            left + width,
            top + height
        )
    )

def apply_transform(image, x, y, scale):

    # הגדלה סביב המרכז

    new_width = int(image.width * scale)
    new_height = int(image.height * scale)


    image = image.resize(
        (
            new_width,
            new_height
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


    # CSS מזיז מהמרכז, לא מהפינה

    pos_x = (
        OUTPUT_SIZE // 2
        -
        new_width // 2
        +
        int(x)
    )


    pos_y = (
        OUTPUT_SIZE // 2
        -
        new_height // 2
        +
        int(y)
    )


    canvas.paste(
        image,
        (
            pos_x,
            pos_y
        )
    )


    return canvas
    
def create_collage(image_paths, transform=None):
    scale, x, y = parse_transform(transform)
    images = []

    for path in image_paths:

        try:

            img = Image.open(path)

            img = img.convert(
                "RGB"
            )

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



    cell_width = (
        OUTPUT_SIZE // cols
    )


    cell_height = (
        OUTPUT_SIZE // rows
    )



    for index, img in enumerate(images):

        row = index // cols
        col = index % cols



        img = crop_to_fill(
            img,
            cell_width,
            cell_height
        )



        cell_x = (
            col * cell_width
        )


        cell_y = (
            row * cell_height
        )



        canvas.paste(
            img,
            (
                cell_x,
                cell_y
            )
        )



    # כאן נכנס המיקום והזום של המשתמש

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



    path = (
        "static/output/collage.png"
    )


    result.save(
        path,
        format="PNG",
        optimize=True
    )


    return path



def create_grid(image_paths):

    images = []


    for path in image_paths:

        try:

            img = Image.open(path)

            img = img.convert(
                "RGB"
            )

            images.append(img)


        except Exception:

            continue



    if len(images) == 0:

        raise Exception(
            "No images found"
        )



    size = OUTPUT_SIZE


    cols = math.ceil(
        math.sqrt(len(images))
    )


    rows = math.ceil(
        len(images) / cols
    )



    cell_width = (
        size // cols
    )


    cell_height = (
        size // rows
    )



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



    path = (
        "static/temp/grid.png"
    )


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



    path = (
        "static/temp/heart_overlay.png"
    )


    overlay.save(
        path
    )


    return path
