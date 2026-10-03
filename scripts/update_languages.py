#!/usr/bin/env python3
"""Generate a real language breakdown from public GitHub repository language bytes."""
import json, os, urllib.request, html
from collections import Counter
from pathlib import Path
USER='maximyellowrock'
TOKEN=os.environ.get('GITHUB_TOKEN','')
def fetch(url):
    headers={'Accept':'application/vnd.github+json','User-Agent':'maxim-profile-languages'}
    if TOKEN: headers['Authorization']='Bearer '+TOKEN
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=25) as response: return json.load(response)
repos=[]
for page in range(1,6):
    batch=fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner')
    repos+=batch
    if len(batch)<100: break
counts=Counter()
for repo in repos:
    if repo.get('fork') or repo.get('private') or repo.get('archived'): continue
    for language,size in fetch(repo['languages_url']).items(): counts[language]+=size
if not counts: raise RuntimeError('No language data found; refusing to overwrite chart')
colors=['#20c8ff','#8d67f8','#1ed8ad','#ffbd59','#ff638c','#6b9cf5','#a7b5d0']
items=counts.most_common(6)
other=sum(counts.values())-sum(size for _,size in items)
if other: items.append(('Other',other))
total=sum(counts.values())
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260">',
'<rect width="1000" height="260" rx="18" fill="#081629"/>',
'<rect x="1" y="1" width="998" height="258" rx="17" fill="none" stroke="#1686be"/>',
'<text x="40" y="61" fill="#f1f8ff" font-family="Arial,sans-serif" font-size="32" font-weight="bold">LANGUAGES IN PUBLIC REPOSITORIES</text>',
'<text x="40" y="95" fill="#98bdd7" font-family="Arial,sans-serif" font-size="18">Measured by GitHub language bytes · excludes forks and archived repos</text>']
x=40
for idx,(lang,size) in enumerate(items):
    width=920*size/total
    parts.append(f'<rect x="{x:.2f}" y="116" width="{width:.2f}" height="35" fill="{colors[idx]}"/>')
    x+=width
for idx,(lang,size) in enumerate(items):
    col=idx%4; row=idx//4; x=40+col*235; y=185+row*35
    parts.extend([f'<circle cx="{x+7}" cy="{y-5}" r="7" fill="{colors[idx]}"/>',
    f'<text x="{x+24}" y="{y}" font-family="Arial,sans-serif" font-size="19" fill="#f0f8ff">{html.escape(lang)} {size/total*100:.1f}%</text>'])
parts.append('</svg>')
Path('assets/languages.svg').write_text(''.join(parts),encoding='utf-8')
print('Updated languages.svg from',len(repos),'repositories and',len(counts),'languages')
