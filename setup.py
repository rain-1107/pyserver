from setuptools import setup, find_packages

VERSION = '0.1.3'
DESCRIPTION = 'Socket-based server package'
LONG_DESCRIPTION = ''

# Setting up
setup(
    name="pythreadserver",
    version=VERSION,
    author="rain1107",
    author_email="ryanbays@icloud.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'socket', 'threading'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
