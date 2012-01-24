from setuptools import setup, find_packages

setup(
    name = 'gitorama',
    version = '0.1.0',
    description = 'A GitHub extension',
    author = 'Alexander Artemenko',
    author_email = 'svetlyak.40wt@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
)


