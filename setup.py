from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mkdocs_include_dir_to_nav",
    version="1.2.0",
    description="A MkDocs plugin include all file in dir to navigation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs, navigation, plugin, directory, folder",
    url="https://github.com/mysiki/mkdocs_include_dir_to_nav",
    author="mysiki",
    # author_email="tome.robin@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    install_requires=["mkdocs>=1.0.4"],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "include_dir_to_nav = mkdocs_include_dir_to_nav.include_dir_to_nav:IncludeDirToNav"
        ]
    },
)
