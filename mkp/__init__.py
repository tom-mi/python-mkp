import ast
import io
import json
import os
import os.path
import pprint
import tarfile

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

_DIRECTORIES = [
    'agents', 'checkman', 'checks', 'doc', 'inventory', 'notifications',
    'pnp-templates', 'web',
]

_VERSION_PACKAGED = 'python-mkp'

_DIST_DIR = 'dist'


def dist(info, path=None):
    if not path:
        import __main__ as main
        path = os.path.dirname(os.path.realpath(main.__file__))

    info['files'] = find_files(path)
    info['num_files'] = sum(len(file_list) for file_list in info['files'].values())
    dist_dir = os.path.join(path, _DIST_DIR)
    filename = '{}-{}.mkp'.format(info['name'], info['version'])

    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)

    pack_to_file(info, path, os.path.join(dist_dir, filename))


def load_file(path):
    file_io = open(path, 'rb')
    return Package(file_io)


def load_bytes(data):
    bytes_io = io.BytesIO(data)
    return Package(bytes_io)


def find_files(path):
    result = {}
    for directory in _DIRECTORIES:
        result[directory] = _find_files_in_directory(os.path.join(path, directory))

    return result


def _find_files_in_directory(path):
    result = []
    for root, dirs, files in os.walk(path):
        for dirname in dirs:
            if dirname.startswith('.'):
                dirs.remove(dirname)
        for filename in files:
            if filename.startswith('.'):
                continue
            elif filename.endswith('~'):
                continue
            abspath = os.path.join(root, filename)
            relpath = os.path.relpath(abspath, start=path)
            result.append(relpath)
    return result


def pack_to_file(info, path, outfile):
    with open(outfile, 'wb') as f:
        f.write(pack_to_bytes(info, path))


def pack_to_bytes(info, path):
    _patch_info(info)
    bytes_io = io.BytesIO()
    with tarfile.open(fileobj=bytes_io, mode='w:gz') as archive:
        _add_to_archive(archive, 'info', encode_info(info))
        _add_to_archive(archive, 'info.json', encode_info_json(info))

        for directory in _DIRECTORIES:
            files = info['files'].get(directory, [])
            if not files:
                continue

            directory_archive = _create_directory_archive(os.path.join(path, directory), files)
            _add_to_archive(archive, directory + '.tar', directory_archive)

    return bytes_io.getvalue()


def _patch_info(info):
    info['version.packaged'] = _VERSION_PACKAGED


def _create_directory_archive(path, files):
    bytes_io = io.BytesIO()
    with tarfile.open(fileobj=bytes_io, mode='w') as archive:
        for filename in files:
            archive.add(os.path.join(path, filename), arcname=filename)

    return bytes_io.getvalue()


def _add_to_archive(archive, filename, data):
    tarinfo, fileobj = _create_tarinfo_and_buffer(data, filename)
    archive.addfile(tarinfo, fileobj=fileobj)


def _create_tarinfo_and_buffer(data, filename):
    tarinfo = tarfile.TarInfo(filename)
    tarinfo.size = len(data)
    bytes_io = io.BytesIO(data)
    return tarinfo, bytes_io


def encode_info(info):
    return pprint.pformat(info).encode()


def encode_info_json(info):
    return json.dumps(info).encode()


def decode_info(info_bytes):
    return ast.literal_eval(info_bytes.decode())


class Package(object):

    def __init__(self, fileobj):
        self.archive = tarfile.open(fileobj=fileobj)
        self._info = self._get_info()
        self._json_info = self._get_json_info()

    def _get_info(self):
        info_file = self.archive.extractfile('info')
        return decode_info(info_file.read())

    def _get_json_info(self):
        try:
            info_file = self.archive.extractfile('info.json')
            return json.loads(info_file.read())
        except KeyError:
            return None

    @property
    def info(self):
        return self._info

    @property
    def json_info(self):
        return self._json_info

    def extract_files(self, path):
        for directory in _DIRECTORIES:
            self._extract_files_in_directory(path, directory)

    def _extract_files_in_directory(self, path, directory):
        files = self.info['files'].get(directory, [])

        if not files:
            return

        target_path = os.path.join(path, directory)
        os.makedirs(target_path)
        dir_archive_file = self.archive.extractfile(directory + '.tar')

        with tarfile.open(fileobj=dir_archive_file) as archive:
            members = [member for member in archive.getmembers() if member.name in files]
            archive.extractall(path=target_path, members=members)
