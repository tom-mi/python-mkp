import ast
import io
import re
import tarfile

import pytest

import mkp

DIRECTORIES = [
    'agents', 'checkman', 'checks', 'doc', 'inventory', 'notifications',
    'pnp-templates', 'web', 'lib', 'agent_based',
]


@pytest.fixture
def sample_files(tmpdir):
    tmpdir.join('agents', 'special', 'agent_test').write_binary(b'hello', ensure=True)
    tmpdir.join('checks', 'foo').write_binary(b'Check Me!', ensure=True)


@pytest.fixture
def sample_info():
    return {
        'author': 'John Doe',
        'name': 'foo',
        'version': '42',
        'version.min_required': '1.2.6p5',
        'version.usable_until': None,
    }


def test_pack_to_bytes(tmpdir):
    info = {
        'files': {'agents': ['special/agent_test']},
        'title': 'Test package',
    }
    tmpdir.join('agents', 'special', 'agent_test').write_binary(b'hello', ensure=True)

    data = mkp.pack_to_bytes(info, str(tmpdir))

    bytes_io = io.BytesIO(data)
    archive = tarfile.open(fileobj=bytes_io)

    info_file = archive.extractfile('info').read()
    extracted_info = ast.literal_eval(info_file.decode())
    assert extracted_info['files'] == info['files']
    assert extracted_info['title'] == info['title']
    assert extracted_info['version.packaged'] == 'python-mkp'

    agents_archive_file = archive.extractfile('agents.tar')
    agents_archive = tarfile.open(fileobj=agents_archive_file, mode='r:')
    agent_file = agents_archive.extractfile('special/agent_test')
    assert agent_file.read() == b'hello'


def test_pack_to_file(tmpdir):
    info = {
        'files': {'agents': ['special/agent_test']},
        'title': 'Test package',
    }
    tmpdir.join('agents', 'special', 'agent_test').write_binary(b'hello', ensure=True)

    outfile = tmpdir.join('test.mkp')

    mkp.pack_to_file(info, str(tmpdir), str(outfile))

    archive = tarfile.open(str(outfile))

    info_file = archive.extractfile('info').read()
    extracted_info = ast.literal_eval(info_file.decode())
    assert extracted_info['files'] == info['files']
    assert extracted_info['title'] == info['title']
    assert extracted_info['version.packaged'] == 'python-mkp'

    agents_archive_file = archive.extractfile('agents.tar')
    agents_archive = tarfile.open(fileobj=agents_archive_file, mode='r:')
    agent_file = agents_archive.extractfile('special/agent_test')
    assert agent_file.read() == b'hello'


def test_find_files_searches_all_directories(tmpdir):
    for directory in DIRECTORIES:
        tmpdir.join(directory, 'test').write_binary(b'Foo', ensure=True)

    result = mkp.find_files(str(tmpdir))
    for directory in DIRECTORIES:
        assert result[directory] == ['test']


def test_find_files_ignores_files_outsider_known_directories(tmpdir):
    # given
    tmpdir.join('unknown_dir', 'test').write_binary(b'Foo', ensure=True)

    # when
    result = mkp.find_files(str(tmpdir))

    # then
    for directory in DIRECTORIES:
        assert result[directory] == []


def test_find_files_with_custom_directory_list(tmpdir):
    # given
    tmpdir.join('agent', 'test').write_binary(b'Foo', ensure=True)
    tmpdir.join('custom_dir', 'test').write_binary(b'Foo', ensure=True)
    tmpdir.join('other_dir', 'test').write_binary(b'Foo', ensure=True)

    # when
    result = mkp.find_files(str(tmpdir), directories=['custom_dir'])

    # then
    assert result['custom_dir'] == ['test']


def test_find_files_searches_subdirectories(tmpdir):
    tmpdir.join('agents', 'special', 'agent_test').write_binary(b'hello', ensure=True)

    result = mkp.find_files(str(tmpdir))

    assert result['agents'] == ['special/agent_test']


def test_find_files_ignores_hidden_files_and_dirs(tmpdir):
    tmpdir.join('agents', '.hidden').write_binary(b'hello', ensure=True)
    tmpdir.join('agents', 'test~').write_binary(b'hello', ensure=True)
    tmpdir.join('agents', '.hidden_dir', 'visible_file').write_binary(b'hello', ensure=True)

    result = mkp.find_files(str(tmpdir))

    assert result['agents'] == []


def test_find_files_omits_files_matching_an_exclude_pattern(tmpdir):
    # given
    a = re.compile(r'.*\.pyc')
    exclude_patterns = [r'.*file_to_exclude$', r'dir-to-omit/.*']
    tmpdir.join('agents', 'file_to_include').write_binary(b'hello', ensure=True)
    tmpdir.join('agents', 'file_to_exclude').write_binary(b'hello', ensure=True)
    tmpdir.join('agents', 'file_to_exclude.not').write_binary(b'hello', ensure=True)
    tmpdir.join('agents', 'dir-to-omit', 'file_inside').write_binary(b'hello', ensure=True)

    # when
    result = mkp.find_files(str(tmpdir), exclude_patterns=exclude_patterns)

    # then
    assert result['agents'] == ['file_to_exclude.not', 'file_to_include']


def test_find_files_includes_all_regular_directories_for_mode_include_all(tmpdir):
    # given
    tmpdir.join('agents', 'test').write_binary(b'Foo', ensure=True)
    tmpdir.join('custom_dir', 'test').write_binary(b'Foo', ensure=True)
    tmpdir.join('other_dir', 'test').write_binary(b'Foo', ensure=True)
    tmpdir.join('.hidden_dir', 'test').write_binary(b'Foo', ensure=True)

    # when
    result = mkp.find_files(str(tmpdir), directories=mkp.INCLUDE_ALL)

    # then
    assert result['agents'] == ['test']
    assert result['custom_dir'] == ['test']
    assert result['other_dir'] == ['test']
    assert '.hidden_dir' not in result


def test_pack_and_unpack_covers_all_known_directories(tmpdir):
    info = {
        'files': {key: ['test'] for key in DIRECTORIES},
    }
    source = tmpdir.join('source').mkdir()
    dest = tmpdir.join('dest').mkdir()

    for directory in DIRECTORIES:
        source.join(directory, 'test').write_binary(b'Foo', ensure=True)

    package_bytes = mkp.pack_to_bytes(info, str(source))
    package = mkp.load_bytes(package_bytes)
    package.extract_files(str(dest))

    for directory in DIRECTORIES:
        assert dest.join(directory, 'test').exists()


def test_dist(tmpdir, sample_files, sample_info):
    mkp.dist(sample_info, str(tmpdir))

    assert tmpdir.join('dist', 'foo-42.mkp').exists()
    package = mkp.load_file(str(tmpdir.join('dist', 'foo-42.mkp')))
    assert package.info['author'] == 'John Doe'
    assert package.info['name'] == 'foo'
    assert package.info['files']['agents'] == ['special/agent_test']
    assert package.info['files']['checks'] == ['foo']
    assert package.info['num_files'] == 2
    assert package.info['version'] == '42'
    assert package.info['version.packaged'] == 'python-mkp'
    assert package.info['version.min_required'] == '1.2.6p5'
    assert package.info['version.usable_until'] is None


def test_dist_with_exclude_patterns(tmpdir, sample_files, sample_info):
    # given
    exclude_patterns = [r'special/.*']

    # when
    mkp.dist(sample_info, str(tmpdir), exclude_patterns=exclude_patterns)

    # then
    assert tmpdir.join('dist', 'foo-42.mkp').exists()
    package = mkp.load_file(str(tmpdir.join('dist', 'foo-42.mkp')))
    assert package.info['author'] == 'John Doe'
    assert package.info['files']['agents'] == []
    assert package.info['files']['checks'] == ['foo']
    assert package.info['num_files'] == 1


def test_dist_with_include_all(tmpdir, sample_files, sample_info):
    # given
    tmpdir.join('custom_dir', 'custom_file').write_binary(b'Custom', ensure=True)

    # when
    mkp.dist(sample_info, str(tmpdir), directories=mkp.INCLUDE_ALL)

    # then
    assert tmpdir.join('dist', 'foo-42.mkp').exists()
    package = mkp.load_file(str(tmpdir.join('dist', 'foo-42.mkp')))
    assert package.info['author'] == 'John Doe'
    assert package.info['files']['agents'] == ['special/agent_test']
    assert package.info['files']['checks'] == ['foo']
    assert package.info['files']['custom_dir'] == ['custom_file']
    assert package.info['num_files'] == 3


def test_dist_with_custom_directories(tmpdir, sample_files, sample_info):
    # when
    mkp.dist(sample_info, str(tmpdir), directories=['agents', 'custom_dir'])

    # then
    assert tmpdir.join('dist', 'foo-42.mkp').exists()
    package = mkp.load_file(str(tmpdir.join('dist', 'foo-42.mkp')))
    assert package.info['author'] == 'John Doe'
    assert package.info['files']['agents'] == ['special/agent_test']
    assert 'checks' not in package.info['files']
    assert package.info['num_files'] == 1


def test_dist_json(tmpdir, sample_files, sample_info):
    mkp.dist(sample_info, str(tmpdir))

    assert tmpdir.join('dist', 'foo-42.mkp').exists()
    package = mkp.load_file(str(tmpdir.join('dist', 'foo-42.mkp')))
    assert package.json_info['author'] == 'John Doe'
    assert package.json_info['name'] == 'foo'
    assert package.json_info['files']['agents'] == ['special/agent_test']
    assert package.json_info['files']['checks'] == ['foo']
    assert package.json_info['num_files'] == 2
    assert package.json_info['version'] == '42'
    assert package.json_info['version.packaged'] == 'python-mkp'
    assert package.json_info['version.min_required'] == '1.2.6p5'
    assert package.json_info['version.usable_until'] is None


def test_dist_uses_script_path_when_no_path_is_given(tmpdir):
    script = tmpdir.join('dist.py')
    script.write_text(u'''#!/usr/bin/env python

from mkp import dist


dist({
    'author': 'John Doe',
    'name': 'foo',
    'version': '42',
})
''', 'utf-8')
    script.chmod(0o700)
    tmpdir.join('agents', 'special', 'agent_test').write_binary(b'hello', ensure=True)
    tmpdir.join('checks', 'foo').write_binary(b'Check Me!', ensure=True)

    script.sysexec()

    assert tmpdir.join('dist', 'foo-42.mkp').exists()
    package = mkp.load_file(str(tmpdir.join('dist', 'foo-42.mkp')))
    assert package.info['author'] == 'John Doe'
    assert package.info['name'] == 'foo'
    assert package.info['files']['agents'] == ['special/agent_test']
    assert package.info['files']['checks'] == ['foo']
    assert package.info['version'] == '42'
    assert package.info['version.packaged'] == 'python-mkp'
    assert package.info['num_files'] == 2
