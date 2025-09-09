from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="newscrap",
    version="0.1.0",
    description="Google News Scraper CLI for OSINT and research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/opsysdebug/NewsCrap",
    author="opsysdebug",
    author_email="your-email@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="scraper, news, google, osint, cli",
    py_modules=["news_scrap"],
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "fake-useragent>=1.2.0",
        "schedule>=1.1.0",
        "Jinja2>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "newscrap=news_scrap:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/opsysdebug/NewsCrap/issues",
        "Source": "https://github.com/opsysdebug/NewsCrap",
    },
)
