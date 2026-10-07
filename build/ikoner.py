"""Ritar appens ikoner: fyra rutor i passens färger på mörk botten.

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
# Samma färger som passen i style.css: förmiddag, eftermiddag, helgpass dag, natt.
RUTOR = ["#ffd166", "#e8833a", "#7cc4b8", "#2e3a66"]
KANT = "#7b88b5"   # ljus kant runt den mörka nattrutan, så att den syns mot botten

RITYTA = 1024      # ritas stort och förminskas, så att kanterna blir mjuka


def rita(marginal):
    """Ikonen i full storlek. marginal är luften runt rutorna, som andel av sidan."""
    bild = Image.new("RGB", (RITYTA, RITYTA), BOTTEN)
    penna = ImageDraw.Draw(bild)
    yta = RITYTA * (1 - 2 * marginal)
    mellanrum = yta * 0.07
    sida = (yta - mellanrum) / 2
    start = RITYTA * marginal
    for nummer, farg in enumerate(RUTOR):
        x = start + (nummer % 2) * (sida + mellanrum)
        y = start + (nummer // 2) * (sida + mellanrum)
        kant = KANT if farg == RUTOR[3] else None
        penna.rounded_rectangle([x, y, x + sida, y + sida], radius=sida * 0.22,
                                fill=farg, outline=kant, width=round(sida * 0.045))
    return bild


def spara(bild, namn, storlek):
    bild.resize((storlek, storlek), Image.LANCZOS).save(os.path.join(ROT, namn), optimize=True)
    print(namn)


def main():
    vanlig = rita(0.145)
    spara(vanlig, "favicon.png", 32)
    spara(vanlig, "apple-touch-icon.png", 180)
    spara(vanlig, "icon-192.png", 192)
    spara(vanlig, "icon-512.png", 512)
    # Android kan beskära ikonen till en cirkel. Då måste motivet ligga i mitten.
    spara(rita(0.24), "icon-maskable-512.png", 512)


if __name__ == "__main__":
    main()
