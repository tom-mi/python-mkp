# python-mkp

[![Build Status](https://travis-ci.org/tom-mi/python-mkp.svg?branch=master)](https://travis-ci.org/tom-mi/python-mkp)

Pack or unpack [Check_MK](https://mathias-kettner.de/check_mk.html) mkp files.

The purpose of this library is to generate mkp files from source without having to set up a complete Check\_MK instance. It is not intended for installing mkp files to a Check\_MK site.
## Installation

    pip install mkp
  
## Usage

### Extract mkp package

    import mkp

    package = mkp.load_file('foo-1.0.mkp')
    print(package.info)
    package.extract_files('path/to/somewhere')

### Pack files to mkp package

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
