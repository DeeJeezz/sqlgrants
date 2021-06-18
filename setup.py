from setuptools import setup, find_packages

setup(
    name='python-SQLGrants',
    version='1.0.0',
    packages=find_packages(),
    description='Grants processing library',
    author='Vadim Meshcheryakov',
    author_email='painassasin@icloud.com',
    python_requires='>=3.8',
    install_requires=[
        'SQLAlchemy~=1.4',
        'mysql-connector-python'
    ]
)
