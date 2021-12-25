from setuptools import setup

setup(
    name='blah',
    version='0.1.0',
    py_modules=['blah'],
    install_requires=[
        'Click',
        'aur',
    ],
    entry_points={
        'console_scripts': [
            'blah = blah:cli',
        ],
    },
)