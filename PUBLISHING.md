# Publishing Agentic Security v2.0 to PyPI

## Prerequisites

1. **Install build tools**:
```bash
pip install --upgrade build twine
```

2. **Configure PyPI credentials**:
```bash
# Create ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<your-api-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<your-test-api-token>
```

## Pre-Publishing Checklist

- [ ] All tests passing: `pytest`
- [ ] Version updated in `setup.py` and `pyproject.toml`
- [ ] CHANGELOG.md updated with release notes
- [ ] README.md reviewed and current
- [ ] All v2.0 features documented
- [ ] Dependencies verified and pinned appropriately
- [ ] License file present (MIT)
- [ ] Git tag created for release

## Build Distribution

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info
```

### 2. Build Source and Wheel Distributions

```bash
python -m build
```

This creates:
- `dist/agentic-security-2.0.0.tar.gz` (source distribution)
- `dist/agentic_security-2.0.0-py3-none-any.whl` (wheel distribution)

### 3. Check Distribution

```bash
twine check dist/*
```

Expected output:
```
Checking dist/agentic-security-2.0.0.tar.gz: PASSED
Checking dist/agentic_security-2.0.0-py3-none-any.whl: PASSED
```

## Test on TestPyPI

### 1. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

### 2. Test Installation

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ agentic-security

# Test CLI
agentic-security version

# Deactivate and remove
deactivate
rm -rf test_env
```

## Publish to PyPI

### 1. Upload to PyPI

```bash
twine upload dist/*
```

### 2. Verify Publication

Visit: https://pypi.org/project/agentic-security/

### 3. Test Installation from PyPI

```bash
# Fresh environment
python -m venv prod_test
source prod_test/bin/activate

# Install from PyPI
pip install agentic-security

# Verify installation
agentic-security version
python -c "from agentic_security.v2 import SecurityPipelineV2; print('v2.0 imported successfully')"

deactivate
rm -rf prod_test
```

## Post-Publishing Steps

### 1. Create GitHub Release

```bash
git tag -a v2.0.0 -m "Agentic Security v2.0.0 - AI-Native Security Intelligence Platform"
git push origin v2.0.0
```

Create release on GitHub with:
- Title: "v2.0.0 - AI-Native Security Intelligence Platform"
- Description: Copy from CHANGELOG.md
- Attach distribution files

### 2. Update Documentation

- [ ] Update docs.agentic-security.com
- [ ] Update GitHub README badges
- [ ] Update examples and tutorials
- [ ] Announce on social media/blog

### 3. Verify Package Metadata

Check on PyPI that all metadata is correct:
- Description renders properly
- Project URLs work
- Classifiers are appropriate
- Dependencies are correct

## Troubleshooting

### Build Fails

```bash
# Check setup.py
python setup.py check

# Validate pyproject.toml
pip install validate-pyproject
validate-pyproject pyproject.toml
```

### Upload Fails

```bash
# Check credentials
cat ~/.pypirc

# Verify token has correct permissions

# Try with verbose output
twine upload --verbose dist/*
```

### Installation Issues

```bash
# Check dependencies
pip check

# Install with verbose
pip install -v agentic-security

# View installed files
pip show -f agentic-security
```

## Version Bumping for Future Releases

### Patch Release (2.0.1)

```bash
# Update version in:
# - setup.py: version="2.0.1"
# - pyproject.toml: version = "2.0.1"
# - src/agentic_security/__init__.py: __version__ = "2.0.1"

# Build and publish
python -m build
twine upload dist/*
```

### Minor Release (2.1.0)

Follow same process, update CHANGELOG.md with new features.

### Major Release (3.0.0)

Include migration guide, breaking changes documentation.

## Distribution Files Checklist

Ensure these files are included:

- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `CHANGELOG.md`
- [ ] `pyproject.toml`
- [ ] `setup.py`
- [ ] `requirements.txt`
- [ ] `package.json` (for aidefence/agentdb)
- [ ] `MANIFEST.in`
- [ ] All source code in `src/`
- [ ] All tests in `tests/`
- [ ] Planning docs in `plan/v2/`

## Security Considerations

- [ ] No API keys in source code
- [ ] No .env files included
- [ ] No sensitive data in examples
- [ ] Dependencies vetted for vulnerabilities
- [ ] SBOM (Software Bill of Materials) generated

## Support After Publishing

- Monitor PyPI downloads: https://pypistats.org/packages/agentic-security
- Watch GitHub issues
- Respond to community questions
- Track user feedback
- Plan future releases based on usage

---

**Ready to publish Agentic Security v2.0!** 🚀

For questions: contact@agentic-security.io
