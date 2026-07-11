"""
Build dark_mode.svg and light_mode.svg from the user's hand-crafted ASCII art.

The art is 125 chars wide x 68 lines tall — displayed as a full-width banner.
GitHub profile README container is ~854px wide.
At font-size 6.8px with Consolas monospace, 125 chars ≈ 850px. Perfect fit.
Line height ~9px → 68 lines ≈ 612px + padding = ~630px.
"""
import sys


def read_ascii_art(filepath):
    """Read ASCII art file and return list of lines."""
    with open(filepath, "r") as f:
        lines = f.readlines()
    # Strip trailing newlines but preserve spaces
    lines = [line.rstrip("\n\r") for line in lines]
    # Remove trailing empty lines
    while lines and lines[-1].strip() == "":
        lines.pop()
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
    Generate full-width ASCII art SVG that fits GitHub's profile README.

    Sizing math:
    - GitHub profile README width: ~854px
    - Consolas char width at 6.8px font-size: ~6.8px * 0.6 ≈ 4.08px per char
    - But with size-adjust: 109%, effective: ~4.45px per char
    - 125 chars × 4.45px ≈ 556px... that's too narrow.
    - Actually at font-size 6.8px, monospace Consolas = ~4.1px per char
    - We want 125 chars to fill ~835px → each char ≈ 6.68px
    - So font-size ~11px should work (Consolas at 11px ≈ 6.6px per char)
    - At 11px font, line-height ~13px → 68 lines = 884px... too tall
    - Let's use font-size 7px, line-height 8.5px → 68 × 8.5 = 578px
    - 125 chars at 7px Consolas ≈ 125 × 4.2 = 525px
    
    Actually, let's just set the SVG viewBox and let it scale to fill the container.
    The SVG will have a fixed coordinate system internally and scale to fit.
    """
    if mode == "dark":
        bg, fg = "#161b22", "#c9d1d9"
    else:
        bg, fg = "#ffffff", "#24292f"

    # Internal coordinate system
    # Use font-size 10px with line-height 12px
    font_size = 10
    line_height = 12
    char_width = 6.1  # Consolas at 10px ≈ 6.1px per char (with size-adjust)
    
    padding_x = 10
    padding_y = 14
    
    num_lines = len(ascii_lines)
    max_width = max(len(line) for line in ascii_lines)
    
    svg_width = int(max_width * char_width + padding_x * 2)
    svg_height = int(num_lines * line_height + padding_y * 2)

    # Build tspans
    tspans = ""
    y = padding_y + font_size  # first baseline
    for line in ascii_lines:
        tspans += f'<tspan x="{padding_x}" y="{y}">{escape_xml(line)}</tspan>\n'
        y += line_height

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" 
     font-family="ConsolasFallback,Consolas,Monaco,monospace" 
     viewBox="0 0 {svg_width} {svg_height}"
     width="100%"
     font-size="{font_size}px">
<style>
@font-face {{
  src: local('Consolas'), local('Consolas Bold'), local('Monaco');
  font-family: 'ConsolasFallback';
  font-display: swap;
  size-adjust: 109%;
}}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{svg_width}" height="{svg_height}" fill="{bg}" rx="10"/>
<text x="{padding_x}" y="{padding_y + font_size}" fill="{fg}">
{tspans}</text>
</svg>
"""
    return svg


if __name__ == "__main__":
    art_file = sys.argv[1] if len(sys.argv) > 1 else "ascii-art.txt"
    
    ascii_lines = read_ascii_art(art_file)
    print(f"ASCII art: {max(len(l) for l in ascii_lines)} chars wide × {len(ascii_lines)} lines tall")
    
    with open("dark_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="dark"))
    with open("light_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="light"))
    print("✅ Created dark_mode.svg and light_mode.svg")
