import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

install_requires = (
    'voteit.core',
)

testing_extras = [
    'nose',
    'coverage',
    'fakeredis<1.2',
    ]

setup(name='voteit.multiple_votes',
      version='0.2dev',
      description='Opt in extensions that allows multiple votes for users.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='VoteIT development team',
      author_email='info@voteit.se',
      url='http://www.voteit.se',
      keywords='web pylons pyramid voteit',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      extras_require = {
          'testing': testing_extras,
          },
      tests_require = install_requires,
      test_suite="voteit.multiple_votes",
      entry_points ={})
