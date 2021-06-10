from setuptools import setup

setup(
    name='grants',
    version='0.0.1',
    description='Grants viewer library',
    author='Vadim Meshcheryakov',
    author_email='painassasin@icloud.com',
    python_requires='>=3.9',
    install_requires=[
        'SQLAlchemy~=1.4.15',
        'mysql-connector-python'
    ]
)

