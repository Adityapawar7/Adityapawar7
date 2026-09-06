import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

# Ensure UTF-8 output across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USERNAME = "Adityapawar7"
REPOS = [
    {
        "name": "scuderia-ferrari-webgl",
        "focus": "0-Lag 3D WebGL Ferrari Telemetry & Performance Showcase",
        "lang": "TypeScript",
        "default_stars": 2,
        "default_push": "2026-09-06"
    },
    {
        "name": "SLIDE-AI-",
        "focus": "AI Presentation Platform Transforming Text Prompts to Multi-Slide PPTX",
        "lang": "TypeScript",
        "default_stars": 1,
        "default_push": "2026-06-21"
    },
    {
        "name": "learnerz-premium-study-suite",
        "focus": "Premium Study OS & Deep-Work Focus Suite for Android",
        "lang": "Kotlin",
        "default_stars": 1,
        "default_push": "2026-07-26"
    },
    {
        "name": "DeveloperOS",
        "focus": "Developer Productivity & Operating System Utility Ecosystem",
        "lang": "Python",
        "default_stars": 0,
        "default_push": "2026-08-09"
    }
]

def clean_description(desc):
    if not desc:
        return "Active engineering project"
    # Strip HTML tags
    desc = re.sub(r"<[^>]+>", "", desc)
    # Strip markdown headers, pipes, newlines
    desc = desc.replace("#", "").replace("|", "-").replace("\n", " ").strip()
    # Normalize whitespace
    desc = re.sub(r"\s+", " ", desc)
    if len(desc) > 80:
        desc = desc[:77] + "..."
    return desc

def fetch_repo_data(repo_name):
    """Fetch live repository telemetry from GitHub API."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    
    # 1. Try GitHub CLI (recommended inside GitHub Actions runner)
    try:
        cmd = ["gh", "api", f"repos/{USERNAME}/{repo_name}"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception:
        pass

    # 2. Try direct REST endpoint
    try:
        url = f"https://api.github.com/repos/{USERNAME}/{repo_name}"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "AdityaPawar7-DigestBot")
        req.add_header("Accept", "application/vnd.github.v3+json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

def main():
    repo_stats = []
    print(f"Querying GitHub API for {len(REPOS)} repositories...")

    for item in REPOS:
        repo_name = item["name"]
        data = fetch_repo_data(repo_name)
        
        if data and isinstance(data, dict):
            pushed_raw = data.get("pushed_at", "")
            pushed_formatted = pushed_raw[:10] if pushed_raw else item["default_push"]
            stars = data.get("stargazers_count", item["default_stars"])
            forks = data.get("forks_count", 0)
            issues = data.get("open_issues_count", 0)
            desc = data.get("description") or item["focus"]
            lang = data.get("language") or item["lang"]
            print(f"  [OK] {repo_name} (Stars: {stars}, Pushed: {pushed_formatted})")
        else:
            print(f"  [Fallback] {repo_name} using baseline metadata")
            pushed_formatted = item["default_push"]
            stars = item["default_stars"]
            forks = 0
            issues = 0
            desc = item["focus"]
            lang = item["lang"]

        repo_stats.append({
            "name": repo_name,
            "url": f"https://github.com/{USERNAME}/{repo_name}",
            "desc": clean_description(desc),
            "lang": lang,
            "stars": stars,
            "forks": forks,
            "issues": issues,
            "pushed_at": pushed_formatted
        })

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Construct DIGEST Markdown Table
    digest_lines = [
        "### 📡 Live Repository Telemetry & Activity Digest",
        f"> *Automated digest compiled at **`{now_utc}`** by unattended GitHub Actions runner.*",
        "",
        "| Repository | Focus & Domain | Primary Tech | Stars | Forks | Open Issues | Last Activity |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |"
    ]

    for r in repo_stats:
        row = f"| [`{r['name']}`]({r['url']}) | {r['desc']} | `{r['lang']}` | ⭐ {r['stars']} | 🍴 {r['forks']} | ⚠️ {r['issues']} | 🕒 `{r['pushed_at']}` |"
        digest_lines.append(row)

    digest_content = "\n".join(digest_lines) + "\n"

    # 1. Write DIGEST.md
    with open("DIGEST.md", "w", encoding="utf-8") as f:
        f.write(f"# Automated Daily Repository Digest\n\n{digest_content}")
    print("Wrote DIGEST.md successfully.")

    # 2. Inject into README.md between markers
    readme_file = "README.md"
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            readme = f.read()

        start_marker = "<!--DIGEST_START-->"
        end_marker = "<!--DIGEST_END-->"

        if start_marker in readme and end_marker in readme:
            before = readme.split(start_marker)[0]
            after = readme.split(end_marker)[1]
            new_readme = f"{before}{start_marker}\n\n{digest_content}\n{end_marker}{after}"
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(new_readme)
            print("Injected live digest into README.md between markers.")
        else:
            print("Notice: DIGEST markers not yet in README.md.")
    else:
        print("Warning: README.md not found in working directory.")

if __name__ == "__main__":
    main()
