from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='embrace',
    version='0.0.1',
    description='An agent-based python orchestration framework used to test, monitor, control or simulate networked systems',
    long_description=readme,
    author='theycallhimpat',
    author_email='nope',
    url='https://github.com/theycallhimpat/embrace',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
