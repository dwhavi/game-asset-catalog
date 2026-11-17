import csv,io,json,os,re,subprocess,sys,datetime
META=json.loads(r'''{"name":"Carmilla Vampire","slug":"carmilla-vampire","zip":"carmilla_vampire.zip","author":"JellyLion","url":"https://opengameart.org/content/carmilla-vampire","license":"CC-BY 4.0","commit":"0120bd1","preview":"preview.png","date":"2026-11-18","tags":"3d,lowpoly,vampire,character,opengameart","attr":"필수: JellyLion (opengameart.org), CC-BY 4.0","notes":"출처 페이지 License(s) CC-BY 4.0 확인 (A114); CREDITS.txt에 제작자·출처 표기. 미리보기는 zip 안 텍스처 이미지(TexturePaint.png)"}''')
def run(a):
    return subprocess.run(a,check=True,capture_output=True,text=True).stdout
def P(s):
    print('::notice::A114 '+s)
raw=open('catalog.csv','rb').read()
assert raw.endswith(b'\n')
txt=raw.decode('utf-8')
rows=list(csv.reader(io.StringIO(txt,newline='')))
hdr=rows[0]
assert len(hdr)==14 and hdr[0]=='name' and hdr[13]=='split', hdr
n_before=len(rows)-1
srcs={r[6].strip().rstrip('/').lower() for r in rows[1:] if len(r)>6}
nms={r[0].strip().lower() for r in rows[1:] if r}
assert META['url'].lower().rstrip('/') not in srcs, 'dup src'
assert META['name'].lower() not in nms, 'dup name'
P('before rows='+str(n_before))
row=[META['name'],'assets-3d-lowpoly-2',META['slug']+'/'+META['zip'],'3D 모델',META['tags'],META['author'],META['url'],META['license'],META['attr'],META['date'],META['notes'],META['slug']+'/'+META['preview'],'','']
buf=io.StringIO()
csv.writer(buf,lineterminator='\n').writerow(row)
new=txt+buf.getvalue()
rows2=list(csv.reader(io.StringIO(new,newline='')))
assert len(rows2)-1==n_before+1
assert rows2[:len(rows)]==rows
assert all(len(r)==14 for r in rows2), 'cols'
open('catalog.csv','wb').write(new.encode('utf-8'))
P('after rows='+str(len(rows2)-1)+' added=1')
cnt={}
for r in rows2[1:]:
    cnt[r[1]]=cnt.get(r[1],0)+1
rd=open('README.md',encoding='utf-8').read()
total=len(rows2)-1
rd,n1=re.subn(r'\*\*총 [\d,]+팩입니다\.\*\*','**총 '+format(total,',')+'팩입니다.**',rd)
assert n1==1, 'total line'
def fixrow(m):
    repo=m.group(1)
    return m.group(0)[:m.start(2)-m.start(0)]+str(cnt.get(repo,0))+m.group(0)[m.end(2)-m.start(0):]
rd,n2=re.subn(r'\| \[(assets-[\w-]+)\]\(https://github\.com/sigco3111/\1\) \|[^\n]*?\| (\d+) \|',fixrow,rd)
P('readme repo rows='+str(n2)+' '+json.dumps({k:cnt.get(k,0) for k in ['assets-2d-pixel','assets-3d-lowpoly','assets-3d-lowpoly-2','assets-ui-icons','assets-audio','assets-2d-portraits']}))
tsum=sum(cnt.get(k,0) for k in ['assets-2d-pixel','assets-3d-lowpoly','assets-3d-lowpoly-2','assets-ui-icons','assets-audio','assets-2d-portraits'])
rd,n3=re.subn(r'\| \*\*합계\*\* \| \| \*\*\d+\*\* \|','| **합계** | | **'+str(tsum)+'** |',rd)
assert n3==1, 'sum row'
open('README.md','w',encoding='utf-8').write(rd)
ch=open('docs/COLLECTION-HISTORY.md',encoding='utf-8').read()
key='A113 ambientCG 1팩 등록'
k=ch.find(key)
assert k>0, 'anchor'
ls=ch.rfind('\n',0,k)+1
block=('### A114 수동 라운드 (1팩, '+META['date']+' KST)\n\n'
 '- 팩: '+META['name']+' (slug '+META['slug']+'), 라이선스: '+META['license']+', 제작자: '+META['author']+'\n'
 '- 출처: '+META['url']+'\n'
 '- 수집 커밋: assets-3d-lowpoly-2 '+META['commit']+' (에셋: '+META['name']+' 추가)\n'
 '- 포털 등록: catalog.csv '+str(n_before)+'→'+str(n_before+1)+' (등록 커밋 시 기록), 기존 행 불변 확인\n'
 '- 규칙 메모: Mixamo 항목은 캐릭터 규칙에 따라 파일 수집 제외, Sketchfab 검색은 접근 키 필요로 이번 회차 미실행, 계절·이벤트 자료 제외\n\n')
ch=ch[:ls]+block+ch[ls:]
open('docs/COLLECTION-HISTORY.md','w',encoding='utf-8').write(ch)
run(['git','config','user.name','asset-collector'])
run(['git','config','user.email','asset-collector@users.noreply.github.com'])
run(['git','add','catalog.csv','README.md','docs/COLLECTION-HISTORY.md'])
run(['git','commit','-q','-m','카탈로그: '+META['name']+' 등록 (A114)'])
sha=run(['git','rev-parse','--short','HEAD']).strip()
P('register commit='+sha)
pushed=False
for k2 in range(3):
    try:
        run(['git','pull','--rebase','-q','origin','main']); run(['git','push','-q','origin','HEAD:main']); pushed=True; break
    except subprocess.CalledProcessError:
        P('push retry '+str(k2))
if not pushed:
    print('::error::A114 push failed'); sys.exit(1)
for cmd in [['python3','tools/build_index.py'],['python3','tools/build_wiki.py']]:
    try:
        o=subprocess.run(cmd,capture_output=True,text=True,timeout=900)
        P('index '+cmd[1]+' rc='+str(o.returncode)+' '+(o.stdout+o.stderr)[-200:].replace('\n',' '))
    except Exception as e:
        P('index '+cmd[1]+' exc '+type(e).__name__)
st=run(['git','status','--porcelain']).strip()
P('index changes: '+(st.replace('\n',' | ')[:400] if st else 'none'))
if st:
    run(['git','add','-A'])
    run(['git','-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-q','-m','색인: 수동 갱신 (A114 '+META['name']+')'])
    for k3 in range(3):
        try:
            run(['git','pull','--rebase','-q','origin','main']); run(['git','push','-q','origin','HEAD:main']); break
        except subprocess.CalledProcessError:
            P('index push retry '+str(k3))
    P('index commit='+run(['git','rev-parse','--short','HEAD']).strip())
P('done total='+str(total))
