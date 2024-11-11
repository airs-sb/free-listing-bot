# Thank you Poke for the renderer
# https://github.com/poke5352

from PIL import Image, ImageDraw, ImageFont
import os
import string

text_colors = {"0": ["black", (0, 0, 0)], "1": ["dark blue", (0, 0, 170)], "2": ["dark green", (0, 170, 0)], "3": ["dark aqua", (0, 170, 170)], "4": ["dark red", (170, 0, 0)], "5": ["dark purple", (170, 0, 170)], "6": ["gold", (255, 170, 0)], "7": ["gray", (170, 170, 170)], "8": [
                               "dark_gray", (85, 85, 85)], "9": ["blue", (85, 85, 255)], "a": ["green", (85, 255, 85)], "b": ["aqua", (85, 255, 255)], "c": ["red", (255, 85, 85)], "d": ["light purple", (255, 85, 255)], "e": ["yellow", (255, 255, 85)], "f": ["white", (255, 255, 255)]}
shadow_colors = {"0": ["black", (0, 0, 0)], "1": ["dark blue", (0, 0, 42)], "2": ["dark green", (0, 42, 0)], "3": ["dark aqua", (0, 42, 42)], "4": ["dark red", (42, 0, 0)], "5": ["dark purple", (42, 0, 42)], "6": ["gold", (42, 42, 0)], "7": ["gray", (42, 42, 42)], "8": [
                                 "dark_gray", (21, 21, 21)], "9": ["blue", (21, 21, 63)], "a": ["green", (21, 63, 21)], "b": ["aqua", (21, 63, 63)], "c": ["red", (63, 21, 21)], "d": ["light purple", (63, 21, 63)], "e": ["yellow", (63, 63, 21)], "f": ["white", (63, 63, 63)]}
dir_path = os.path.dirname(os.path.realpath(__file__))
letters = string.ascii_letters


def draw_italics(char, x, y, width, height, background, fnt, color):
    """
    Creates a new image and imprints the character on the new image and modifies it
    Image is then copied onto the original image
    """
    foreground = Image.new('RGBA', (width, height))
    foreground_draw = ImageDraw.Draw(foreground)

    size = fnt.getsize(char)[0]
    foreground_draw.text((x, y), char, font=fnt, fill=color)

    region = foreground.crop((x, y+2, size+x, y+4))
    foreground_draw.rectangle((x, y+2, size+x, y+3),
                              outline=(0, 0, 0), fill=(0, 0, 0))
    foreground.paste(region, (x+2, y+2))

    region = foreground.crop((x, y+4, size+x, y+6))
    foreground_draw.rectangle((x, y+4, size+x, y+5),
                              outline=(0, 0, 0), fill=(0, 0, 0))
    foreground.paste(region, (x+1, y+4))

    region = foreground.crop((x, y+6, size+x, y+8))
    foreground_draw.rectangle((x, y+6, size+x, y+7),
                              outline=(0, 0, 0), fill=(0, 0, 0))
    foreground.paste(region, (x+1, y+6))


    region = foreground.crop((x, y+12, size+x, y+16))
    foreground_draw.rectangle((x, y+12, size+x, y+15),
                              outline=(0, 0, 0), fill=(0, 0, 0))
    foreground.paste(region, (x-1, y+12))

    region = foreground.crop((x, y+16, size+x, y+19))
    foreground_draw.rectangle((x, y+16, size+x, y+18),
                              outline=(0, 0, 0), fill=(0, 0, 0))
    foreground.paste(region, (x-2, y+16))

    background.paste(foreground, (0, 0), foreground)
    return background

def render(lore_lines):
    lore_lines.insert(1, [])
    processed_lines = []

    for line in lore_lines:
        special_character = False
        code_character = False
        bolded = False
        italics = False
        strikethrough = False
        shadow_color = (63, 63, 63)
        color = (255, 255, 255)
        if line == "":
            processed_lines.append([])
        else:
            lore_location = len(processed_lines)
            processed_lines.append([])

            for char in line:
                if ord(char) > 127:
                    special_character = True
                if char == '️':
                    special_character = False
                elif char == "&":
                    code_character = True
                elif code_character is True:
                    code_character = False
                    if char in text_colors:
                        color = text_colors[char][1]
                        shadow_color = shadow_colors[char][1]
                    elif char == "r":
                        color = (255, 255, 255)
                        italics = False
                        bolded = False
                    elif char == "l":
                        bolded = True
                    elif char == "o":
                        italics = True
                else:
                    processed_lines[lore_location].append(
                        [char, color, bolded, italics, special_character, shadow_color])
                    special_character = False

    width = 0
    height = 18 + 24 + 20 + 14 + ((len(processed_lines)-4)*20)
    x = 8
    for line in processed_lines:
        if line == []:
            pass
        else:
            for char in line:
                if char[2] is True:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/MinecraftBold.otf", 20)
                else:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/MinecraftRegular.otf", 20)
                if char[4] is True:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/unifont.ttf", 16)
                if char[0] == " ":
                    size = 10
                    x = size + x
                else:
                    size = fnt.getsize(char[0])[0]
                    x = size + x
            if x > width:
                width = x + 10
            x = 8


    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    x = 8
    line_number = 0
    for line in processed_lines:
        line_number = line_number + 1
        if not line == []:
            for char in line:
                if char[2] is True:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/MinecraftBold.otf", 20)
                else:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/MinecraftRegular.otf", 20)
                color = char[5]
                if char[4] is True:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/unifont.ttf", 16)
                    if line_number == 1:
                        draw.text((x, 8), char[0], font=fnt, fill=color)
                    else:
                        draw.text(
                            (x, 25+((line_number-2)*7+(13*(line_number-3)))), char[0], font=fnt, fill=color)
                else:
                    if char[3] is True:
                        if line_number == 1:
                            img = draw_italics(
                                char[0], x+2, 8, width, height, img, fnt, color)
                        else:
                            img = draw_italics(
                                char[0], x+2, 25+((line_number-2)*7+(13*(line_number-3))), width, height, img, fnt, color)

                    else:
                        if line_number == 1:
                            draw.text((x+2, 8), char[0], font=fnt, fill=color)
                        else:
                            draw.text(
                                (x+2, 25+((line_number-2)*7+(13*(line_number-3)))), char[0], font=fnt, fill=color)

                if char[0] == " ":
                    if char[2] is True:
                        size = 10
                    else:
                        size = 8
                    x = size + x
                else:
                    size = fnt.getsize(char[0])[0]
                    x = size + x
            x = 8

    x = 8
    line_number = 0
    for line in processed_lines:
        line_number = line_number + 1
        if not line == []:
            for char in line:
                if char[2] is True:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/MinecraftBold.otf", 20)
                else:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/MinecraftRegular.otf", 20)
                color = char[1]
                if char[4] is True:
                    fnt = ImageFont.truetype(
                        dir_path + "/fonts/unifont.ttf", 16)
                    if line_number == 1:
                        draw.text((x, 8), char[0], font=fnt, fill=color)
                    else:
                        draw.text(
                            (x, 25+((line_number-2)*7+(13*(line_number-3)))), char[0], font=fnt, fill=color)
                else:
                    if char[3] is True:
                        if line_number == 1:
                            img = draw_italics(
                                char[0], x, 6, width, height, img, fnt, color)
                        else:
                            img = draw_italics(
                                char[0], x, 23+((line_number-2)*7+(13*(line_number-3))), width, height, img, fnt, color)

                    else:
                        if line_number == 1:
                            draw.text((x, 6), char[0], font=fnt, fill=color)
                        else:
                            draw.text(
                                (x, 23+((line_number-2)*7+(13*(line_number-3)))), char[0], font=fnt, fill=color)

                if char[0] == " ":
                    if char[2] is True:
                        size = 10
                    else:
                        size = 8
                    x = size + x
                else:
                    size = fnt.getsize(char[0])[0]
                    x = size + x
            x = 8

    return img
