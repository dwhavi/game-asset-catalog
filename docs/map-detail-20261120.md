tools/check_sizes.py | ta, timezone  OWNER = "sigco3111" REPOS = ["assets-2d-pixel", "assets-audio", "assets-3d-lowpoly", "assets-3d-lowpoly-2", "assets-ui-icons", "assets-2d-portraits", "assets-code"] LIMIT_MB = 900 # (기준
reg.py | sert META['name'].lower() not in nms, 'dup name' P('before rows='+str(n_before)) row=[META['name'],'assets-3d-lowpoly-2',META['slug']+'/'+META['zip'],'3D 모델',META['tags'],META['author'],META['url'],M
reg.py | repo rows='+str(n2)+' '+json.dumps({k:cnt.get(k,0) for k in ['assets-2d-pixel','assets-3d-lowpoly','assets-3d-lowpoly-2','assets-ui-icons','assets-audio','assets-2d-portraits']})) tsum=sum(cnt.get(k,
reg.py | o','assets-2d-portraits']})) tsum=sum(cnt.get(k,0) for k in ['assets-2d-pixel','assets-3d-lowpoly','assets-3d-lowpoly-2','assets-ui-icons','assets-audio','assets-2d-portraits']) rd,n3=re.subn(r'\| \*
reg.py | g']+'), 라이선스: '+META['license']+', 제작자: '+META['author']+'\n'  '- 출처: '+META['url']+'\n'  '- 수집 커밋: assets-3d-lowpoly-2 '+META['commit']+' (에셋: '+META['name']+' 추가)\n'  '- 포털 등록: catalog.csv '+str(n_
README.md | s-3d-lowpoly](https://github.com/sigco3111/assets-3d-lowpoly) | 3D 로우폴리 모델 (1호, GLB·OBJ) | 508 | | [assets-3d-lowpoly-2](https://github.com/sigco3111/assets-3d-lowpoly-2) | 3D 로우폴리 모델 (2호) | 215 | | 
README.md | 3d-lowpoly) | 3D 로우폴리 모델 (1호, GLB·OBJ) | 508 | | [assets-3d-lowpoly-2](https://github.com/sigco3111/assets-3d-lowpoly-2) | 3D 로우폴리 모델 (2호) | 215 | | [assets-ui-icons](https://github.com/sigco3111/ass
--- raw repo-to-link mapping in tools/ and docs/ ---
MAP tools/check_sizes.py hasrepo=True
MAP tools/build_wiki.py hasrepo=True
MAP tools/build_index.py hasrepo=True
MAP reg.py hasrepo=True
