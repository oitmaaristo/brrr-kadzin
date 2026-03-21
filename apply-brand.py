#!/usr/bin/env python3
"""Apply BRRR Capital branding to Claude Code Agent Monitor."""
from pathlib import Path

BASE = Path("/home/brrr/agent-monitor/client")

# 1. TAILWIND CONFIG — BRRR brand colors
tc = BASE / "tailwind.config.js"
old = tc.read_text()
new = old.replace('0: "#06060a",', '0: "#0d0d1a",')
new = new.replace('1: "#0c0c14",', '1: "#131320",')
new = new.replace('2: "#13131e",', '2: "#1a1a2e",')
new = new.replace('3: "#1a1a28",', '3: "#1f1f35",')
new = new.replace('4: "#222233",', '4: "#26263d",')
new = new.replace('5: "#2a2a3d",', '5: "#2d2d45",')
new = new.replace('DEFAULT: "#2a2a3d",', 'DEFAULT: "#2d2d45",')
new = new.replace('light: "#363650",', 'light: "#3a3a55",')
new = new.replace('DEFAULT: "#6366f1",', 'DEFAULT: "#00d4aa",')
new = new.replace('hover: "#818cf8",', 'hover: "#00e6b8",')
new = new.replace('muted: "rgba(99, 102, 241, 0.15)",', 'muted: "rgba(0, 212, 170, 0.15)",')
new = new.replace(
    'sans: ["Inter",',
    'display: ["Outfit", "Inter", "sans-serif"],\n        sans: ["Inter",'
)
tc.write_text(new)
print("OK tailwind.config.js")

# 2. INDEX.HTML — title + Google Fonts
idx = BASE / "index.html"
old = idx.read_text()
new = old.replace(
    '<title>Agent Dashboard - Claude Code Monitor</title>',
    '<title>brrr.kadzin — Agent Monitor</title>'
).replace(
    '<meta name="theme-color" content="#6366f1" />',
    '<meta name="theme-color" content="#1a1a2e" />'
).replace(
    '<meta charset="UTF-8" />',
    '<meta charset="UTF-8" />\n    <link rel="preconnect" href="https://fonts.googleapis.com" />\n    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />'
).replace(
    'content="Son Nguyen Hoang"', 'content="BRRR Capital"'
)
idx.write_text(new)
print("OK index.html")

# 3. SIDEBAR — brrr.kadzin branding
sb = BASE / "src" / "components" / "Sidebar.tsx"
old = sb.read_text()
new = old.replace(
    '<Activity className="w-4 h-4 text-accent" />',
    '<span className="text-accent font-bold text-lg" style={{fontFamily:"Outfit"}}>b</span>'
)
new = new.replace(
    '<h1 className="text-sm font-semibold text-gray-100 truncate">Agent Dashboard</h1>',
    '<h1 className="text-sm font-semibold text-gray-100 truncate" style={{fontFamily:"Outfit"}}>brrr<span className="text-accent">.</span>kadzin</h1>'
)
new = new.replace(
    '<p className="text-[11px] text-gray-500">Claude Code Monitor</p>',
    '<p className="text-[11px] text-gray-500">Agent Monitor</p>'
)
new = new.replace('href="https://sonnguyenhoang.com"', 'href="#"')
new = new.replace('<span>sonnguyenhoang.com</span>', '<span>BRRR Capital</span>')
new = new.replace('title="sonnguyenhoang.com"', 'title="BRRR Capital"')
new = new.replace('href="https://github.com/hoangsonww"', 'href="#"')
new = new.replace('>v1.0.0<', '>BRRR<')
sb.write_text(new)
print("OK Sidebar.tsx")

# 4. INDEX.CSS — scrollbar and selection colors
css = BASE / "src" / "index.css"
old = css.read_text()
new = old.replace('scrollbar-color: #2a2a3d #0c0c14;', 'scrollbar-color: #2d2d45 #131320;')
new = new.replace('background: #0c0c14;', 'background: #131320;')
new = new.replace('background: #2a2a3d;', 'background: #2d2d45;')
new = new.replace('background: #363650;', 'background: #3a3a55;')
new = new.replace('rgba(99, 102, 241, 0.3)', 'rgba(0, 212, 170, 0.3)')
css.write_text(new)
print("OK index.css")

print("\nDone! Now run: cd /home/brrr/agent-monitor && npm run build")
