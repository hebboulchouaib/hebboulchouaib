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


def render(stats):
    font = "'Segoe UI', Helvetica, Arial, sans-serif"
    w, h = 400, 174
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub stats">',
         f'<rect width="{w}" height="{h}" rx="6" fill="#08080a"/>',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="none" stroke="#2a2a2e"/>',
         f'<text x="24" y="36" font-family="{font}" font-size="12" letter-spacing="2.5" fill="#b04545">GITHUB STATS</text>']
    for i, (value, label) in enumerate(stats):
        x, y = 24 + (i % 2) * 180, 80 + (i // 2) * 54
        s.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="28" font-weight="700" fill="#e8e4df">{value}</text>')
        s.append(f'<text x="{x}" y="{y + 18}" font-family="{font}" font-size="10" letter-spacing="2" fill="#6f6a66">{label}</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    open(OUT, "w", encoding="utf-8").write(render(collect()))
    print("wrote", OUT)
