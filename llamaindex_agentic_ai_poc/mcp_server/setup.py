# setup.py
from setuptools import setup, find_packages

setup(
    name='my-mcp-server',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # List any external dependencies your package needs, e.g., 'requests>=2.20.0'
    ],
    author='Your Name',
    author_email='venugopalgotagi@gmail.com',
    description='A simple example package.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/venugopalgotagi/fyld_poc/my-mcp-server',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)