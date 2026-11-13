import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "hebboulchouaib")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT", "languages.svg")
HIDE = {"Jupyter Notebook"}          
COLORS = ["#b04545", "#8c3636", "#e8e4df", "#9a958f", "#6b4040", "#5a5650"]


def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("User-Agent", "profile-readme")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    totals = {}
    repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
    for repo in repos:
        if repo["fork"] or repo["name"] == USER:
            continue
        for lang, size in api(f"/repos/{USER}/{repo['name']}/languages").items():
            if lang not in HIDE:
                totals[lang] = totals.get(lang, 0) + size
    return totals


def render(totals):
    items = sorted(totals.items(), key=lambda x: -x[1])[:6]
    total = sum(v for _, v in items) or 1
    font = "'Segoe UI', Helvetica, Arial, sans-serif"
    w, bar_x, bar_w = 400, 24, 352
    h = 96 + 26 * ((len(items) + 1) // 2)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Most used languages">',
         f'<rect width="{w}" height="{h}" rx="6" fill="#08080a"/>',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="none" stroke="#2a2a2e"/>',
         f'<text x="24" y="36" font-family="{font}" font-size="12" letter-spacing="2.5" fill="#b04545">MOST USED LANGUAGES</text>']
    x = bar_x
    for i, (name, size) in enumerate(items):
        seg = bar_w * size / total
        s.append(f'<rect x="{x:.1f}" y="52" width="{max(seg - 2, 1):.1f}" height="8" rx="2" fill="{COLORS[i]}"/>')
        x += seg
    for i, (name, size) in enumerate(items):
        col, row = i % 2, i // 2
        lx, ly = 24 + col * 180, 92 + row * 26
        s.append(f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4" fill="{COLORS[i]}"/>')
        s.append(f'<text x="{lx + 16}" y="{ly}" font-family="{font}" font-size="12" fill="#9a958f">{name} <tspan fill="#e8e4df">{100 * size / total:.1f}%</tspan></text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    data = collect()
    if not data:
        sys.exit("No language data found (no public repos yet?)")
    open(OUT, "w", encoding="utf-8").write(render(data))
    print("wrote", OUT)
