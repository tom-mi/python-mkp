import argparse
import os
import textwrap
from mkp import DIRECTORIES


def main():
    args = _parse_args()
    cwd = os.getcwd()
    if not args.ignore_non_empty:
        _ensure_empty_directory(cwd)

    for directory in DIRECTORIES:
        os.makedirs(os.path.join(cwd, directory), exist_ok=True)
    dist_py_path = os.path.join(cwd, 'dist.py')
    with open(dist_py_path, 'w') as f:
        f.write(_dist_py_template(args))
    os.chmod(dist_py_path, 0o755)


def _parse_args():
    parser = argparse.ArgumentParser(description='Create a Check_MK mkp project skeleton in the current directory.')
    parser.add_argument('--name', default='example', help='Package name')
    parser.add_argument('--author', default='John Doe', help='Author name')
    parser.add_argument('--version', default='0.1.0', help='Package version')
    parser.add_argument('--description', default='Example package', help='Package description')
    parser.add_argument('--title', default='Example', help='Package title')
    parser.add_argument('--download_url', default='http://example.com/', help='Download URL')
    parser.add_argument('--min_required', default='1.2.3', help='Minimum required version')
    parser.add_argument('--ignore-non-empty', action='store_true', help='Allow running in non-empty directories')
    return parser.parse_args()


def _dist_py_template(args):
    return textwrap.dedent(f"""
        #!/usr/bin/env python

        from mkp import dist

        dist({{
            "author": "{args.author}",
            "description": "{args.description}",
            "download_url": "{args.download_url}",
            "name": "{args.name}",
            "title": "{args.title}",
            "version": "{args.version}",
            "version.min_required": "{args.min_required}",
        }})
        """).lstrip()


def _ensure_empty_directory(path):
    entries = [e for e in os.listdir(path) if not e.startswith('.')]
    if entries:
        print("Error: The current directory is not empty. Use --ignore-non-empty to override.")
        exit(1)


if __name__ == "__main__":
    main()
