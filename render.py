# Render entry.png: one hero ingredient — ripe strawberries, glistening.
# Drawn procedurally with PIL (supersampled 2x, downscaled to 1024x1024).
# No text, no hands, one ingredient only. Deterministic (fixed seed).
import math
import random
from PIL import Image, ImageDraw, ImageFilter

random.seed(7)
SS = 2
W = H = 1024 * SS
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img, "RGBA")


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---- warm wooden-table background: vertical gradient + plank bands ----
top_c, mid_c, bot_c = (255, 205, 140), (214, 148, 84), (96, 50, 24)
for y in range(H):
    t = y / H
    c = lerp(top_c, mid_c, t) if t < 0.55 else lerp(mid_c, bot_c, (t - 0.55) / 0.45)
    d.line([(0, y), (W, y)], fill=c)
# soft plank seams
for fy in (0.30, 0.62, 0.90):
    y = int(H * fy)
    d.line([(0, y), (W, y)], fill=(70, 38, 18, 90), width=3 * SS)
    d.line([(0, y + 3 * SS), (W, y + 3 * SS)], fill=(255, 220, 160, 40), width=2 * SS)
# warm bokeh light spots, top corners
for (bx, by, br, al) in [(0.12, 0.10, 0.16, 46), (0.88, 0.07, 0.13, 40),
                         (0.95, 0.30, 0.09, 30), (0.05, 0.42, 0.08, 26)]:
    d.ellipse([W * (bx - br), H * (by - br * 0.8), W * (bx + br), H * (by + br * 0.8)],
              fill=(255, 230, 170, al))
# gentle light pool behind the plate
d.ellipse([W * 0.08, H * 0.30, W * 0.92, H * 0.95], fill=(255, 225, 165, 34))

# ---- ceramic plate ----
pcx, pcy, prx, pry = W * 0.50, H * 0.66, W * 0.44, H * 0.315
d.ellipse([pcx - prx, pcy - pry + 10 * SS, pcx + prx, pcy + pry + 10 * SS],
          fill=(60, 30, 14, 110))  # plate shadow on table
d.ellipse([pcx - prx, pcy - pry, pcx + prx, pcy + pry], fill=(250, 244, 230))
d.ellipse([pcx - prx * 0.86, pcy - pry * 0.86, pcx + prx * 0.86, pcy + pry * 0.86],
          fill=(244, 232, 210))
d.ellipse([pcx - prx * 0.86, pcy - pry * 0.86, pcx + prx * 0.86, pcy + pry * 0.86],
          outline=(214, 190, 158, 255), width=3 * SS)


def half_width(v, s):
    """Half-width of the strawberry body at fraction v (0=top, 1=bottom tip)."""
    return 0.60 * s * (math.sin(math.pi * (0.06 + 0.94 * v)) ** 0.8)


def berry_points(cx, cy, s, rot_deg, n=160):
    """Rounded-top, tapering body: top at cy-0.55s, tip at cy+0.95s."""
    rot = math.radians(rot_deg)
    pts = []
    for i in range(n + 1):
        v = i / n
        y = cy - 0.55 * s + v * 1.50 * s
        hw = half_width(v, s)
        x = cx + hw
        xr = (x - cx) * math.cos(rot) - (y - cy) * math.sin(rot)
        yr = (x - cx) * math.sin(rot) + (y - cy) * math.cos(rot)
        pts.append((cx + xr, cy + yr))
    for i in range(n, -1, -1):
        v = i / n
        y = cy - 0.55 * s + v * 1.50 * s
        hw = half_width(v, s)
        x = cx - hw
        xr = (x - cx) * math.cos(rot) - (y - cy) * math.sin(rot)
        yr = (x - cx) * math.sin(rot) + (y - cy) * math.cos(rot)
        pts.append((cx + xr, cy + yr))
    return pts


def point_in_poly(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_strawberry(cx, cy, s, rot=0, droplets=True):
    # soft contact shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([cx - s * 0.75, cy + s * 0.55, cx + s * 0.75, cy + s * 0.95],
               fill=(40, 16, 8, 110))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh.filter(
        ImageFilter.GaussianBlur(14 * SS)).convert("RGBA")).convert("RGB"), (0, 0))

    poly = berry_points(cx, cy, s, rot)
    # gradient body through mask
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for yy in range(int(cy - s), int(cy + s) + 1):
        t = (yy - (cy - s)) / (2 * s)
        c = lerp((255, 88, 66), (222, 32, 40), t) if t < 0.5 else lerp((222, 32, 40), (148, 8, 22), (t - 0.5) * 2)
        gd.line([(0, yy), (W, yy)], fill=c)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img, "RGBA")
    # soft shade on the right edge (outside the body, blurred)
    cres = Image.new("L", (W, H), 0)
    dc = ImageDraw.Draw(cres)
    dc.ellipse([cx - s * 0.2, cy - s * 0.95, cx + s * 1.15, cy + s * 1.0], fill=255)
    dc.polygon(poly, fill=0)
    cres = cres.filter(ImageFilter.GaussianBlur(16 * SS))
    dark = Image.new("RGBA", (W, H), (90, 0, 8, 38))
    img.paste(Image.alpha_composite(img.convert("RGBA"), Image.composite(
        dark, Image.new("RGBA", (W, H), (0, 0, 0, 0)), cres)).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # seeds: rows of pale achenes inside the body
    for row in range(8):
        fy = -0.45 + row * 0.17
        yy = cy + fy * s
        v = (fy + 0.55) / 1.50
        half = half_width(max(0.0, min(1.0, v)), s) * 0.92
        if half < s * 0.08:
            continue
        nseed = max(2, int(half / (s * 0.15)))
        for k in range(nseed):
            fx = -half + (2 * half) * (k + 0.5) / nseed + random.uniform(-4, 4) * SS
            rr = math.radians(rot)
            sx = cx + fx * math.cos(rr) - (yy - cy) * math.sin(rr) * 0.15
            sy = cy + (yy - cy) * math.cos(rr) + fx * math.sin(rr) * 0.15
            if not point_in_poly(sx, sy, poly):
                continue
            sw, sh2 = 7.5 * SS * (s / (300 * SS)), 11 * SS * (s / (300 * SS))
            d.ellipse([sx - sw / 2, sy - sh2 / 2, sx + sw / 2, sy + sh2 / 2],
                      fill=(120, 20, 18, 160))  # pit
            d.ellipse([sx - sw / 2, sy - sh2 / 2 - 2 * SS, sx + sw / 2, sy + sh2 / 2 - 2 * SS],
                      fill=(255, 236, 175))  # seed
            d.ellipse([sx - sw / 4, sy - sh2 / 2 - 2 * SS, sx + sw / 6, sy - sh2 / 6],
                      fill=(255, 250, 220))
    # glossy highlight, upper left (soft round blob, stays in upper half)
    hi = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dh = ImageDraw.Draw(hi)
    dh.ellipse([cx - s * 0.55, cy - s * 0.75, cx + s * 0.10, cy - s * 0.28],
               fill=(255, 255, 255, 48))
    img.paste(Image.alpha_composite(img.convert("RGBA"), hi.filter(
        ImageFilter.GaussianBlur(22 * SS)).convert("RGBA")).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # juice droplets
    if droplets:
        for _ in range(9):
            ang = random.uniform(-1.1, 1.1)
            rr2 = random.uniform(0.25, 0.75)
            dx = cx + math.sin(ang) * rr2 * s * 0.75
            dy = cy + math.cos(ang) * rr2 * s * 0.7 - s * 0.1
            if not point_in_poly(dx, dy, poly):
                continue
            r = random.uniform(5, 10) * SS
            d.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(255, 255, 255, 110))
            d.ellipse([dx - r * 0.45, dy - r * 0.55, dx + r * 0.25, dy + r * 0.15],
                      fill=(255, 255, 255, 220))
    # green calyx: pointed leaves fanning from the stem, ON the berry top
    top_y = cy - s * 0.55
    for la in (-52, -30, -10, 12, 34, 56):
        a = math.radians(la + rot * 0.4 - 90)
        tipx = cx + math.cos(a) * s * 0.34
        tipy = top_y + math.sin(a) * s * 0.30
        base = s * 0.10
        px = math.cos(a + math.pi / 2) * base
        py = math.sin(a + math.pi / 2) * base
        col = (46, 128, 52) if la % 2 == 0 else (74, 164, 74)
        d.polygon([(cx - px, top_y - py), (tipx, tipy), (cx + px, top_y + py)], fill=col)
    d.ellipse([cx - s * 0.09, top_y - s * 0.06, cx + s * 0.09, top_y + s * 0.06],
              fill=(34, 96, 40))
    # stem
    d.line([(cx, top_y - s * 0.02), (cx + s * 0.05, top_y - s * 0.20)],
           fill=(96, 130, 60), width=6 * SS)


def draw_half(cx, cy, s, rot=18):
    """A halved strawberry, cut face up: juicy pink flesh, seeds, white core."""
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - s * 0.8, cy + s * 0.5, cx + s * 0.8, cy + s * 0.9],
                               fill=(40, 16, 8, 110))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh.filter(
        ImageFilter.GaussianBlur(12 * SS)).convert("RGBA")).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # skin rim
    d.ellipse([cx - s, cy - s * 0.82, cx + s, cy + s * 0.82], fill=(196, 22, 34))
    # flesh with radial gradient (concentric ellipses)
    for i in range(28, 0, -1):
        t = i / 28
        c = lerp((255, 158, 168), (232, 74, 96), 1 - t)
        d.ellipse([cx - s * 0.94 * t, cy - s * 0.76 * t, cx + s * 0.94 * t, cy + s * 0.76 * t],
                  fill=c)
    # pale core star
    d.ellipse([cx - s * 0.30, cy - s * 0.24, cx + s * 0.30, cy + s * 0.24],
              fill=(255, 228, 222))
    d.ellipse([cx - s * 0.16, cy - s * 0.13, cx + s * 0.16, cy + s * 0.13],
              fill=(255, 244, 238))
    # seeds ring in the flesh
    for k in range(12):
        a = 2 * math.pi * k / 12 + 0.3
        sx = cx + math.cos(a) * s * 0.62
        sy = cy + math.sin(a) * s * 0.50
        d.ellipse([sx - 5 * SS, sy - 7 * SS, sx + 5 * SS, sy + 7 * SS],
                  fill=(255, 240, 190))
    # gloss streaks: wet, juicy
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(gl)
    dg.ellipse([cx - s * 0.7, cy - s * 0.65, cx - s * 0.1, cy - s * 0.25],
               fill=(255, 255, 255, 90))
    dg.ellipse([cx + s * 0.15, cy + s * 0.1, cx + s * 0.55, cy + s * 0.45],
               fill=(255, 255, 255, 60))
    img.paste(Image.alpha_composite(img.convert("RGBA"), gl.filter(
        ImageFilter.GaussianBlur(10 * SS)).convert("RGBA")).convert("RGB"), (0, 0))


# ---- composition: three whole berries + one glistening half ----
draw_strawberry(W * 0.335, H * 0.475, 300 * SS, rot=-14)
draw_strawberry(W * 0.665, H * 0.44, 285 * SS, rot=12)
draw_strawberry(W * 0.50, H * 0.335, 205 * SS, rot=4, droplets=False)
draw_half(W * 0.60, H * 0.72, 185 * SS)

# ---- warm vignette + final grade ----
img = img.resize((1024, 1024), Image.LANCZOS)
vig = Image.new("L", (1024, 1024), 0)
dv = ImageDraw.Draw(vig)
dv.ellipse([-220, -220, 1244, 1244], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(180))
black = Image.new("RGB", (1024, 1024), (46, 18, 6))
img = Image.composite(img, black, vig.point(lambda p: 255 - int((255 - p) * 0.28)))
img.save("entry.png", optimize=True)
print("saved entry.png")
