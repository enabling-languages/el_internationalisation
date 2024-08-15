from setuptools import setup

setup(
    name='el_internationalisation',
    version='0.7.5',
    description='Helper functions to improve Python internationalisation',
    url='https://github.com/enabling-languages/el_internationalisation',
    author='Andrew Cunningham',
    author_email='',
    license='MIT',
    packages=['el_internationalisation'],
    install_requires=[
        'arabic_reshaper',
        'hexdump',
        'lxml',
        'pyfribidi',
        'pyicu',
        'python-bidi',
        'regex',
        'rich',
        'unicodedataplus',
        'wcwidth'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
)
