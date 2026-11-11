"""Download Poly Haven (CC0) models / textures / HDRIs into assets/polyhaven/<id>/ and log credits.
Usage: python fetch_polyhaven.py [--res 1k] id1 id2 ...
"""
import json, os, sys, urllib.request
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'polyhaven')
UA = {'User-Agent': 'cartoon-short-builder'}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()

def save(url, path):
    if os.path.exists(path): return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = get(url)
    with open(path, 'wb') as f: f.write(data)

def fetch(aid, res):
    info = json.loads(get(f'https://api.polyhaven.com/info/{aid}'))
    files = json.loads(get(f'https://api.polyhaven.com/files/{aid}'))
    d = os.path.join(OUT, aid)
    kind = info['type']  # 0 hdri, 1 texture, 2 model
    if kind == 0:
        f = files['hdri'][res]['hdr']; save(f['url'], os.path.join(d, f'{aid}_{res}.hdr'))
    elif kind == 2:
        g = files['gltf'][res]['gltf']
        save(g['url'], os.path.join(d, os.path.basename(g['url'])))
        for rel, inc in g.get('include', {}).items():
            save(inc['url'], os.path.join(d, rel))
    else:
        for mapname in ('Diffuse', 'nor_gl', 'Rough', 'AO', 'arm'):
            if mapname in files and res in files[mapname]:
                f = files[mapname][res].get('jpg') or files[mapname][res].get('png')
                save(f['url'], os.path.join(d, os.path.basename(f['url'])))
    authors = ', '.join(info.get('authors', {}).keys())
    return f"- {info['name']} (`{aid}`) by {authors} - Poly Haven, CC0 - https://polyhaven.com/a/{aid}"

if __name__ == '__main__':
    args = sys.argv[1:]; res = '1k'
    if args and args[0] == '--res': res = args[1]; args = args[2:]
    credits = os.path.join(ROOT, 'CREDITS.md')
    existing = open(credits).read() if os.path.exists(credits) else '# Credits\n\nEverything not listed here was made for this project.\n\n'
    for a in args:
        try:
            line = fetch(a, res); print('ok', a)
            if f'`{a}`' not in existing: existing += line + '\n'
        except Exception as e:
            print('FAIL', a, e)
    open(credits, 'w').write(existing)
