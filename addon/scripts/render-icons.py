"""Render the AMO listing icon and a preview sheet from addon/src/icons/icon.svg.

Usage (from addon/):  npm run icons

Outputs (committed, never part of the XPI):
  docs/amo/icon-128.png      the Developer Hub "Add-on icon" upload
  docs/amo/icon-preview.png  the tile at 128/64/32/16 px plus the default workspace
                             icon as groups.js getIconUrl renders it, plain and coloured

Headless Firefox rasterises the SVG as a coverage mask (white glyph on a black page;
its --screenshot has no alpha channel), Pillow draws the tile and composes everything.
Firefox: FIREFOX_BIN env, else the default Windows install path, else `firefox` on PATH.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('Pillow is missing: pip install pillow')

# --- Look of the listing icon (change here, then `npm run icons`) ---
TILE = '#B5552F'        # terracotta rounded square
GLYPH = '#FFF7EC'       # ivory glyph
RADIUS = 28             # corner radius, of 128
GLYPH_FRACTION = 92 / 128  # glyph box size relative to the tile, centred

# --- Preview sheet ---
LIGHT_BG, DARK_BG = '#ffffff', '#2b2a33'
LIGHT_GLYPH, DARK_GLYPH = '#5b5b66', '#fbfbfe'  # the SVG's light-dark() pair
SAMPLE_COLOUR = '#4a90e2'
LABEL = '#8f8f9d'

WORK = 512
OUT = 128
MIN_SHOT = 256
ROOT_FILL = 'fill="context-fill light-dark(#5b5b66,#fbfbfe)"'
PLACEHOLDER = 'transparent'

SCRIPT_DIR = Path(__file__).resolve().parent
SVG_PATH = SCRIPT_DIR.parent / 'src' / 'icons' / 'icon.svg'
OUT_DIR = SCRIPT_DIR.parent.parent / 'docs' / 'amo'
ICON_PATH = OUT_DIR / 'icon-128.png'
PREVIEW_PATH = OUT_DIR / 'icon-preview.png'

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
html, body {{ margin: 0; background: #000; overflow: hidden; }}
svg {{ display: block; width: {size}px; height: {size}px; }}
</style></head><body>
{svg}
</body></html>
"""


def fail(message):
    sys.exit(f'render-icons: {message}')


def find_firefox():
    env = os.environ.get('FIREFOX_BIN')
    if env:
        if not Path(env).is_file():
            fail(f'FIREFOX_BIN does not exist: {env}')
        return env
    default = Path(r'C:\Program Files\Mozilla Firefox\firefox.exe')
    if default.is_file():
        return str(default)
    found = shutil.which('firefox')
    if found:
        return found
    fail('Firefox not found: set FIREFOX_BIN')


def shoot(firefox, svg_text, tmp, name):
    """Render svg_text white-on-black at WORK px; return an 'L' coverage mask of WORK x WORK."""
    page = tmp / f'{name}.html'
    page.write_text(PAGE.format(size=WORK, svg=svg_text), encoding='utf-8')
    shot = tmp / f'{name}.png'
    profile = tmp / f'profile-{name}'
    profile.mkdir()
    cmd = [firefox, '-headless', '-no-remote', '-profile', str(profile),
           f'-window-size={WORK},{WORK}', '-screenshot', str(shot), page.as_uri()]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=60)
    except subprocess.TimeoutExpired as e:
        fail(f'Firefox timed out after 60 s; close every Firefox and retry.\n{e.stdout or ""}{e.stderr or ""}')
    output = (proc.stdout or '') + (proc.stderr or '')
    # Firefox prints "Screenshot saved to:" on POSIX; on Windows that line never reaches the pipe
    # (verified on Firefox 156), so the file written into the fresh temp dir is the success signal.
    if not shot.is_file():
        fail(f'Firefox did not save a screenshot (exit {proc.returncode}):\n{output}')

    with Image.open(shot) as im:
        im.load()
        size = im.size
        mask = im.convert('L')
    w, h = size
    if w != h:
        side = min(w, h)
        print(f'render-icons: {name} shot is {w}x{h}, not square; cropping to its top-left {side}x{side}')
        mask = mask.crop((0, 0, side, side))
    if mask.width < MIN_SHOT:
        fail(f'{name} shot is {mask.width}px, smaller than {MIN_SHOT}px')
    if mask.width != WORK:
        mask = mask.resize((WORK, WORK), Image.LANCZOS)
    return mask, size


def colour_through(mask, colour):
    """A WORK-size RGBA layer: `colour` with the mask as its alpha."""
    layer = Image.new('RGBA', mask.size, colour)
    layer.putalpha(mask)
    return layer


def make_tile(glyph_mask):
    tile = Image.new('RGBA', (WORK, WORK), (0, 0, 0, 0))
    scale = WORK / OUT
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, WORK - 1, WORK - 1), radius=round(RADIUS * scale), fill=TILE)
    box = round(WORK * GLYPH_FRACTION)
    offset = (WORK - box) // 2
    glyph = colour_through(glyph_mask.resize((box, box), Image.LANCZOS), GLYPH)
    tile.alpha_composite(glyph, (offset, offset))
    return tile.resize((OUT, OUT), Image.LANCZOS)


def make_default_icon(glyph_mask, plate_mask, glyph_colour, sample, size):
    """The 'main-squares' workspace icon as getIconUrl renders it, at `size` px."""
    icon = colour_through(glyph_mask, glyph_colour)
    if sample:
        icon.alpha_composite(colour_through(plate_mask, sample))
    return icon.resize((size, size), Image.LANCZOS)


def make_preview(tile, glyph_mask, plate_mask):
    font = ImageFont.load_default()
    width, row_h, pad = 760, 180, 20
    sheet = Image.new('RGBA', (width, row_h * 2), LIGHT_BG)
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, row_h, width, row_h * 2), fill=DARK_BG)

    for row, glyph_colour in enumerate((LIGHT_GLYPH, DARK_GLYPH)):
        top = row * row_h + pad
        base = top + 128  # images sit on a common baseline
        x = pad
        for size in (128, 64, 32, 16):
            img = tile if size == OUT else tile.resize((size, size), Image.LANCZOS)
            sheet.alpha_composite(img, (x, base - size))
            draw.text((x, base + 8), f'{size}', fill=LABEL, font=font)
            x += size + 28
        x += 24
        for sample, label in ((None, 'plain'), (SAMPLE_COLOUR, 'colour')):
            draw.text((x, base - 56), f'workspace {label}', fill=LABEL, font=font)
            for size in (32, 16):
                icon = make_default_icon(glyph_mask, plate_mask, glyph_colour, sample, size)
                sheet.alpha_composite(icon, (x, base - size))
                draw.text((x, base + 8), f'{size}', fill=LABEL, font=font)
                x += size + 28
            x += 20
    return sheet


def check_icon(icon):
    checks = {(0, 0): 0, (64, 8): 255, (64, 64): 255}
    for xy, want in checks.items():
        got = icon.getpixel(xy)[3]
        if got != want:
            fail(f'icon-128.png pixel {xy} has alpha {got}, expected {want}')


def main():
    svg = SVG_PATH.read_text(encoding='utf-8')
    if svg.count(ROOT_FILL) != 1:
        fail(f'{SVG_PATH.name}: expected the root attribute {ROOT_FILL} exactly once, found {svg.count(ROOT_FILL)}')
    if svg.count(PLACEHOLDER) != 1:
        fail(f'{SVG_PATH.name}: expected the word "{PLACEHOLDER}" exactly once (getIconUrl replaces the first), '
             f'found {svg.count(PLACEHOLDER)}')

    firefox = find_firefox()
    tmp = Path(tempfile.mkdtemp(prefix='strata-icon-'))
    try:
        glyph_mask, shot_size = shoot(firefox, svg.replace(ROOT_FILL, 'fill="#fff"'), tmp, 'glyph')
        plate_svg = svg.replace(ROOT_FILL, 'fill="#000"').replace(PLACEHOLDER, '#fff', 1)
        plate_mask, _ = shoot(firefox, plate_svg, tmp, 'plate')
    finally:
        for _ in range(10):
            try:
                shutil.rmtree(tmp)
                break
            except OSError:
                time.sleep(0.5)
        else:
            print(f'render-icons: could not delete {tmp}', file=sys.stderr)

    icon = make_tile(glyph_mask)
    check_icon(icon)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    icon.save(ICON_PATH)
    make_preview(icon, glyph_mask, plate_mask).save(PREVIEW_PATH)

    print(f'shot size: {shot_size[0]}x{shot_size[1]}')
    print(ICON_PATH)
    print(PREVIEW_PATH)


if __name__ == '__main__':
    main()
