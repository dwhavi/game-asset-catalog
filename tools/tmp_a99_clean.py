import glob, subprocess


def sh(c):
    print(c, flush=True)
    subprocess.run(c, shell=True, check=True)


targets = []
for pat in ["tools/tmp_a99_*.py", ".github/workflows/tmp-a99-*.yml", ".github/workflows/tmp_a99_*.py"]:
    targets.extend(glob.glob(pat))
for t in targets:
    sh("git rm -q " + t)
sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" commit -m "정리: A99 임시 파일 삭제"')
sh("git push origin HEAD:main")
print("cleaned", targets, flush=True)
