import os
import subprocess
import sys
import pytest
from mkp import DIRECTORIES


@pytest.mark.smoke
def test_mkp_init_creates_skeleton_and_mkp(tmp_path):
    # Run mkp-init in the temp directory
    result = subprocess.run([
        sys.executable, '-m', 'mkp.cli.init', '--name', 'testpkg', '--author', 'Tester', '--version', '1.2.3',
        '--description', 'desc', '--title', 'TestPkg', '--download_url', 'http://example.com/', '--min_required',
        '1.0.0', '--ignore-non-empty'
    ], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, f"mkp-init failed: {result.stderr}"
    # Check all directories are created
    for d in DIRECTORIES:
        assert (tmp_path / d).is_dir(), f"Directory {d} not created"
    # Check dist.py is created
    dist_py = tmp_path / 'dist.py'
    assert dist_py.is_file(), "dist.py not created"
    # Run dist.py to create mkp package
    result = subprocess.run([
        str(dist_py)
    ], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, f"dist.py failed: {result.stderr}"
    # Check dist/ directory and .mkp file
    dist_dir = tmp_path / 'dist'
    assert dist_dir.is_dir(), "dist directory not created"
    mkp_files = list(dist_dir.glob('*.mkp'))
    assert mkp_files, "No mkp package created by dist.py"
