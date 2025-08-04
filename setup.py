from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chatapi-cli",
    version="1.0.0",
    author="ChatAPI CLI Tool",
    description="A powerful command-line interface for interacting with multiple AI providers including OpenAI and Perplexity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marshal-dteach/chatapi-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "chatapi-cli=chatapi_cli:cli",
        ],
    },
    keywords="chatapi, cli, openai, perplexity, chat, terminal, ai",
    project_urls={
        "Bug Reports": "https://github.com/marshal-dteach/chatapi-cli/issues",
        "Source": "https://github.com/marshal-dteach/chatapi-cli",
    },
) 