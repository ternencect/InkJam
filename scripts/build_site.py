"""Build InkJam from the public-file manifest and a verified Release video."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import argparse, hashlib, json, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def safe(base, name):
    path = (base / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(base.resolve()):
        raise ValueError(f'Invalid public path: {name}')
    return path

class References(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []
    def handle_starttag(self, tag, attrs):
        self.refs.extend(value for key, value in attrs if key in ('href', 'src', 'poster') and value)

def build(video, out):
    site = ROOT / 'site'
    manifest = json.loads((site / 'site-manifest.json').read_text())
    catalog = json.loads((site / 'library/catalog.json').read_text())
    for work in catalog['works']:
        scores = {score['id']: score for score in work['scores']}
        for score in scores.values():
            for asset in score['assets'].values():
                assert digest(safe(site, asset['path'])) == asset['sha256'], 'Score hash mismatch'
        for perf in work['performances']:
            score = scores[perf['score_id']]
            media = json.loads(safe(site, perf['media_manifest_path']).read_text())
            validation = json.loads(safe(site, perf['validation_path']).read_text())
            assert media['work_id'] == work['id']
            assert media['score_id'] == score['id']
            assert media['performance_id'] == perf['id']
            assert perf['score_sha256'] == score['assets']['musicxml']['sha256'] == media['score_sha256'] == validation['source_score_sha256']
            assert perf['video_sha256'] == media['sha256'] == validation['movie_sha256']
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a new or empty output directory.')
    out.mkdir(parents=True, exist_ok=True)
    for name, expected in manifest['files'].items():
        src = video if name == manifest['video_path'] else safe(site, name)
        assert src.is_file(), f'Missing file: {name}'
        assert src.stat().st_size == expected['bytes'] and digest(src) == expected['sha256'], f'File hash mismatch: {name}'
        target = safe(out, name); target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
    shutil.copyfile(site / 'site-manifest.json', out / 'site-manifest.json')
    for page in out.rglob('*.html'):
        refs = References(); refs.feed(page.read_text())
        for ref in refs.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc or not url.path: continue
            target = (page.parent / unquote(url.path)).resolve()
            assert target.is_relative_to(out.resolve()) and target.is_file(), f'Broken link: {page.name}: {ref}'
    print(json.dumps({'status': 'passed', 'files': len(manifest['files']), 'video_sha256': digest(video), 'output': str(out)}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--video', type=Path)
    group.add_argument('--download-release', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'site/site-manifest.json').read_text())
    if args.download_release:
        with tempfile.TemporaryDirectory(prefix='inkjam-media-') as tmp:
            filename = Path(manifest['video_path']).name
            subprocess.run(['gh', 'release', 'download', manifest['release_tag'], '--repo', 'ternencect/InkJam', '--pattern', filename, '--dir', tmp], check=True)
            build(Path(tmp) / filename, args.output)
    else:
        build(args.video, args.output)

if __name__ == '__main__':
    main()
