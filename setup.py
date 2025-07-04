from setuptools import setup, find_packages


with open('oven/version.py') as f:
    exec(f.read())

setup(
    name='exp_oven',
    version=__version__,
    author='Yan XIA',
    author_email='',
    packages=find_packages(),
    package_dir={'oven': 'oven'},
    package_data={'oven': ['utils/manual.txt']},
    include_package_data=True,
    description='Experiments monitor and notification utilities.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'omegaconf',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'oven = oven.cli:oven',  # Full version of CLI.
            'bake = oven.cli:bake',  # Shortcuts for baking a command.
            'ding = oven.cli:ding',  # Shortcuts for logging.
        ],
    },
)
