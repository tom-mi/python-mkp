# python-mkp

![ci](https://github.com/tom-mi/python-mkp/workflows/ci/badge.svg)
![release](https://github.com/tom-mi/python-mkp/workflows/release/badge.svg)
[![PyPI version](https://badge.fury.io/py/mkp.svg)](https://badge.fury.io/py/mkp)

Pack or unpack [Check_MK](https://mathias-kettner.de/check_mk.html) mkp files.

The purpose of this library is to generate mkp files from source without having to set up a complete Check\_MK instance.
It is not intended for installing mkp files to a Check\_MK site.

## Installation

```sh
pip install mkp
```

## Usage

### Automatically pack mkp package

Create a executable script in the the top directory, e.g. `dist.py`

```python
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
```

Create a directory structure as follows:

```text
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
```

Empty directories can be omitted. Running `dist.py` will pack all files in the
directories listed above to a mkp package with the canonical name and the
specified metadata. The mkp file will be written to the `dist` directory.

### Extract mkp package

```python
import mkp

package = mkp.load_file('foo-1.0.mkp')
print(package.info)
package.extract_files('path/to/somewhere')
```

### Pack files to mkp package

In contrast to `dist`, this provides the possibility to manually select the
files by replacing `find_files`. It is also possible to choose a different
output filename.

```python
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
```

### Advanced usage

Exclude files when packing using [regular expressions](https://docs.python.org/3/library/re.html):

```python
files = mkp.find_files('path/to/files', exclude_patterns=[r'.*\.pyc$', '__pycache__'])
```

or

```python
dist({
# ...
}, exclude_patterns=[r'.*\.pyc$', '__pycache__'])
```

## Development Setup

Install development dependencies into local environment (`${repo_root}/.venv`):

```sh
scripts/bootstrap
```

Run all tests with tox:

```sh
scripts/test
# or
source .venv/bin/activate
tox
```

Run tests of current python version with pytest:

```sh
source .venv/bin/activate
pytest
```

Release new version:

```sh
git tag <new_version>
git push --tags
```

## License

This software is licensed under GPLv2.
