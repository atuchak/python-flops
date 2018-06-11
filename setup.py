from setuptools import find_packages, setup


def read_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError, RuntimeError):
        return ''


packages = find_packages(exclude=['test_*.py'])

setup(
    name='flops',
    packages=packages,
    version='0.1.4',
    author='Anton Tuchak',
    author_email='anton.tuchak@gmail.com',
    long_description=read_long_description(),
    description='Python library to easy access flops.ru API.',
    keywords=['flops.ru API client flops'],
    url='https://github.com/atuchak/python-flops',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP'
    ],
    install_requires=['requests'],
)
