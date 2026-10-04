import os
import re
import subprocess
import requests
from collections import defaultdict
from datetime import datetime,timezone

BASE_DIR=os.path.expanduser("~")
LEETCODE_DIR=os.path.join(BASE_DIR,"LeetCode")
OUTPUT_FILE="Daily-Coding-Progress.md"
README_FILE="README.md"

def get_leetcode():
    problems=defaultdict(list)

    if not os.path.exists(LEETCODE_DIR):
        return problems

    try:
        result=subprocess.run(
            ["git","-C",LEETCODE_DIR,"log","--all","--format=%ad|%s","--date=short"],
            capture_output=True,
            text=True
        )

        seen=set()

        for line in result.stdout.splitlines():
            parts=line.split("|",1)

            if len(parts)!=2:
                continue

            date,message=parts

            match=re.search(r"(\d+)-[a-z0-9]+",message.lower())

            if not match:
                continue

            number=match.group(1)

            folder_match=re.search(
                rf"(\d+-[a-z0-9][a-z0-9-]*)",
                message.lower()
            )

            if folder_match:
                problem=folder_match.group(1)
            else:
                continue

            key=problem

            if key in seen:
                continue

            seen.add(key)
            problems[date].append(problem)

        # If git history does not contain every problem,
        # count the folders and use their latest git date.
        folders=[]

        for name in os.listdir(LEETCODE_DIR):
            path=os.path.join(LEETCODE_DIR,name)

            if os.path.isdir(path) and re.match(r"^\d+-",name):
                folders.append(name)

        for folder in folders:
            try:
                result=subprocess.run(
                    [
                        "git",
                        "-C",
                        LEETCODE_DIR,
                        "log",
                        "-1",
                        "--format=%ad",
                        "--date=short",
                        "--",
                        folder
                    ],
                    capture_output=True,
                    text=True
                )

                date=result.stdout.strip()

                if date:
                    already=False

                    for values in problems.values():
                        if folder in values:
                            already=True
                            break

                    if not already:
                        problems[date].append(folder)

            except:
                pass

    except Exception as e:
        print("LeetCode error:",e)

    return problems


def get_codeforces():
    problems=defaultdict(list)

    try:
        url="https://codeforces.com/api/user.status?handle=RamyaKudalkar"

        response=requests.get(url,timeout=20)
        response.raise_for_status()

        data=response.json()

        if data.get("status")!="OK":
            return problems

        submissions=data["result"]

        accepted={}

        for sub in submissions:

            if sub.get("verdict")!="OK":
                continue

            contest_id=sub.get("contestId")
            index=sub.get("problem",{}).get("index")
            name=sub.get("problem",{}).get("name")
            timestamp=sub.get("creationTimeSeconds")

            if not contest_id or not index or not name or not timestamp:
                continue

            key=f"{contest_id}/{index}"

            date=datetime.fromtimestamp(
                timestamp,
                timezone.utc
            ).strftime("%Y-%m-%d")

            if key not in accepted:
                accepted[key]=(date,name)
            else:
                old_date=accepted[key][0]

                if date<old_date:
                    accepted[key]=(date,name)

        for key,(date,name) in accepted.items():

            problems[date].append(
                f"{key} - {name}"
            )

    except Exception as e:
        print("Codeforces API error:",e)

    return problems


leetcode=get_leetcode()
codeforces=get_codeforces()

for date in list(leetcode.keys()):
    leetcode[date]=sorted(set(leetcode[date]))

    if not leetcode[date]:
        del leetcode[date]

for date in list(codeforces.keys()):
    codeforces[date]=sorted(set(codeforces[date]))

    if not codeforces[date]:
        del codeforces[date]


leetcode_unique=set()

for values in leetcode.values():
    for problem in values:
        leetcode_unique.add(problem)


codeforces_unique=set()

for values in codeforces.values():
    for problem in values:
        codeforces_unique.add(problem)


total_leetcode=len(leetcode_unique)
total_codeforces=len(codeforces_unique)
total=total_leetcode+total_codeforces


all_dates=sorted(
    set(leetcode.keys())|set(codeforces.keys()),
    reverse=True
)


with open(OUTPUT_FILE,"w",encoding="utf-8") as f:

    f.write("# 📊 Daily Coding Progress\n\n")
    f.write(f"**Total Solved: {total}**\n\n")

    for date in all_dates:

        if not leetcode.get(date) and not codeforces.get(date):
            continue

        dt=datetime.strptime(date,"%Y-%m-%d")
        formatted=dt.strftime("%B %d, %Y")

        f.write(f"## 📅 {formatted}\n\n")

        if leetcode.get(date):

            f.write("🟢 **LeetCode**\n\n")

            for problem in leetcode[date]:
                f.write(f"- {problem}\n")

            f.write("\n")

        if codeforces.get(date):

            f.write("🔵 **Codeforces**\n\n")

            for problem in codeforces[date]:
                f.write(f"- {problem}\n")

            f.write("\n")


with open(README_FILE,"w",encoding="utf-8") as f:
    f.write("## 📊 Daily-Coding-Progress\n\n")
    f.write("### 🎯 Total Solved\n\n")
    f.write(f"**{total} Problems**\n\n")
    f.write("[**View Interactive Chart →**](https://ramyakudalkar.github.io/Daily-Coding-Progress/)\n")


print("Daily-Coding-Progress.md updated successfully!")
print("README.md updated successfully!")
print(f"LeetCode: {total_leetcode}")
print(f"Codeforces: {total_codeforces}")
print(f"Total solved: {total}")