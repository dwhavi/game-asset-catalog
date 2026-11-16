import csv,io,re,subprocess as S,json
ROW=["8-Bit Sound Effect Pack","assets-audio","8-bit-sound-effect-pack/Game_SFX_by_OwlishMedia_0.zip","효과음","sfx,8bit,retro,audio","OwlishMedia","https://opengameart.org/content/8-bit-sound-effect-pack","CC0","없음 (CC0)","2026-11-16","파일 75개 8비트 효과음; zip 3.9MB 저장소 내 포함; zip 내부 License.txt에 재판매 제한 문구 있음(페이지는 CC0)"]
O=[]
def lg(s):
 print(s,flush=True);O.append(str(s))
def sh(c,ck=1):
 lg("$ "+c);S.run(c,shell=True,check=ck)
t=open("catalog.csv",encoding="utf-8").read()
rows=list(csv.reader(io.StringIO(t)))
hdr=rows[0];body=rows[1:]
lg("header "+",".join(hdr))
from collections import Counter
c=Counter(r[3] for r in body if r[1]=="assets-audio")
lg("audio types "+json.dumps(dict(c),ensure_ascii=False))
if c:
 ROW[3]=c.most_common(1)[0][0]
names=set(r[0] for r in body)
if ROW[0] in names:
 lg("exists");ROW[0]=ROW[0]
else:
 def q(x):
  return '"'+x.replace('"','""')+'"' if ("," in x or '"' in x) else x
 line=",".join(q(x) for x in ROW)
 t=t.rstrip("\n")+"\n"+line+"\n"
 open("catalog.csv","w",encoding="utf-8").write(t)
 lg("row added")
total=len([l for l in t.splitlines() if l.strip()])-1
lg("total %d"%total)
R=open("README.md",encoding="utf-8").read()
m=re.search(r"(\d{3,4})팩",R)
if m:
 R=R.replace(m.group(0),str(total)+"팩")
 open("README.md","w",encoding="utf-8").write(R)
 lg("readme %s -> %d팩"%(m.group(0),total))
L=open("docs/log.md",encoding="utf-8").read()
if "A101" not in L:
 e=("- 2026-11-16 A101 재개: 8-Bit Sound Effect Pack(1팩, catalog.csv "+str(total)+"행; 효과음 1, 3D 0). "
  "임시 GitHub Actions 워크플로+파이썬으로 러너에서 OpenGameArt 원본 zip(Game_SFX_by_OwlishMedia_0.zip, 3.9MB, 75파일)을 받아 팩 폴더 생성·커밋. "
  "512 Sound Effects(8-bit style)·RPG Sound Pack은 이미 색인에 있어 중복 제외. 3D는 Quaternius 페이지가 Google Drive 폴더로만 연결되고, "
  "kenney.nl·poly.pizza(403)·itch.io는 직접 zip URL이 없어 이번 라운드에서 0팩. 라이선스 CC0(출처 페이지 표기). "
  "catalog.csv·README.md·docs/log.md만 수정(색인은 Actions 자동 갱신).\n")
 open("docs/log.md","w",encoding="utf-8").write(L.rstrip("\n")+"\n"+e)
 lg("log appended")
sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" add catalog.csv README.md docs/log.md')
sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" commit -m "카탈로그: A101 1팩 등록"')
sh("git push origin HEAD:main")
sh("git rm -q tools/tmp_a101b_cat.py .github/workflows/tmp-a101b-cat.yml",0)
sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" commit -m "정리: A101b 임시 파일 삭제"',0)
sh("git push origin HEAD:main",0)
lg("done")
