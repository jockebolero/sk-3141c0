"""Ritar appens ikoner: nio rutor på mörk botten, som ett utsnitt av månadsvyn
i appen. Sju rutor har passens färger, två är lediga dagar.

Gjord av J. Stork.

Skriver till repots rot:
    favicon.png              32 px, webbläsarens flik
    apple-touch-icon.png     180 px, hemskärmen på iPhone
    icon-192.png             192 px, hemskärmen på Android
    icon-512.png             512 px, startbilden på Android
    icon-maskable-512.png    512 px med extra luft, när Android beskär ikonen

Behöver bara köras om ikonen ska ändras. Kräver Pillow:
    pip install pillow
    python3 build/ikoner.py
"""
import os

from PIL import Image, ImageDraw

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOTTEN = "#16202e"
# Rutorna rad för rad, som i månadsvyn. Samma färger som passen i style.css,
# utom natt som är ljusare (#5b6bb0 i stället för #2e3a66) för att ha minst 3:1
# mot botten. Lediga dagar är medvetet svaga: de är bakgrund, inte information.
FM, EM, HD, N, HN = "#ffd166", "#e8833a", "#7cc4b8", "#5b6bb0", "#2f7d77"
LEDIG = "#2c3745"
RUTOR = [FM, EM, N,
         LEDIG, FM, EM,
         HD, LEDIG, HN]
KOLUMNER = 3

RITYTA = 1024      # ritas stort och förminskas, så att kanterna blir mjuka


def rita(marginal):
    """Ikonen i full storlek. marginal är luften runt rutorna, som andel av sidan."""
    bild = Image.new("RGB", (RITYTA, RITYTA), BOTTEN)
    penna = ImageDraw.Draw(bild)
    yta = RITYTA * (1 - 2 * marginal)
    mellanrum = yta * 0.066
    sida = (yta - mellanrum * (KOLUMNER - 1)) / KOLUMNER
    start = RITYTA * marginal
    for nummer, farg in enumerate(RUTOR):
        x = start + (nummer % KOLUMNER) * (sida + mellanrum)
        y = start + (nummer // KOLUMNER) * (sida + mellanrum)
        penna.rounded_rectangle([x, y, x + sida, y + sida], radius=sida * 0.2, fill=farg)
    return bild


def spara(bild, namn, storlek):
    bild.resize((storlek, storlek), Image.LANCZOS).save(os.path.join(ROT, namn), optimize=True)
    print(namn)


def main():
    vanlig = rita(0.16)
    spara(vanlig, "favicon.png", 32)
    spara(vanlig, "apple-touch-icon.png", 180)
    spara(vanlig, "icon-192.png", 192)
    spara(vanlig, "icon-512.png", 512)
    # Android kan beskära ikonen till en cirkel. Då måste motivet ligga i mitten.
    spara(rita(0.235), "icon-maskable-512.png", 512)


if __name__ == "__main__":
    main()
