import argparse
import os
from mkp import load_file


def main():
    args = _parse_args()
    package = load_file(args.mkp_file)
    extract_path = _get_extract_path(args.output_dir, args.no_prefix, package)
    os.makedirs(extract_path, exist_ok=True)
    package.extract_files(extract_path)
    _write_info_files(package, extract_path)


def _parse_args():
    parser = argparse.ArgumentParser(description='Extract a Check_MK mkp package. '
                                                 'By default, a directory with the package name and version is created in the output '
                                                 'directory.')
    parser.add_argument('mkp_file', help='Path to the mkp package file.')
    parser.add_argument('-o', '--output-dir', default='.',
                        help='Output directory (default: current directory)')
    parser.add_argument('--no-prefix', action='store_true',
                        help='Do not create a package prefix directory')
    return parser.parse_args()


def _get_extract_path(output_dir, no_prefix, package):
    if no_prefix:
        return output_dir
    name = package.info.get('name', 'package')
    version = package.info.get('version', 'unknown')
    dir_name = f"{name}-{version}"
    return os.path.join(output_dir, dir_name)


def _write_info_files(package, extract_path):
    info_path = os.path.join(extract_path, "info")
    info_json_path = os.path.join(extract_path, "info.json")
    with open(info_path, "w") as f:
        import pprint
        f.write(pprint.pformat(package.info))
    if package.json_info is not None:
        import json
        with open(info_json_path, "w") as f:
            json.dump(package.json_info, f, indent=2)
    else:
        with open(info_json_path, "w") as f:
            f.write("{}\n")


if __name__ == "__main__":
    main()
