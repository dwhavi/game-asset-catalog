import os, subprocess
REPO = os.environ.get('REPO', '')
FILES = {
    'assets-3d-lowpoly-2': ['.github/workflows/a96-3d.yml', '.github/workflows/a96-thumb.yml', '.github/workflows/a96-thumb2.yml', '.github/workflows/a96-clean.yml', 'thumb-log.txt'],
    'assets-audio': ['.github/workflows/a96-audio.yml'],
    'game-asset-catalog': ['tools/a96.py', 'tools/a96b.py', 'tools/a96t.py', 'tools/a96t2.py', 'tools/a96d.py', 'tools/a96c.py', 'tools/a96-packs.json', 'a96-res.txt', 'thumb-log.txt', '.github/workflows/a96-cat.yml', '.github/workflows/a96b-cat.yml', '.github/workflows/a96d.yml', '.github/workflows/a96-clean.yml'],
}
for f in FILES.get(REPO, []):
    if os.path.exists(f):
        subprocess.run(['git', 'rm', '-q', f])
        print('removed', f)
subprocess.run(['git', 'config', 'user.name', 'sigco3111'])
subprocess.run(['git', 'config', 'user.email', 'sigco3111@users.noreply.github.com'])
subprocess.run(['git', 'add', '-A'])
r = subprocess.run(['git', 'commit', '-m', '정리: A96 임시 파일 삭제'], capture_output=True, text=True)
print(r.stdout, r.stderr)
subprocess.run(['git', 'push'])
