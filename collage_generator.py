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

    draw = ImageDraw.Draw(mask)


    points = []

    for y in range(size):

        for x in range(size):

            nx = (
                x - size / 2
            ) / (size / 2)

            ny = (
                y - size / 2
            ) / (size / 2)


            heart = (
                nx**2 +
                ny**2 -
                0.3
            )**3 - (
                nx**2 *
                ny**3
            )


            if heart < 0:

                points.append(
                    (x, y)
                )


    draw.polygon(
        points,
        fill=255
    )


    return mask

def crop_to_fill(image, width, height):
    """
    חיתוך תמונה בלי עיוות
    """

    img_ratio = (
        image.width /
        image.height
    )

    target_ratio = (
        width /
        height
    )


    if img_ratio > target_ratio:

        new_height = height

        new_width = int(
            height * img_ratio
        )

    else:

        new_width = width

        new_height = int(
            width / img_ratio
        )


    image = image.resize(
        (new_width, new_height),
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





def create_collage(image_paths):

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


        x = (
            col * cell_width
        )

        y = (
            row * cell_height
        )


        canvas.paste(
            img,
            (
                x,
                y
            )
        )



    mask = create_heart_mask(
        OUTPUT_SIZE
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


    result.save(
        "static/output/collage.png"
    )


    return (
        "static/output/collage.png"
    )
