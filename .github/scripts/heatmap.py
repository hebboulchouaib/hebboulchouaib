import datetime, json, os, random, sys, urllib.request

USER = os.environ.get("GH_USER", "hebboulchouaib")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT", "heatmap.svg")
LEVELS = ["#131316", "#3a1d1f", "#6b2b2c", "#8f3a3a", "#b04545"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
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
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def level(n, peak):
    if n == 0:
        return 0
    r = n / peak
    return 1 if r <= 0.25 else 2 if r <= 0.5 else 3 if r <= 0.75 else 4


def render(total, weeks):
    font = "'Segoe UI', Helvetica, Arial, sans-serif"
    w, h, x0, y0, step, cell = 790, 212, 24, 76, 14, 11
    peak = max((d["contributionCount"] for wk in weeks for d in wk["contributionDays"]), default=1) or 1
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Contribution activity">',
         f'<rect width="{w}" height="{h}" rx="6" fill="#08080a"/>',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="none" stroke="#2a2a2e"/>',
         f'<text x="24" y="36" font-family="{font}" font-size="12" letter-spacing="2.5" fill="#b04545">ACTIVITY</text>',
         f'<text x="{w-24}" y="36" text-anchor="end" font-family="{font}" font-size="10" letter-spacing="2" fill="#6f6a66">{total} CONTRIBUTIONS IN THE LAST YEAR</text>']
    last_month = None
    for i, wk in enumerate(weeks):
        days = wk["contributionDays"]
        if not days:
            continue
        month = datetime.date.fromisoformat(days[0]["date"]).strftime("%b").upper()
        if month != last_month and i < len(weeks) - 2:
            s.append(f'<text x="{x0 + i * step}" y="64" font-family="{font}" font-size="9" letter-spacing="1.5" fill="#6f6a66">{month}</text>')
        last_month = month
        for d in days:
            s.append(f'<rect x="{x0 + i * step}" y="{y0 + d["weekday"] * step}" width="{cell}" height="{cell}" rx="2" fill="{LEVELS[level(d["contributionCount"], peak)]}"/>')
    lx = w - 24 - 5 * step - 60
    s.append(f'<text x="{lx}" y="199" text-anchor="end" font-family="{font}" font-size="9" letter-spacing="1.5" fill="#6f6a66">LESS</text>')
    for i, c in enumerate(LEVELS):
        s.append(f'<rect x="{lx + 8 + i * step}" y="190" width="{cell}" height="{cell}" rx="2" fill="{c}"/>')
    s.append(f'<text x="{lx + 8 + 5 * step + 4}" y="199" font-family="{font}" font-size="9" letter-spacing="1.5" fill="#6f6a66">MORE</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    total, weeks = collect()
    open(OUT, "w", encoding="utf-8").write(render(total, weeks))
    print("wrote", OUT)
