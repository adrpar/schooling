from setuptools import setup, find_packages

setup(
    name='math-trainer',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'lxml',
        'inkex',
    ],
    entry_points={
        'console_scripts': [
            'math-trainer=math_trainer:cli',
        ],
    },
    python_requires='>=3.6',
)
