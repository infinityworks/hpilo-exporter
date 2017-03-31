import io
from setuptools import setup, find_packages
import sys

VERSION = "0.1.1"
PACKAGE_NAME = "hpilo-exporter"
SOURCE_DIR_NAME = "src"

def readme():
    with io.open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Prometheus exporter for HP iLO metrics",
    author="Joe Stringer",
    author_email="joe.stringer@infinityworks.com",
    long_description=readme(),
    url="https://github.com/infinityworksltd/hpilo-exporter",
    package_dir={'': SOURCE_DIR_NAME},
    packages=find_packages(SOURCE_DIR_NAME, exclude=('*.tests',)),
    include_package_data=True,
    zip_safe=False,
    package_data={},
    license='Apache 2',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Development Status :: 2 - Pre-Alpha',
    ],
    install_requires=[
        "python-hpilo>=3.8",
        "tornado>=3.1.1"
    ],
    entry_points={
        'console_scripts': [
            'hpilo-exporter = hpilo_exporter.__main__:main',
        ],
    }
)
