import os
import random

output_dir = "data/assets/products"
os.makedirs(output_dir, exist_ok=True)

def generate_svg(filename, title, color1, color2):
    svg_content = f"""<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad_{filename}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
          <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
        </linearGradient>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.5" stroke-opacity="0.1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grad_{filename})" />
      <rect width="100%" height="100%" fill="url(#grid)" />
      
      <!-- Abstract Shapes -->
      <circle cx="80%" cy="20%" r="100" fill="white" fill-opacity="0.05" />
      <rect x="10%" y="70%" width="200" height="200" fill="white" fill-opacity="0.03" transform="rotate(15 100 700)" />
      
      <text x="50%" y="45%" font-family="monospace" font-size="40" font-weight="black" fill="white" text-anchor="middle" letter-spacing="10">
        SOVEREIGN
      </text>
      <text x="50%" y="55%" font-family="monospace" font-size="18" fill="#00ff88" text-anchor="middle" letter-spacing="5" font-weight="bold">
        {title.upper()}
      </text>
      
      <rect x="40%" y="60%" width="20%" height="2" fill="#00ff88" fill-opacity="0.5" />
    </svg>"""
    
    with open(os.path.join(output_dir, f"{filename}.svg"), "w") as f:
        f.write(svg_content)

themes = [
    ("matrix_01", "#0f172a", "#00ff88"),
    ("matrix_02", "#1e1b4b", "#8b5cf6"),
    ("matrix_03", "#450a0a", "#f43f5e"),
    ("matrix_04", "#064e3b", "#10b981"),
    ("matrix_05", "#0f172a", "#38bdf8"),
    ("matrix_06", "#171717", "#404040"),
    ("matrix_07", "#2e1065", "#d946ef"),
    ("matrix_08", "#0c4a6e", "#0ea5e9"),
    ("matrix_09", "#1e293b", "#94a3b8"),
    ("matrix_10", "#000000", "#00ff88")
]

for name, c1, c2 in themes:
    generate_svg(name, "Neural Node active", c1, c2)

print(f"✅ Generated {len(themes)} Sovereign assets in {output_dir}")
