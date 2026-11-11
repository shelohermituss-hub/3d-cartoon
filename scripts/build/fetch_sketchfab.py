"""Download Sketchfab models (glTF) into assets/sketchfab/<uid>/ and log credits.

The API token is never stored in the project: the session's network proxy adds it to requests
to api.sketchfab.com. Only CC0 and CC-BY models are accepted (CC-BY = credit required, see CREDITS.md).
Usage: python fetch_sketchfab.py UID [UID ...]
"""
import io, json, os, sys, urllib.request, zipfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'sketchfab')
OK_LICENCES = ('CC Attribution', 'CC0 Public Domain')


def get(url, auth=False):
    h = {'User-Agent': 'cartoon-short-builder'}
    if auth:
        h['Authorization'] = 'Token proxy-injected'   # replaced by the proxy with the real token
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=300).read()


def fetch(uid):
    info = json.loads(get(f'https://api.sketchfab.com/v3/models/{uid}'))
    lic = info['license']['label'] if isinstance(info.get('license'), dict) else str(info.get('license'))
    if lic not in OK_LICENCES:
        raise SystemExit(f'{uid}: licence "{lic}" not accepted')
    dl = json.loads(get(f'https://api.sketchfab.com/v3/models/{uid}/download', auth=True))
    url = dl['gltf']['url']
    d = os.path.join(OUT, uid)
    os.makedirs(d, exist_ok=True)
    zipfile.ZipFile(io.BytesIO(get(url))).extractall(d)
    who = info['user']['displayName']
    return (f"- \"{info['name']}\" by {who} - Sketchfab, {lic}"
            f" ({'https://creativecommons.org/licenses/by/4.0/' if 'Attribution' in lic else 'public domain'})"
            f" - https://sketchfab.com/3d-models/{uid} (`{uid}`)")


if __name__ == '__main__':
    credits = os.path.join(ROOT, 'CREDITS.md')
    text = open(credits).read()
    for uid in sys.argv[1:]:
        line = fetch(uid)
        print('ok', line)
        if f'`{uid}`' not in text:
            text += line + '\n'
    open(credits, 'w').write(text)
