from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="arbs_exchanges",
    version="0.1.2",
    author="knao124",
    author_email="noname@gmail.com",
    description="複数の仮想通貨取引所のREST APIとWebSocket APIのラッパー",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/knao124/arbs_exchanges",
    packages=find_packages(exclude=["tests*"]),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
