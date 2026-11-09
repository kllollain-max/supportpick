"""Offline, read-only verification of SupportPick runtime ZIP backups.
No network, extraction, or production changes.
"""
import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import PurePosixPath

MAX_MEMBERS = 10000
MAX_TOTAL_BYTES = 350 * 1024 * 1024
MAX_MEMBER_BYTES = 150 * 1024 * 1024
MAX_MANIFEST_BYTES = 200 * 1024
GENERATION = re.compile(r"gov24-[0-9]+-[0-9]+\Z")

def _read_json(archive, name, max_bytes=MAX_MANIFEST_BYTES):
    info = archive.getinfo(name)
    if info.file_size > max_bytes:
        raise ValueError("metadata_too_large")
    return json.loads(archive.read(info))

def _archive_digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def verify_zip(path):
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if not 1 <= len(infos) <= MAX_MEMBERS:
            raise ValueError("invalid_archive_member_count")
        names = set()
        total = 0
        for info in infos:
            name = info.filename
            pp = PurePosixPath(name)
            mode = info.external_attr >> 16
            if (not name or '\\' in name or pp.is_absolute() or '..' in pp.parts
                    or any(x in ('', '.') for x in name.split('/'))
                    or info.is_dir() or stat.S_ISLNK(mode)
                    or name in names or info.flag_bits & 1):
                raise ValueError("unsafe_archive_entry")
            names.add(name)
            total += info.file_size
            if info.file_size > MAX_MEMBER_BYTES or total > MAX_TOTAL_BYTES:
                raise ValueError("archive_size_limit")
        if 'current.json' not in names:
            raise ValueError("missing_pointer")
        pointer = _read_json(archive, 'current.json')
        generation = pointer.get('generation')
        if not isinstance(generation, str) or not GENERATION.fullmatch(generation):
            raise ValueError("invalid_generation")
        if pointer.get('version') != 1 or pointer.get('path') != 'snapshots/' + generation:
            raise ValueError("invalid_pointer")
        if type(pointer.get('count')) is not int or pointer['count'] <= 0:
            raise ValueError("invalid_count")
        manifest_files = sorted(n for n in names if n.endswith('/manifest.json'))
        if len(manifest_files) != 2:
            raise ValueError("invalid_generation_count")
        verified_files = 0
        generations = []
        permitted = {'current.json', 'status.json'}
        permitted.update(manifest_files)
        for manifest_name in manifest_files:
            prefix = manifest_name.rsplit('/', 1)[0]
            gen = prefix.removeprefix('snapshots/')
            if prefix != 'snapshots/' + gen or not GENERATION.fullmatch(gen):
                raise ValueError("invalid_snapshot_path")
            raw = archive.read(manifest_name)
            if gen == generation and hashlib.sha256(raw).hexdigest() != pointer.get('manifestSha256'):
                raise ValueError("pointer_manifest_digest_mismatch")
            manifest = json.loads(raw)
            if manifest.get('generation') != gen or manifest.get('version') != 1:
                raise ValueError("invalid_manifest")
            files = manifest.get('files')
            if not isinstance(files, dict) or not files:
                raise ValueError("invalid_manifest_files")
            declared = {prefix + '/' + f for f in files}
            actual = {n for n in names if n.startswith(prefix + '/') and n != manifest_name}
            if declared != actual:
                raise ValueError("manifest_file_set_mismatch")
            for relative, expected in files.items():
                if (not isinstance(relative, str) or relative.startswith('/') or '\\' in relative
                        or '..' in PurePosixPath(relative).parts
                        or not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected)):
                    raise ValueError("unsafe_manifest_entry")
                h = hashlib.sha256()
                with archive.open(prefix + '/' + relative) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        h.update(block)
                if h.hexdigest() != expected:
                    raise ValueError("snapshot_digest_mismatch")
                verified_files += 1
            permitted.update(declared)
            if gen == generation:
                feed = _read_json(archive, prefix + '/data.json', MAX_MEMBER_BYTES)
                if feed.get('generation') != gen or len(feed.get('items', [])) != pointer['count']:
                    raise ValueError("pointer_data_mismatch")
            generations.append(gen)
        if names - permitted:
            raise ValueError("undeclared_archive_files")
        return {'status': 'passed', 'generation': generation, 'items': pointer['count'],
                'generations': sorted(generations), 'verified_files': verified_files,
                'members': len(infos), 'archive_sha256': _archive_digest(path)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zip_path')
    args = parser.parse_args()
    try:
        result = verify_zip(args.zip_path)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, OSError, zipfile.BadZipFile, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'failed', 'reason': type(exc).__name__}, sort_keys=True))
        return 1

if __name__ == '__main__':
    sys.exit(main())
