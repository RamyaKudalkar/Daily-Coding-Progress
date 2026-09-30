import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPOS = {
    "LeetCode": os.path.expanduser("~/LeetCode"),
    "Codeforces": os.path.expanduser("~/Codeforces")
}

def git_output(repo, args):
    try:
        result = subprocess.run(
            ["git", "-C", repo] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_problem_date(repo, folder):
    output = git_output(
        repo,
        ["log", "--diff-filter=A", "--format=%ad", "--date=short", "--", folder]
    )

    if not output:
        output = git_output(
            repo,
            ["log", "-1", "--format=%ad", "--date=short", "--", folder]
        )

    return output.splitlines()[-1] if output else None

def format_leetcode(name):
    match = re.match(r"(\d+)[-_](.+)", name)

    if match:
        number = match.group(1)
        title = match.group(2).replace("-", " ").title()
        return f"Q{number} — {title}"

    return name

def format_codeforces(name):
    match = re.match(r"(\d+[A-Z]?)[\s-]+(.+)", name)

    if match:
        number = match.group(1)
        title = match.group(2)
        return f"{number} — {title}"

    return name

def get_problems(repo, platform):
    problems = defaultdict(list)

    if not os.path.isdir(repo):
        return problems

    if platform == "Codeforces":
        result = subprocess.run(
            ["git", "-C", repo, "ls-files"],
            capture_output=True,
            text=True,
            check=True
        )

        folders = set()

        for file in result.stdout.splitlines():
            match = re.match(r"^(\d+/[A-Z]\s*-\s*[^/]+)/", file)

            if match:
                folders.add(match.group(1))

        for folder in folders:
            date = get_problem_date(repo, folder)

            if date:
                match = re.match(r"^(\d+)/([A-Z]\s*-\s*.+)$", folder)

                if match:
                    display = f"{match.group(1)}{match.group(2)}"
                    problems[date].append(display)

    else:
        for item in os.listdir(repo):
            path = os.path.join(repo, item)

            if not os.path.isdir(path):
                continue

            if not item or not item[0].isdigit():
                continue

            date = get_problem_date(repo, item)

            if date:
                problems[date].append(format_leetcode(item))

    for date in problems:
        problems[date] = sorted(set(problems[date]))

    return problems

leetcode = get_problems(REPOS["LeetCode"], "LeetCode")
codeforces = get_problems(REPOS["Codeforces"], "Codeforces")

all_dates = sorted(set(leetcode) | set(codeforces))

total_leetcode = sum(len(v) for v in leetcode.values())
total_codeforces = sum(len(v) for v in codeforces.values())
total = total_leetcode + total_codeforces

lines = [
    "# 📊 Daily Coding Progress",
    "",
    f"**Total Solved: {total}**",
    ""
]

for date in all_dates:
    formatted_date = datetime.strptime(
        date, "%Y-%m-%d"
    ).strftime("%B %d, %Y")

    lines.append(f"## 📅 {formatted_date}")
    lines.append("")

    if date in leetcode:
        lines.append(f"🟢 **LeetCode — {len(leetcode[date])}**")
        for problem in leetcode[date]:
            lines.append(f"• {problem}")
        lines.append("")

    if date in codeforces:
        lines.append(f"🔵 **Codeforces — {len(codeforces[date])}**")
        for problem in codeforces[date]:
            lines.append(f"• {problem}")
        lines.append("")

    lines.append("---")
    lines.append("")

output = os.path.join(BASE, "DAILY_PROGRESS.md")

with open(output, "w", encoding="utf-8") as file:
    file.write("\n".join(lines))

print("DAILY_PROGRESS.md updated successfully!")
print(f"LeetCode: {total_leetcode}")
print(f"Codeforces: {total_codeforces}")
print(f"Total solved: {total}")
