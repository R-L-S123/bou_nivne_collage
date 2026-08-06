from PIL import Image
import json
import requests
from io import BytesIO
import math
import os


WIDTH = 1200
HEIGHT = 1200



def inside_heart(x, y):

    value = (
        (x*x + y*y - 1)**3
        -
        x*x*y**3
    )

    return value <= 0



def create_heart_mask():

    mask = Image.new(
        "L",
        (WIDTH, HEIGHT),
        0
    )


    pixels = mask.load()


    for px in range(WIDTH):

        for py in range(HEIGHT):

            x = (
                px - WIDTH / 2
            ) / (WIDTH / 3)


            y = -(
                py - HEIGHT / 2
            ) / (HEIGHT / 3)


            if inside_heart(x, y):

                pixels[px, py] = 255


    return mask



def download_image(url, token):

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )


    response.raise_for_status()


    return Image.open(
        BytesIO(response.content)
    )



def crop_resize(image, size):

    target_ratio = (
        size[0] / size[1]
    )


    img_ratio = (
        image.width / image.height
    )


    if img_ratio > target_ratio:

        # תמונה רחבה מדי

        new_width = int(
            image.height * target_ratio
        )


        left = (
            image.width - new_width
        ) // 2


        image = image.crop(
            (
                left,
                0,
                left + new_width,
                image.height
            )
        )


    else:

        # תמונה גבוהה מדי

        new_height = int(
            image.width / target_ratio
        )


        top = (
            image.height - new_height
        ) // 2


        image = image.crop(
            (
                0,
                top,
                image.width,
                top + new_height
            )
        )


    return image.resize(
        size,
        Image.LANCZOS
    )



def create_collage():

    old_file = "static/heart_collage.png"

    if os.path.exists(old_file):
        os.remove(old_file)
        
    with open(
        "photos.json",
        encoding="utf-8"
    ) as f:

        photos = json.load(f)



    if len(photos) < 25:

        raise Exception(
            "צריך לפחות 25 תמונות"
        )



    mask = create_heart_mask()



    collage = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT
        ),
        "white"
    )



    # מספר תמונות בשורה

    cols = math.ceil(
        math.sqrt(
            len(photos) * 1.2
        )
    )


    rows = math.ceil(
        len(photos) / cols
    )



    cell_w = WIDTH // cols
    cell_h = HEIGHT // rows



    # מעט הגדלה כדי למנוע רווחים

    BLEED = 1.0



    index = 0



    for row in range(rows):

        for col in range(cols):


            if index >= len(photos):

                break



            photo = photos[index]



            url = (
                photo["url"]
                +
                "=w1000-h1000"
            )



            img = download_image(
                url,
                photo["token"]
            )



            img = crop_resize(
                img,
                (
                    int(cell_w * BLEED),
                    int(cell_h * BLEED)
                )
            )



            x = (
                col * cell_w
                -
                (img.width - cell_w) // 2
            )


            y = (
                row * cell_h
                -
                (img.height - cell_h) // 2
            )



            collage.paste(
                img,
                (
                    x,
                    y
                )
            )



            index += 1



    # חיתוך לצורת לב

    collage.putalpha(
        mask
    )



    collage.save(
        "static/heart_collage.png"
    )



    return "heart_collage.png"
