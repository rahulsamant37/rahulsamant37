"""
Build dark_mode.svg and light_mode.svg with perfectly justified neofetch panel.
Updated content for MTech at IIT Bombay, Quant/HFT/R&D focus.
Aligned bottom of info panel with bottom of ASCII art (31 lines).
"""
import sys
import unicodedata
import html

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

def display_len(s):
    """Calculate the display width of a string in monospace font.
    Normal chars = 1. East Asian wide / Emojis = 2.
    Unescapes HTML entities first so '&amp;' counts as 1 char."""
    s = html.unescape(s)
    length = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ['W', 'F']:
            length += 2
        else:
            length += 1
    return length

def generate_svg(ascii_lines, mode="dark"):
    if mode == "dark":
        bg, fg       = "#161b22", "#c9d1d9"
        key, val, cc = "#ffa657", "#a5d6ff", "#616e7f"
        add_c, del_c = "#3fb950", "#f85149"
    else:
        bg, fg       = "#ffffff", "#24292f"
        key, val, cc = "#0550ae", "#0a3069", "#6e7781"
        add_c, del_c = "#1a7f37", "#cf222e"

    # ── ASCII art sizing ──
    art_font   = 8.5
    art_lh     = 9.2          
    art_x      = 8
    art_y0     = 16           
    art_w      = 125 * 5.1    

    # ── Info panel sizing ──
    info_font  = 15
    info_lh    = 20           
    info_x     = int(art_w) + 30
    info_y0    = 26           

    # ── Canvas ──
    canvas_w   = info_x + 550
    canvas_h   = max(len(ascii_lines) * art_lh + art_y0 + 8, 640)

    # Build ASCII tspans
    art_tspans = ""
    y = art_y0
    for line in ascii_lines:
        art_tspans += f'<tspan x="{art_x}" y="{y:.1f}">{escape_xml(line)}</tspan>\n'
        y += art_lh

    # ── Info content ──
    ix = info_x
    INFO_WIDTH = 58  # Set to a fixed width of 58 characters

    def row(y_val, content):
        return f'<tspan x="{ix}" y="{y_val}">{content}</tspan>\n'

    def info_line(y_val, k, v, k2=None, unescaped_v=None):
        key_str = f"{k}.{k2}" if k2 else k
        
        # Calculate display lengths
        key_len = display_len(key_str)
        # If unescaped_v is provided (for custom markup like Lines of Code), use its length
        val_len = display_len(unescaped_v) if unescaped_v else display_len(v)
        
        dots_needed = INFO_WIDTH - 4 - key_len - val_len
        dots_needed = max(1, dots_needed)
        dots = "." * dots_needed
        
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

    def section(y_val, title):
        dashes = "—" * max(1, (INFO_WIDTH - display_len(title) - 1))
        return row(y_val, f'{title} {dashes}')

    iy = info_y0
    info_tspans = ""

    # Line 1-2: Header
    title = "rahulsamant37"
    dashes = "—" * max(1, (INFO_WIDTH - display_len(title) - 1))
    info_tspans += row(iy, f"{title} {dashes}")
    iy += info_lh

    # Line 3-6: Academic & Career Fields
    info_tspans += info_line(iy, "Class", "MTech @ IIT Bombay")
    iy += info_lh
    # Escape ampersand for XML, but length calculation will unescape it
    info_tspans += info_line(iy, "Focus", "R&amp;D, Quant, Systems")
    iy += info_lh
    info_tspans += info_line(iy, "Base", "IIT Bombay, India")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    # Line 7-11: Skills
    info_tspans += info_line(iy, "Knowledge", "C++, Python, SQL", "Core")
    iy += info_lh
    info_tspans += info_line(iy, "Knowledge", "Algorithms, OS, Systems", "Systems")
    iy += info_lh
    info_tspans += info_line(iy, "Knowledge", "Math, Statistics, ML", "Quant")
    iy += info_lh
    info_tspans += info_line(iy, "Knowledge", "LLMs, RAG, NLP", "AI")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    # Line 12-15: Tools
    info_tspans += info_line(iy, "Weaponry", "VSCode, Linux, Git")
    iy += info_lh
    info_tspans += info_line(iy, "Frameworks", "PyTorch, Spark, Docker")
    iy += info_lh
    info_tspans += info_line(iy, "Cloud", "AWS, MLOps, MongoDB")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    # Line 16-20: GitHub Stats
    info_tspans += section(iy, "- GitHub Stats")
    iy += info_lh
    info_tspans += info_line(iy, "Open Source", "Active Contributor")
    iy += info_lh
    info_tspans += info_line(iy, "Research", "AI &amp; Systems")
    iy += info_lh
    
    # Line 19: Lines of Code
    loc_key = "Lines of Code"
    # Exact visible text for length calculation
    loc_visible_text = "446,276 ( 523,178++, 76,902-- )"
    
    # Custom markup for the value
    loc_markup = (
        f'<tspan class="value" id="loc_data">446,276</tspan> ( '
        f'<tspan class="addColor" id="loc_add">523,178</tspan><tspan class="addColor">++</tspan>, '
        f'<tspan class="delColor" id="loc_del">76,902</tspan><tspan class="delColor">--</tspan> )'
    )
    info_tspans += info_line(iy, loc_key, loc_markup, unescaped_v=loc_visible_text)
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    # Line 21-24: Interests
    info_tspans += section(iy, "- Interests")
    iy += info_lh
    info_tspans += info_line(iy, "Domains", "High-Frequency Trading")
    iy += info_lh
    info_tspans += info_line(iy, "Hobbies", "Coding, Reading, Chess")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    # Line 25-29: Contact
    info_tspans += section(iy, "- Connect")
    iy += info_lh
    info_tspans += info_line(iy, "Email", "rahulsamantcoc2@gmail.com")
    iy += info_lh
    info_tspans += info_line(iy, "LinkedIn", "rahul-samant-kb37")
    iy += info_lh
    info_tspans += info_line(iy, "GitHub", "rahulsamant37")
    iy += info_lh
    info_tspans += blank(iy)
    iy += info_lh

    # Line 30-31: Motto
    info_tspans += section(iy, "- Motto")
    iy += info_lh
    
    motto_clean = "Comfort < Motivation < Discipline < Obsession"
    motto_xml = "Comfort &lt; Motivation &lt; Discipline &lt; Obsession"
    
    dots_needed = INFO_WIDTH - 3 - display_len(motto_clean)
    dots = "." * max(1, dots_needed)
    info_tspans += row(iy, f'<tspan class="cc">. {dots} </tspan><tspan class="value">{motto_xml}</tspan>')

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
.addColor {{ fill: {add_c}; }}
.delColor {{ fill: {del_c}; }}
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

    with open("dark_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="dark"))
    with open("light_mode.svg", "w") as f:
        f.write(generate_svg(ascii_lines, mode="light"))
    print("✅ Created dark_mode.svg and light_mode.svg")
