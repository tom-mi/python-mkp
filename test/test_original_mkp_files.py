import mkp


def test_load_bytes(original_mkp_file):
    package = mkp.load_bytes(original_mkp_file)

    assert type(package) == mkp.Package
    assert package.info['title'] == 'Title of test'


def test_load_file(original_mkp_file, tmpdir):
    tmpdir.join('test.mkp').write_binary(original_mkp_file)

    package = mkp.load_file(str(tmpdir.join('test.mkp')))

    assert type(package) == mkp.Package
    assert package.info['title'] == 'Title of test'
    assert package.json_info is None


def test_extract_files(original_mkp_file, tmpdir):
    package = mkp.load_bytes(original_mkp_file)

    package.extract_files(str(tmpdir))

    assert tmpdir.join('agents', 'special', 'agent_test').exists()
    assert tmpdir.join('checkman', 'test').exists()
    assert tmpdir.join('checkman', 'test').open().read() == 'title: Hello World!\n'


def test_load_bytes_with_info_json(original_mkp_file_with_info_json):
    package = mkp.load_bytes(original_mkp_file_with_info_json)

    assert type(package) == mkp.Package
    assert package.info['title'] == 'Title of test'
    assert package.json_info['title'] == 'Title of test'
