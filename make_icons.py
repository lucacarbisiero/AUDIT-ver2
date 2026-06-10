# -*- coding: utf-8 -*-
"""Icone PWA per Audit Energetico (brand fbc: viola + teal, lente con mini-bar-chart)."""
import math
from PIL import Image, ImageDraw, ImageFilter

SS = 4
MASTER = 512 * SS

# brand fbc
TOP    = (149, 117, 205)   # viola chiaro (#9575CD)
BOTTOM = (74,  46, 165)    # viola scuro  (#4A2EA5)
TEAL   = (0,   214, 150)   # accento verde/teal (#00D696)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def diagonal_gradient(size, c1, c2):
    g = Image.new("RGB", (size, size)); px = g.load(); md = (size - 1) * 2
    for y in range(size):
        for x in range(size):
            px[x, y] = lerp(c1, c2, (x + y) / md)
    return g

def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m

def build_master():
    S = MASTER
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # sfondo viola + angoli arrotondati
    mask = rounded_mask(S, int(S * 0.235))
    img.paste(diagonal_gradient(S, TOP, BOTTOM).convert("RGBA"), (0, 0), mask)

    # highlight morbido alto-sx
    gloss = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).ellipse([-S*0.45, -S*0.75, S*0.85, S*0.30], fill=(255, 255, 255, 55))
    gloss = gloss.filter(ImageFilter.GaussianBlur(S * 0.10))
    img = Image.alpha_composite(img, Image.composite(gloss, Image.new("RGBA", (S, S), (0,0,0,0)), mask))

    # ---- lente d'ingrandimento ----
    cx, cy = 0.445 * S, 0.420 * S
    outer  = 0.205 * S
    ring   = 0.060 * S
    white  = (255, 255, 255, 255)

    # ombra morbida della lente
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    off = int(S * 0.012)
    sd.ellipse([cx-outer+off, cy-outer+off, cx+outer+off, cy+outer+off], outline=(40,20,90,150), width=int(ring))
    ang = math.radians(45)
    hx1, hy1 = cx + (outer-ring*0.2)*math.cos(ang), cy + (outer-ring*0.2)*math.sin(ang)
    hx2, hy2 = cx + 0.36*S*math.cos(ang), cy + 0.36*S*math.sin(ang)
    sd.line([hx1+off, hy1+off, hx2+off, hy2+off], fill=(40,20,90,150), width=int(0.085*S))
    sh = sh.filter(ImageFilter.GaussianBlur(S * 0.018))
    img = Image.alpha_composite(img, sh)

    # manico (sotto l'anello), con cap arrotondati
    glass = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glass)
    hw = int(0.085 * S)
    gd.line([hx1, hy1, hx2, hy2], fill=white, width=hw)
    r = hw // 2
    gd.ellipse([hx2-r, hy2-r, hx2+r, hy2+r], fill=white)

    # mini bar-chart teal dentro la lente
    bars = [(-0.085, 0.075), (0.0, 0.120), (0.085, 0.165)]  # (dx in S, altezza in S)
    bw = 0.045 * S
    base = cy + 0.085 * S
    for dx, h in bars:
        x = cx + dx * S
        gd.rounded_rectangle([x-bw/2, base-h*S, x+bw/2, base], radius=bw*0.35, fill=TEAL + (255,))

    # anello della lente (sopra le barre)
    gd.ellipse([cx-outer, cy-outer, cx+outer, cy+outer], outline=white, width=int(ring))

    img = Image.alpha_composite(img, glass)
    return img

def main():
    master = build_master()
    for out in (512, 192):
        master.resize((out, out), Image.LANCZOS).save(f"icona-{out}.png")
        print("scritto icona-%d.png" % out)

if __name__ == "__main__":
    main()
