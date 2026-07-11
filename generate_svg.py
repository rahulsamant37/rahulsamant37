"""
Generate dark_mode.svg and light_mode.svg with high-fidelity ASCII art portrait.

Uses m3-passport-size.png (well-lit, white bg, centered face, square crop).
Matches Andrew6rant's SVG layout exactly — 985x530px, Consolas monospace, 
ASCII art on left, neofetch-style info on right.
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import sys

# Two ramps depending on the SVG background:
#
# DARK SVG (light text on dark bg):
#   - Dark pixels in photo (hair, glasses, eyebrows) → DENSE chars that show up bright
#   - Light pixels in photo (background, shirt, skin highlights) → SPARSE/space chars
#
# LIGHT SVG (dark text on light bg):
#   - Dark pixels in photo → DENSE chars (they print dark)
#   - Light pixels in photo → SPARSE/space chars
#
# So for BOTH modes we want: dark photo pixel → dense char, light photo pixel → space.
# This is the "standard" mapping (darkest pixel = densest char).
CHAR_RAMP = "@%#MW&8B$QODHEXZAUJTYLCG0Pmbdpqwkheaonsxzjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

ASCII_WIDTH  = 42   # characters wide  (fits ~390px at 16px Consolas)
ASCII_HEIGHT = 25   # lines tall       (fits ~530px at 20px line spacing)


def image_to_ascii(image_path, width=ASCII_WIDTH, height=ASCII_HEIGHT):
    """
    Convert a well-lit headshot with light background to ASCII art.
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    # 1) For passport-size photo, crop to upper 85% (head + shoulders, skip bottom)
    #    and center horizontally
    crop_top    = 0
    crop_bottom = int(h * 0.88)
    crop_left   = int(w * 0.05)
    crop_right  = int(w * 0.95)
    img = img.crop((crop_left, crop_top, crop_right, crop_bottom))

    # 2) Resize to ASCII grid (accounting for monospace char aspect ratio ~0.5)
    img = img.resize((width, height), Image.LANCZOS)

    # 3) Enhance contrast and sharpness for edge definition
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)

    # 4) Convert to grayscale
    gray = img.convert("L")
    gray_arr = np.array(gray, dtype=np.float64)

    # 5) Edge detection — emphasize glasses frames, hair outline, facial features
    edge_img = gray.filter(ImageFilter.Kernel(
        size=(3, 3),
        kernel=[-1, -1, -1, -1, 8, -1, -1, -1, -1],
        scale=1, offset=128
    ))
    edge_arr = np.array(edge_img, dtype=np.float64) - 128.0

    # Darken pixels where edges are strong (makes outlines sharper in ASCII)
    blended = gray_arr - np.abs(edge_arr) * 0.35
    blended = np.clip(blended, 0, 255)

    # 6) Auto-levels: stretch to full 0-255 range
    lo = np.percentile(blended, 2)
    hi = np.percentile(blended, 98)
    if hi > lo:
        blended = (blended - lo) / (hi - lo) * 255.0
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    # 7) Invert: we want dark pixels (hair, glasses) → index 0 (dense chars like @)
    #    and light pixels (background) → last index (space)
    #    Since grayscale 0=black=dark and our ramp[0]=@ is dense, this is the NATURAL mapping.
    #    No inversion needed!

    # 8) Map to characters
    ramp_len = len(CHAR_RAMP)
    lines = []
    for y in range(height):
        line = ""
        for x in range(width):
            pixel = blended[y, x]
            idx = min(int(pixel / 256 * ramp_len), ramp_len - 1)
            line += CHAR_RAMP[idx]
        lines.append(line)

    return lines


def escape_xml(s):
    """Escape XML special characters."""
    return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;"))


def generate_svg(ascii_lines, mode="dark"):
    """
    Generate SVG matching Andrew6rant's exact layout:
    - 985x530px canvas
    - ASCII art at x=15 (left panel, ~42 chars)
    - Info text at x=390 (right panel)
    - 16px Consolas monospace font
    - 20px line spacing (y increments)
    """
    if mode == "dark":
        bg, fg       = "#161b22", "#c9d1d9"
        key, val, cc = "#ffa657", "#a5d6ff", "#616e7f"
        add_c, del_c = "#3fb950", "#f85149"
    else:
        bg, fg       = "#ffffff", "#24292f"
        key, val, cc = "#0550ae", "#0a3069", "#6e7781"
        add_c, del_c = "#1a7f37", "#cf222e"

    # Build ASCII art tspans (left panel)
    ascii_tspans = ""
    y = 30
    for line in ascii_lines:
        ascii_tspans += f'<tspan x="15" y="{y}">{escape_xml(line)}</tspan>\n'
        y += 20

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="530px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {key};}}
.value {{fill: {val};}}
.addColor {{fill: {add_c};}}
.delColor {{fill: {del_c};}}
.cc {{fill: {cc};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="985px" height="530px" fill="{bg}" rx="15"/>
<text x="15" y="30" fill="{fg}" class="ascii">
{ascii_tspans}</text>
<text x="390" y="30" fill="{fg}">
<tspan x="390" y="30">rahul@samant</tspan> -———————————————————————————————————————————-—-
<tspan x="390" y="50" class="cc">. </tspan><tspan class="key">Role</tspan>:<tspan class="cc"> .................. </tspan><tspan class="value">Data Scientist &amp; ML Engineer</tspan>
<tspan x="390" y="70" class="cc">. </tspan><tspan class="key">Location</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">Building AI Agents 🌍</tspan>
<tspan x="390" y="90" class="cc">. </tspan><tspan class="key">IDE</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">VSCode, Cursor, Windsurf</tspan>
<tspan x="390" y="110" class="cc">. </tspan>
<tspan x="390" y="130" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Programming</tspan>:<tspan class="cc"> ....... </tspan><tspan class="value">Python, JavaScript, SQL</tspan>
<tspan x="390" y="150" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">AI/ML</tspan>:<tspan class="cc"> ............ </tspan><tspan class="value">LLMs, GenAI, NLP, RAG</tspan>
<tspan x="390" y="170" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Real</tspan>:<tspan class="cc"> ...................... </tspan><tspan class="value">Hindi, English</tspan>
<tspan x="390" y="190" class="cc">. </tspan>
<tspan x="390" y="210" class="cc">. </tspan><tspan class="key">Expertise</tspan>.<tspan class="key">AI</tspan>:<tspan class="cc"> ............. </tspan><tspan class="value">LLMs, RAG, Fine Tuning, NLP</tspan>
<tspan x="390" y="230" class="cc">. </tspan><tspan class="key">Expertise</tspan>.<tspan class="key">Infra</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">Spark, AWS, MLOps, Docker</tspan>
<tspan x="390" y="250" class="cc">. </tspan><tspan class="key">Expertise</tspan>.<tspan class="key">Data</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">MongoDB, SQL, Data Pipelines</tspan>
<tspan x="390" y="270" class="cc">. </tspan>
<tspan x="390" y="290" class="cc">. </tspan><tspan class="key">Research</tspan>:<tspan class="cc"> ......... </tspan><tspan class="value">Agentic AI, Multi-Modal LLMs, RAG</tspan>
<tspan x="390" y="310" class="cc">. </tspan><tspan class="key">Research</tspan>:<tspan class="cc"> ................... </tspan><tspan class="value">MCP Server, A2A Protocol</tspan>
<tspan x="390" y="350">- Contact</tspan> -——————————————————————————————————————————————-—-
<tspan x="390" y="370" class="cc">. </tspan><tspan class="key">Email</tspan>:<tspan class="cc"> ...................... </tspan><tspan class="value">rahulsamantcoc2@gmail.com</tspan>
<tspan x="390" y="390" class="cc">. </tspan><tspan class="key">LinkedIn</tspan>:<tspan class="cc"> .............................. </tspan><tspan class="value">rahul-samant-kb37</tspan>
<tspan x="390" y="410" class="cc">. </tspan><tspan class="key">GitHub</tspan>:<tspan class="cc"> ................................. </tspan><tspan class="value">rahulsamant37</tspan>
<tspan x="390" y="450">- GitHub Stats</tspan> -—————————————————————————————————————————-—-
<tspan x="390" y="470" class="cc">. </tspan><tspan class="key">Open Source</tspan>:<tspan class="cc"> ..................................... </tspan><tspan class="value">💚</tspan>
<tspan x="390" y="490" class="cc">. </tspan><tspan class="key">AI Research</tspan>:<tspan class="cc"> ..................................... </tspan><tspan class="value">🔬</tspan>
<tspan x="390" y="510" class="cc">. </tspan><tspan class="key">Motto</tspan>:<tspan class="cc"> .. </tspan><tspan class="value">Transforming data into intelligence! 🚀</tspan>
</text>
</svg>
"""
    return svg


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "m3-passport-size.png"
    
    ascii_lines = image_to_ascii(image_path)

    print("ASCII Art Preview:")
    print("=" * 42)
    for line in ascii_lines:
        print(line)
    print("=" * 42)
    print()

    with open("dark_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="dark"))
    with open("light_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="light"))
    print("✅ Created dark_mode.svg and light_mode.svg")
