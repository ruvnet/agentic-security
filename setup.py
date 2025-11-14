from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r') as f:
        requirements = []
        for line in f:
            line = line.strip()
            # Skip comments, empty lines, and optional dependencies
            if line and not line.startswith('#') and ';' not in line:
                requirements.append(line)
        return requirements

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="agentic-security",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=read_requirements(),
    extras_require={
        'gui': ['streamlit>=1.28.0'],
        'cache': ['redis>=5.0.0'],
        'all': ['streamlit>=1.28.0', 'redis>=5.0.0'],
        'dev': [
            'pytest>=7.4.3',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'agentic-security=agentic_security.security_cli:cli',
        ],
    },
    python_requires='>=3.10',
    author="rUv",
    author_email="contact@agentic-security.io",
    description="AI-Native Security Intelligence Platform with learning capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ruvnet/agentic-security",
    project_urls={
        'Documentation': 'https://docs.agentic-security.com',
        'Source': 'https://github.com/ruvnet/agentic-security',
        'Bug Reports': 'https://github.com/ruvnet/agentic-security/issues',
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords="security ai llm vulnerability-detection prompt-injection agentic devsecops automation machine-learning agentdb aidefence",
    license="MIT",
    platforms=["any"],
)
