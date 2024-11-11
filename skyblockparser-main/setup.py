from setuptools import setup, find_packages

VERSION = '2.0'
DESCRIPTION = 'A package allowing you to parse skyblock profile information including networth.'

# Setting up
setup(
    name="skyblockparser",
    version=VERSION,
    author="nom",
    author_email="<noemtdev@gmail.com>",
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['aiohttp', 'pillow'],
    keywords=['python', 'hypixel', 'skyblock', 'hypixel skyblock'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ],
    package_data={'skyblockparser': ['skyblockparser/*']}
)