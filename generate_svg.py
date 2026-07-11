"""
Build dark_mode.svg and light_mode.svg with:
  LEFT:  User's hand-crafted ASCII art (125 chars × 68 lines) at small font
  RIGHT: neofetch-style info panel at normal font

Uses SVG viewBox for responsive scaling to fit GitHub's ~854px profile area.

Layout (internal coordinates):
  Canvas:     1500 × 640
  ASCII art:  font 8.5px, x=8, ~638px wide  (125 × 5.1px)
  Info panel:  font 15px,  x=660, ~840px wide
"""
import sys


def read_ascii_art(filepath):
    with open(filepath, "r") as f:
        lines = [line.rstrip("\n\r") for line in f.readlines()]
    while lines and lines[-1].strip() == "":
        lines.pop()
    return lines


def escape_xml(s):
    return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;"))


def generate_svg(ascii_lines, mode="dark"):
    if mode == "dark":
        bg, fg       = "#161b22", "#c9d1d9"
        key, val, cc = "#ffa657", "#a5d6ff", "#616e7f"
    else:
        bg, fg       = "#ffffff", "#24292f"
        key, val, cc = "#0550ae", "#0a3069", "#6e7781"

    # ── ASCII art sizing ──
    art_font   = 8.5
    art_lh     = 9.2          # line height
    art_x      = 8
    art_y0     = 16           # first baseline
    art_w      = 125 * 5.1    # ≈ 637px

    # ── Info panel sizing ──
    info_font  = 15
    info_lh    = 20           # line height
    info_x     = int(art_w) + 30   # 667
    info_y0    = 26                # first baseline (vertically centered-ish)

    # ── Canvas ──
    canvas_w   = info_x + 830      # 667 + 830 = 1497 ≈ 1500
    canvas_h   = max(len(ascii_lines) * art_lh + art_y0 + 8, 640)

    # Build ASCII tspans
    art_tspans = ""
    y = art_y0
    for line in ascii_lines:
        art_tspans += f'<tspan x="{art_x}" y="{y:.1f}">{escape_xml(line)}</tspan>\n'
        y += art_lh

    # ── Info content (neofetch style, matching Andrew6rant layout) ──
    ix = info_x
    def row(y_val, content):
        return f'<tspan x="{ix}" y="{y_val}">{content}</tspan>\n'

    def info_line(y_val, k, dots, v, k2=None):
        """Build a neofetch-style line: . key: .... value"""
        if k2:
            return row(y_val,
                f'<tspan class="cc">. </tspan>'
                f'<tspan class="key">{k}</tspan>.'
                f'<tspan class="key">{k2}</tspan>:'
                f'<tspan class="cc"> {dots} </tspan>'
                f'<tspan class="value">{v}</tspan>')
        return row(y_val,
            f'<tspan class="cc">. </tspan>'
            f'<tspan class="key">{k}</tspan>:'
            f'<tspan class="cc"> {dots} </tspan>'
            f'<tspan class="value">{v}</tspan>')

    def blank(y_val):
        return row(y_val, '<tspan class="cc">. </tspan>')

    def section(y_val, title, dashes):
        return row(y_val, f'{title} -{dashes}-')

    iy = info_y0
    info_tspans = ""

    # Header
    info_tspans += row(iy, 'rahul@samant')
    iy += info_lh
    info_tspans += row(iy, '-' * 58)
    iy += info_lh

    info_tspans += info_line(iy, "Role", "...................", "Data Scientist &amp; ML Engineer")
    iy += info_lh
    info_tspans += info_line(iy, "Location", ".................", "Building AI Agents 🌍")
    iy += info_lh
    info_tspans += info_line(iy, "IDE", "....................", "VSCode, Cursor, Windsurf")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    info_tspans += info_line(iy, "Languages", "..", "Python, JavaScript, SQL", "Code")
    iy += info_lh
    info_tspans += info_line(iy, "Languages", "....", "LLMs, GenAI, NLP, RAG", "AI")
    iy += info_lh
    info_tspans += info_line(iy, "Languages", "........", "Hindi, English", "Real")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    info_tspans += info_line(iy, "Expertise", "......", "LLMs, RAG, Fine Tuning", "AI")
    iy += info_lh
    info_tspans += info_line(iy, "Expertise", "....", "Spark, AWS, MLOps, Docker", "Infra")
    iy += info_lh
    info_tspans += info_line(iy, "Expertise", "....", "MongoDB, SQL, Data Pipelines", "Data")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    info_tspans += info_line(iy, "Research", "........", "Agentic AI, Multi-Modal LLMs")
    iy += info_lh
    info_tspans += info_line(iy, "Research", "........", "RAG Systems, MCP Server, A2A")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    info_tspans += info_line(iy, "Tools", ".............", "PyTorch, TensorFlow, LangChain")
    iy += info_lh
    info_tspans += info_line(iy, "Cloud", ".............", "AWS, Docker, Kubernetes, Jenkins")
    iy += info_lh * 2

    # Contact section
    info_tspans += section(iy, "- Contact", "—" * 24)
    iy += info_lh
    info_tspans += info_line(iy, "Email", "..................", "rahulsamantcoc2@gmail.com")
    iy += info_lh
    info_tspans += info_line(iy, "LinkedIn", "...........................", "rahul-samant-kb37")
    iy += info_lh
    info_tspans += info_line(iy, "GitHub", ".............................", "rahulsamant37")
    iy += info_lh * 2

    # GitHub Stats section
    info_tspans += section(iy, "- GitHub Stats", "—" * 21)
    iy += info_lh
    info_tspans += info_line(iy, "Open Source", "...............................", "💚")
    iy += info_lh
    info_tspans += info_line(iy, "AI Research", "...............................", "🔬")
    iy += info_lh * 2

    # Motto
    info_tspans += section(iy, "- Motto", "—" * 24)
    iy += info_lh
    info_tspans += row(iy, f'<tspan class="cc">. </tspan><tspan class="value">Transforming data into intelligence! 🚀</tspan>')

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg"
     font-family="ConsolasFallback,Consolas,Monaco,monospace"
     viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}"
     width="100%">
<style>
@font-face {{
  src: local('Consolas'), local('Consolas Bold'), local('Monaco');
  font-family: 'ConsolasFallback';
  font-display: swap;
  size-adjust: 109%;
}}
.key  {{ fill: {key}; }}
.value {{ fill: {val}; }}
.cc   {{ fill: {cc}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{canvas_w:.0f}" height="{canvas_h:.0f}" fill="{bg}" rx="12"/>
<text x="{art_x}" y="{art_y0}" fill="{fg}" font-size="{art_font}px">
{art_tspans}</text>
<text x="{info_x}" y="{info_y0}" fill="{fg}" font-size="{info_font}px">
{info_tspans}</text>
</svg>
"""
    return svg


if __name__ == "__main__":
    art_file = sys.argv[1] if len(sys.argv) > 1 else "ascii-art.txt"
    ascii_lines = read_ascii_art(art_file)
    print(f"ASCII art: {max(len(l) for l in ascii_lines)} chars × {len(ascii_lines)} lines")

    with open("dark_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="dark"))
    with open("light_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="light"))
    print("✅ Created dark_mode.svg and light_mode.svg")
