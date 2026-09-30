from pathlib import Path
import subprocess,re

BASE=Path(__file__).resolve().parent.parent

def git(repo,args):
    return subprocess.run(["git","-C",str(repo)]+args,capture_output=True,text=True,check=True).stdout

def get_date(repo,folder):
    out=git(repo,["log","--diff-filter=A","--format=%ad","--date=short","--",folder]).splitlines()
    return out[-1] if out else None

counts={}
repos=[Path.home()/"LeetCode",Path.home()/"Codeforces"]

for item in repos[0].iterdir():
    if item.is_dir() and item.name[:1].isdigit():
        d=get_date(repos[0],item.name)
        if d:
            counts[d]=counts.get(d,0)+1

folders=set()
for f in git(repos[1],["ls-files"]).splitlines():
    m=re.match(r"^(\d+/[A-Z]\s*-\s*[^/]+)/",f)
    if m:
        folders.add(m.group(1))

for folder in folders:
    d=get_date(repos[1],folder)
    if d:
        counts[d]=counts.get(d,0)+1

dates=sorted(counts)
values=[counts[d] for d in dates]

p=BASE/"docs/index.html"
s=p.read_text(encoding="utf-8")
s=re.sub(r"const dates=.*?;",f"const dates={dates!r};",s)
s=re.sub(r"const values=.*?;",f"const values={values!r};",s)
p.write_text(s,encoding="utf-8")

print(f"Interactive chart updated: {sum(values)} problems")
