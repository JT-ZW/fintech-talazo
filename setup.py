from setuptools import setup, find_packages

setup(
    name='talazo',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-marshmallow',
        'flask-migrate',
        'flask-cors',
        'flask-limiter',
        'python-dotenv',
        'scikit-learn',
        'numpy',
        'scipy',
        'click',
        'werkzeug',
        'joblib'
    ],
    entry_points={
        'console_scripts': [
            'talazo=talazo.cli:cli',
        ],
    },
)