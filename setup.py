from setuptools import find_packages, setup
import versioneer


setup(
    name='mkp',
    version=versioneer.get_version(),
    url='https://github.com/tom-mi/python-mkp/',
    license='GPLv2',
    author='Thomas Reifenberger',
    install_requires=[],
    author_email='tom-mi@users.noreply.github.com',
    description='Pack and unpack Check_MK mkp files',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Monitoring',
        ],
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        'console_scripts': [
            'mkp-extract=mkp.cli.extract:main',
        ],
    },
)
