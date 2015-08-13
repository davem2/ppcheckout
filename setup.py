from setuptools import setup, find_packages
setup(
  name          = 'ppcheckout',
  author        = 'David Maranhao',
  author_email  = 'david.maranhao@gmail.com',
  license       = 'MIT',
  description   = 'Automates the initial setup of a pgdp.net post processing project.',
  packages      = ['ppcheckout'], # this must be the same as the name above
  package_data  = {'': ['_NEW_PROJECT_TEMPLATE']},
  version       = '0.1.0',
  url           = 'https://github.com/davem2/ppcheckout',
  download_url  = 'https://github.com/davem2/ppcheckout/tarball/0.2.0',
  keywords      = ['text', 'processing', 'book', 'ebook', 'gutenberg', 'distributedproofreaders'],
  entry_points = {
      'console_scripts': [
          'ppcheckout = ppcheckout.ppcheckout:main',
      ],
  },
  install_requires = [
    'docopt >= 0.6.1',
    'docutils >= 0.12',
    'pillow >= 2.7.0',
  ],
  classifiers = [
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Text Processing",
    "Topic :: Text Processing :: Markup",
  ],
)

