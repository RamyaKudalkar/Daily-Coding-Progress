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
        return f"Q{number} â€” {title}"

    return name

def format_codeforces(name):
    match = re.match(r"(\d+[A-Z]?)[\s-]+(.+)", name)

    if match:
        number = match.group(1)
        title = match.group(2)
        return f"{number} â€” {title}"

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
    "# ðŸ“Š Daily Coding Progress",
    "",
    f"**Total Solved: {total}**",
    ""
]

for date in all_dates:
    formatted_date = datetime.strptime(
        date, "%Y-%m-%d"
    ).strftime("%B %d, %Y")

    lines.append(f"## ðŸ“… {formatted_date}")
    lines.append("")

    if date in leetcode:
        lines.append(f"ðŸŸ¢ **LeetCode â€” {len(leetcode[date])}**")
        for problem in leetcode[date]:
            lines.append(f"â€¢ {problem}")
        lines.append("")

    if date in codeforces:
        lines.append(f"ðŸ”µ **Codeforces â€” {len(codeforces[date])}**")
        for problem in codeforces[date]:
            lines.append(f"â€¢ {problem}")
        lines.append("")

    lines.append("---")
    lines.append("")

output = os.path.join(BASE, "Daily-Coding-Progress.md")

with open(output, "w", encoding="utf-8") as file:
    file.write("\n".join(lines))

readme = os.path.join(BASE, "README.md")

chart_dates = sorted(set(leetcode) | set(codeforces))
chart_values = []

running_total = 0

for date in chart_dates:
    running_total += len(leetcode.get(date, [])) + len(codeforces.get(date, []))
    chart_values.append(running_total)

chart_data = ",".join(
    f'"{date}":{value}' for date, value in zip(chart_dates, chart_values)
)

chart_url = (
    "https://quickchart.io/chart?c="
    "{type:%27bar%27,data:{labels:["
    + ",".join(f"%27{d}%27" for d in chart_dates)
    + "],datasets:[{label:%27Problems%20Solved%27,data:["
    + ",".join(map(str, chart_values))
    + "],borderWidth:0}]},options:{"
    "scales:{xAxes:[{display:true}],yAxes:[{beginAtZero:true}]},"
    "legend:{display:false}}}"
)

readme_lines = [
    "# 💻 Daily Coding Progress",
    "",
    "🎯 Total Solved",
    "",
    f"**{total} Problems**",
    "",
    "<!-- DAILY_CODING_PROGRESS_CHART_START -->",
    f"![Daily Coding Progress]({chart_url})",
    "<!-- DAILY_CODING_PROGRESS_CHART_END -->",
    ""
]

with open(readme, "w", encoding="utf-8") as file:
    file.write("\n".join(readme_lines))

print("Daily-Coding-Progress.md updated successfully!")
print("README.md updated successfully!")
print(f"LeetCode: {total_leetcode}")
print(f"Codeforces: {total_codeforces}")
print(f"Total solved: {total}")
