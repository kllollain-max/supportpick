"""Read-only recovery of the exact Pages bytes, never a reconstructed release."""
import argparse
import hashlib
import json
import os
import re
import tarfile
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

API = 'https://api.github.com/repos/kllollain-max/supportpick'


def verify_origin(run, jobs, sha):
    if run.get('head_sha') != sha or run.get('path') != '.github/workflows/deploy-approved.yml':
        raise ValueError('unexpected_release_origin')
    # A post-publication audit can fail even though deployment succeeded.
    if not any(step.get('conclusion') == 'success' and 'actions/deploy-pages@v4' in step.get('name', '')
               for job in jobs.get('jobs', []) for step in job.get('steps', [])):
        raise ValueError('publication_not_confirmed')


def validate_run(run_id, sha):
    if not re.fullmatch(r'[1-9][0-9]*', str(run_id)):
        raise ValueError('invalid_run_id')
    headers = {'Accept': 'application/vnd.github+json',
               'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN']}
    def get(path):
        with urlopen(Request(API + path, headers=headers), timeout=30) as response:
            return json.load(response)
    verify_origin(get('/actions/runs/' + str(run_id)), get('/actions/runs/' + str(run_id) + '/jobs'), sha)


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name:
        raise ValueError('unsafe_archive_path')
    return path


def restore(archive, output, sha):
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('invalid_source_sha')
    output = Path(output)
    if output.exists() and (output.is_symlink() or not output.is_dir() or any(output.iterdir())):
        raise ValueError('output_not_empty')
    with tarfile.open(archive) as bundle:
        members = bundle.getmembers()
        if len(members) > 50000 or sum(m.size for m in members) > 400 * 1024 * 1024:
            raise ValueError('archive_budget_exceeded')
        files = set()
        for member in members:
            name = str(relative(member.name))
            if not member.isdir() and not member.isfile():
                raise ValueError('archive_links_or_special_files')
            if member.isfile():
                if name in files:
                    raise ValueError('duplicate_archive_file')
                files.add(name)
        output.mkdir(parents=True, exist_ok=True)
        bundle.extractall(output, filter='data')
    manifest = json.loads((output / 'site-manifest.json').read_text())
    if manifest.get('sourceRevision') != sha:
        raise ValueError('artifact_source_mismatch')
    digests = manifest.get('files', {})
    if not isinstance(digests, dict) or files != set(digests) | {'site-manifest.json'}:
        raise ValueError('artifact_inventory_mismatch')
    for name, digest in digests.items():
        path = output / relative(name)
        if not re.fullmatch(r'[0-9a-f]{64}', str(digest)) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('artifact_content_mismatch:' + name)
    return {'sourceRevision': sha, 'generation': manifest['generation'], 'verifiedFiles': len(files)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--run-id')
    parser.add_argument('--archive')
    parser.add_argument('--output')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.expected_sha):
        raise ValueError('invalid_source_sha')
    if args.run_id:
        validate_run(args.run_id, args.expected_sha)
        print('Published run identity verified')
    elif args.archive and args.output:
        print(json.dumps(restore(args.archive, args.output, args.expected_sha)))
    else:
        parser.error('provide --run-id or both --archive and --output')
