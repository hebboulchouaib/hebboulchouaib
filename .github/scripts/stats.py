import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "hebboulchouaib")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT", "stats.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
    }
  }
}
"""


def collect():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body)
    req.add_header("User-Agent", "profile-readme")
    req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        u = json.load(r)["data"]["user"]
    repos = u["repositories"]
    c = u["contributionsCollection"]
    return [
        (c["totalCommitContributions"], "COMMITS THIS YEAR"),
        (c["totalPullRequestContributions"], "PULL REQUESTS"),
        (repos["totalCount"], "PUBLIC REPOS"),
        (sum(n["stargazerCount"] for n in repos["nodes"]), "STARS EARNED"),
    ]


def level_of(stats):
    commits, prs, repos, stars = (v for v, _ in stats)
    points = commits + 4 * prs + 6 * repos + 8 * stars
    level = 1 + int(points ** 0.5)
    low, high = (level - 1) ** 2, level ** 2
    return level, (points - low) / (high - low)


def render(stats):
    font = "'Segoe UI', Helvetica, Arial, sans-serif"
    w, h = 400, 174
    level, progress = level_of(stats)
    cx, cy, r = 78, 100, 40
    circ = 2 * 3.14159265 * r
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub stats">',
         f'<rect width="{w}" height="{h}" rx="6" fill="#08080a"/>',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="none" stroke="#2a2a2e"/>',
         f'<text x="24" y="36" font-family="{font}" font-size="12" letter-spacing="2.5" fill="#b04545">GITHUB STATS</text>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1a1a1e" stroke-width="6"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#b04545" stroke-width="6" stroke-linecap="round" '
         f'stroke-dasharray="{circ * progress:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>',
         f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{font}" font-size="26" font-weight="700" fill="#e8e4df">{level}</text>',
         f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" font-family="{font}" font-size="8" letter-spacing="2" fill="#6f6a66">LEVEL</text>']
    for i, (value, label) in enumerate(stats):
        y = 74 + i * 26
        if i:
            s.append(f'<line x1="168" y1="{y - 17}" x2="376" y2="{y - 17}" stroke="#1a1a1e"/>')
        s.append(f'<text x="168" y="{y}" font-family="{font}" font-size="10" letter-spacing="2" fill="#6f6a66">{label}</text>')
        s.append(f'<text x="376" y="{y}" text-anchor="end" font-family="{font}" font-size="16" font-weight="700" fill="#e8e4df">{value}</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    data = collect()
    open(OUT, "w", encoding="utf-8").write(render(data))
    print("wrote", OUT)
