import subprocess
import os

TEST_MKP = os.path.join(os.path.dirname(__file__), "test_original.mkp")
EXTRACT_SCRIPT = os.path.join(os.path.dirname(__file__), "../mkp/cli/extract.py")


def test_cli_extract_smoke(tmpdir):
    output_dir = str(tmpdir)
    result = subprocess.run([
        "python3", EXTRACT_SCRIPT, TEST_MKP, "-o", output_dir
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    # Check output dir for extracted files
    subdirs = os.listdir(output_dir)
    assert subdirs, "No output directory created"
    extract_path = os.path.join(output_dir, subdirs[0])
    assert os.path.isdir(extract_path), "Extracted directory missing"
    # Check info files
    assert os.path.isfile(os.path.join(extract_path, "info")), "info file missing"
    assert os.path.isfile(os.path.join(extract_path, "info.json")), "info.json file missing"
    # Check agents/special/agent_test exists and is a file
    agent_test_path = os.path.join(extract_path, "agents", "special", "agent_test")
    assert os.path.isfile(agent_test_path), "agents/special/agent_test missing"
    # Check checkman/test exists and contains expected content
    checkman_test_path = os.path.join(extract_path, "checkman", "test")
    assert os.path.isfile(checkman_test_path), "checkman/test missing"
    with open(checkman_test_path) as f:
        content = f.read()
    assert "Hello World!" in content, "checkman/test content mismatch"
