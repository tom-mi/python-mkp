# python-mkp

![ci](https://github.com/tom-mi/python-mkp/workflows/ci/badge.svg)
![release](https://github.com/tom-mi/python-mkp/workflows/release/badge.svg)
[![PyPI version](https://badge.fury.io/py/mkp.svg)](https://badge.fury.io/py/mkp)

Pack or unpack [Check_MK](https://mathias-kettner.de/check_mk.html) mkp files.

The purpose of this library is to generate mkp files from source without having to set up a complete Check\_MK instance. It is not intended for installing mkp files to a Check\_MK site.
## Installation

    pip install mkp

## Usage

### Automatically pack mkp package

Create a executable script in the the top directory, e.g. `dist.py`

    #!/usr/bin/env python

    from mkp import dist

    dist({
        'author': 'John Doe',
        'description': 'Test the automatic creation of packages',
        'download_url': 'http://example.com/',
        'name': 'test',
        'title': 'Test',
        'version': '1.0',
        'version.min_required': '1.2.3',
    })

Create a directory structure as follows:

    ├── agents/
    ├── agent_based/
    ├── checkman/
    ├── checks/
    ├── doc/
    ├── inventory/
    ├── lib/
    ├── notifications/
    ├── pnp-templates/
    ├── web/
    └── dist.py

Empty directories can be omitted. Running `dist.py` will pack all files in the
directories listed above to a mkp package with the canonical name and the
specified metadata. The mkp file will be written to the `dist` directory.

### Extract mkp package

    import mkp

    package = mkp.load_file('foo-1.0.mkp')
    print(package.info)
    package.extract_files('path/to/somewhere')

### Pack files to mkp package

In contrast to `dist`, this provides the possibility to manually select the
files by replacing `find_files`. It is also possible to choose a different
output filename.

    import mkp

    info = {
      'author': 'tom-mi',
      'description': 'Test the system',
      'download_url': 'http://example.com/',
      'files': mkp.find_files('path/to/files'),
      'name': 'test',
      'title': 'Test',
      'version': '1.0',
      'version.min_required': '1.2.3',
    }
    mkp.pack_to_file(info, 'path/to/files', 'test-1.0.mkp')

## License

This software is licensed under GPLv2.
