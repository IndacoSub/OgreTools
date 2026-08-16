# write_text.py

from PIL import Image, ImageDraw, ImageFont
import argparse

# ============================================================
# CONFIG GENERALE
# ============================================================

SCALE = 4

COLOR_TEXT_MODE1 = (247, 8, 8, 255)
COLOR_OUTLINE_MODE1 = (255, 255, 255, 255)
COLOR_SHADOW_MODE1 = (165, 165, 165, 255)

COLOR_TEXT_MODE2 = (255, 255, 255, 255)
COLOR_OUTLINE_MODE2 = (0, 0, 0, 255)

# ============================================================
# MODE0 — 128×16, testo grigio #555555, outline bianca, shadow
# ============================================================

def render_mode0(text):
    WIDTH = 128
    HEIGHT = 16
    FONT_PATH = "TCCB____.TTF"
    FONT_SIZE = 18

    COLOR_TEXT_MODE0 = (85, 85, 85, 255)  # #555555

    big_w = WIDTH * SCALE
    big_h = HEIGHT * SCALE

    font_big = ImageFont.truetype(FONT_PATH, FONT_SIZE * SCALE)

    # tela di sicurezza
    tmp_w = big_w * 2
    tmp_h = big_h
    img_tmp = Image.new("RGBA", (tmp_w, tmp_h), (0, 0, 0, 0))
    draw_tmp = ImageDraw.Draw(img_tmp)

    base_x_tmp = 0
    base_y_tmp = 0

    # outline 2px
    for ox in range(-2 * SCALE, 2 * SCALE + 1, SCALE):
        for oy in range(-2 * SCALE, 2 * SCALE + 1, SCALE):
            draw_tmp.text((base_x_tmp + ox, base_y_tmp + oy), text, font=font_big, fill=COLOR_OUTLINE_MODE1)

    # shadow
    draw_tmp.text((base_x_tmp, base_y_tmp + SCALE), text, font=font_big, fill=COLOR_SHADOW_MODE1)

    # testo grigio
    draw_tmp.text((base_x_tmp, base_y_tmp), text, font=font_big, fill=COLOR_TEXT_MODE0)

    # crop
    bbox_tmp = img_tmp.getbbox()
    cropped_big = img_tmp.crop(bbox_tmp)
    w_big, h_big = cropped_big.size

    # stretch fino a pixel 86 (parte da pixel 6)
    max_big_width = (86 - 6) * SCALE

    if w_big > max_big_width:
        stretched_big = cropped_big.resize((max_big_width, h_big), Image.NEAREST)
    else:
        stretched_big = cropped_big

    # canvas finale grande
    img_big = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    img_big.paste(stretched_big, (6 * SCALE, 1), stretched_big)

    # downscale
    img_final = img_big.resize((WIDTH, HEIGHT), Image.NEAREST)
    return img_final


# ============================================================
# MODE1 — 128×16, rosso, outline bianca, shadow, stretch fino a pixel 86
# ============================================================

def render_mode1(text):
    WIDTH = 128
    HEIGHT = 16
    FONT_PATH = "TCCB____.TTF"
    FONT_SIZE = 18

    big_w = WIDTH * SCALE
    big_h = HEIGHT * SCALE

    font_big = ImageFont.truetype(FONT_PATH, FONT_SIZE * SCALE)

    # tela di sicurezza
    tmp_w = big_w * 2
    tmp_h = big_h
    img_tmp = Image.new("RGBA", (tmp_w, tmp_h), (0, 0, 0, 0))
    draw_tmp = ImageDraw.Draw(img_tmp)

    base_x_tmp = 0
    base_y_tmp = 0

    # outline 2px
    for ox in range(-2 * SCALE, 2 * SCALE + 1, SCALE):
        for oy in range(-2 * SCALE, 2 * SCALE + 1, SCALE):
            draw_tmp.text((base_x_tmp + ox, base_y_tmp + oy), text, font=font_big, fill=COLOR_OUTLINE_MODE1)

    # shadow
    draw_tmp.text((base_x_tmp, base_y_tmp + SCALE), text, font=font_big, fill=COLOR_SHADOW_MODE1)

    # testo
    draw_tmp.text((base_x_tmp, base_y_tmp), text, font=font_big, fill=COLOR_TEXT_MODE1)

    # crop
    bbox_tmp = img_tmp.getbbox()
    cropped_big = img_tmp.crop(bbox_tmp)
    w_big, h_big = cropped_big.size

    # stretch fino a pixel 86 (parte da pixel 6)
    max_big_width = (86 - 6) * SCALE

    if w_big > max_big_width:
        stretched_big = cropped_big.resize((max_big_width, h_big), Image.NEAREST)
    else:
        stretched_big = cropped_big

    # canvas finale grande
    img_big = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    img_big.paste(stretched_big, (6 * SCALE, 1), stretched_big)

    # downscale
    img_final = img_big.resize((WIDTH, HEIGHT), Image.NEAREST)
    return img_final


# ============================================================
# MODE2 — 256×32, bianco, outline nera, font diverso e più grande
# ============================================================

def render_mode2(text):
    WIDTH = 256
    HEIGHT = 32

    FONT_PATH = "DejaVuSansCondensed-Bold.ttf"
    FONT_SIZE = 22

    # scala per lavorare in "big" e poi downscale
    big_w = WIDTH * SCALE
    big_h = HEIGHT * SCALE

    font_big = ImageFont.truetype(FONT_PATH, FONT_SIZE * SCALE)

    # outline radius in pixel (sulla canvas grande)
    outline_px = 2 * SCALE

    # calcolo metriche del font per evitare tagli
    ascent, descent = font_big.getmetrics()

    # getbbox sostituisce getsize nelle versioni moderne di Pillow
    bbox = font_big.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]


    # canvas temporanea: larga il doppio per sicurezza, alta quanto serve
    tmp_w = max(big_w * 2, text_width + 4 * outline_px + 10)
    # altezza: ascent + descent + padding per outline e margine
    tmp_h = ascent + descent + 4 * outline_px + 10

    img_tmp = Image.new("RGBA", (int(tmp_w), int(tmp_h)), (0, 0, 0, 0))
    draw_tmp = ImageDraw.Draw(img_tmp)

    # posizionamento orizzontale e verticale calcolati
    base_x_tmp = 1 + outline_px
    # posizioniamo la baseline a ascent + outline + piccolo padding
    base_y_tmp = outline_px + 5

    # disegno outline (2px) attorno al testo
    for ox in range(-outline_px, outline_px + 1, SCALE):
        for oy in range(-outline_px, outline_px + 1, SCALE):
            draw_tmp.text((base_x_tmp + ox, base_y_tmp + oy), text, font=font_big, fill=COLOR_OUTLINE_MODE2)

    # testo principale
    draw_tmp.text((base_x_tmp, base_y_tmp), text, font=font_big, fill=COLOR_TEXT_MODE2)

    # crop al bounding box reale
    bbox_tmp = img_tmp.getbbox()
    if bbox_tmp is None:
        # testo vuoto o invisibile: ritorna canvas vuota
        return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    cropped_big = img_tmp.crop(bbox_tmp)
    w_big, h_big = cropped_big.size

    # stretch solo se supera la larghezza massima
    max_big_width = WIDTH * SCALE
    if w_big > max_big_width:
        stretched_big = cropped_big.resize((max_big_width, h_big), Image.NEAREST)
    else:
        stretched_big = cropped_big

    # canvas finale grande
    img_big = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    # centriamo verticalmente per evitare tagli se c'è spazio extra
    paste_x = 0
    paste_y = max(0, (big_h - stretched_big.size[1]) // 2)
    img_big.paste(stretched_big, (paste_x, paste_y), stretched_big)

    # downscale finale (mantieni NEAREST se vuoi effetto pixel)
    img_final = img_big.resize((WIDTH, HEIGHT), Image.NEAREST)
    return img_final


# ============================================================
# ESEMPIO DI USO
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Renderizza testo nei MODE1/MODE2.")

    parser.add_argument(
        "-t", "--text",
        type=str,
        required=True,
        help="Testo da renderizzare"
    )

    parser.add_argument(
        "-m", "--mode",
        type=int,
        choices=[0, 1, 2],
        required=True,
        help="Modalità di rendering: 0, 1 oppure 2"
    )


    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Percorso del file PNG di output"
    )

    args = parser.parse_args()

    if args.mode == 0:
        img = render_mode0(args.text)
    elif args.mode == 1:
        img = render_mode1(args.text)
    else:
        img = render_mode2(args.text)


    # salvataggio
    img.save(args.output, format="PNG")

    print(f"Salvato {args.output} in MODE{args.mode}.")