import os, re, subprocess, time, traceback

REPO_DIR = "fire-and-spell-animations"
ZIP = "anims_0.zip"
TAG = "a98-fire-and-spell-animations"
LOG = []


def log(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    LOG.append(line)


def push():
    for _ in range(3):
        if subprocess.run(["git", "push", "origin", "HEAD:main"]).returncode == 0:
            return True
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])
        time.sleep(5)
    return False


try:
    tok = os.environ.get("GITHUB_TOKEN", "")
    os.environ["GH_TOKEN"] = tok
    subprocess.run(["git", "config", "user.name", "sigco3111"], check=True)
    subprocess.run(["git", "config", "user.email", "sigco3111k@gmail.com"], check=True)
    path = os.path.join(REPO_DIR, ZIP)
    if os.path.exists(path):
        exists = subprocess.run(["gh", "release", "view", TAG], capture_output=True).returncode == 0
        if not exists:
            subprocess.run(["gh", "release", "create", TAG, path, "--title", "FIre and Spell Animations (A98)",
                            "--notes", "CC0 원본 zip. 5MB 초과 zip은 Releases 첨부 규칙에 따라 릴리스로 올렸습니다."], check=True)
            log("release created", TAG)
        else:
            log("release exists", TAG)
        subprocess.run(["git", "rm", "-q", path], check=True)
        md_path = os.path.join(REPO_DIR, "pack.md")
        md = open(md_path, encoding="utf-8").read()
        md = md.replace("- 받은 파일: " + ZIP, "- 받은 파일: " + ZIP + " (Releases 첨부: " + TAG + ")", 1)
        open(md_path, "w", encoding="utf-8").write(md)
        subprocess.run(["git", "add", md_path], check=True)
        rd = open("README.md", encoding="utf-8").read()
        old = "- 파일: \u0060" + ZIP + "\u0060 (10823.9KB) — 저장소 내 포함"
        new = "- 파일: \u0060" + ZIP + "\u0060 (10823.9KB) — Releases 첨부 (tag " + TAG + ")"
        if old in rd:
            rd = rd.replace(old, new, 1)
            open("README.md", "w", encoding="utf-8").write(rd)
            subprocess.run(["git", "add", "README.md"], check=True)
            log("README entry fixed")
        else:
            log("README entry not found")
        subprocess.run(["git", "commit", "-m", "정리: FIre and Spell Animations zip을 Releases로 이동"], check=True)
        if not push():
            raise SystemExit("push failed")
        log("moved to release")
    else:
        log("zip already removed from tree")
except SystemExit as e:
    log("EXIT", str(e))
except Exception:
    log("FATAL")
    traceback.print_exc()

try:
    open("tmp-a98-log3.txt", "w", encoding="utf-8").write("\n".join(LOG) + "\n")
    subprocess.run(["git", "add", "-f", "tmp-a98-log3.txt"], check=False)
    subprocess.run(["git", "commit", "-m", "임시: A98 릴리스 이동 로그"], check=False)
    push()
except Exception:
    traceback.print_exc()
log("done")
