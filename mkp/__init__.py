import ast
import io
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


def pack_to_bytes(info, path):
    _patch_info(info)
    bytes_io = io.BytesIO()
    with tarfile.open(fileobj=bytes_io, mode='w:gz') as archive:
        info_data = pprint.pformat(info).encode()
        tarinfo, fileobj = _create_tarinfo_and_buffer(info_data, 'info')
        archive.addfile(tarinfo, fileobj=fileobj)

        for directory in _DIRECTORIES:
            files = info['files'].get(directory, [])
            if not files:
                continue

            directory_archive = _create_directory_archive(os.path.join(path, directory), files)
            tarinfo, fileobj = _create_tarinfo_and_buffer(directory_archive, directory + '.tar')
            archive.addfile(tarinfo, fileobj)

    return bytes_io.getvalue()


def _patch_info(info):
    info['version.packaged'] = _VERSION_PACKAGED


def _create_directory_archive(path, files):
    bytes_io = io.BytesIO()
    with tarfile.open(fileobj=bytes_io, mode='w') as archive:
        for filename in files:
            archive.add(os.path.join(path, filename), arcname=filename)

    return bytes_io.getvalue()


def _create_tarinfo_and_buffer(data, filename):
    tarinfo = tarfile.TarInfo(filename)
    tarinfo.size = len(data)
    bytes_io = io.BytesIO(data)
    return tarinfo, bytes_io


class Package(object):

    def __init__(self, fileobj):
        self.archive = tarfile.open(fileobj=fileobj)
        self._info = self._load_info()

    def _load_info(self):
        info_file = self.archive.extractfile('info')
        return ast.literal_eval(info_file.read().decode())

    @property
    def info(self):
        return self._info

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
