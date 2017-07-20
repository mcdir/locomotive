from setuptools import setup

setup(name='locomotive',
      version='0.1',
      description='locomotive',
      url='https://github.com/mcdir/locomotive',
      author='Unknown',
      author_email='unknown@unknown.xxx',
      license='MIT',
      packages=['ML'],
      install_requires=[
          'nltk',
          'feedparser'
      ],
      zip_safe=False)