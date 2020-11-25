from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    readme_text = fh.read()

setup(
    name='jemris-mpm-utils',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/milosen/jemris-mpm-utils',
    author='Nikola Milosevic',
    author_email='milosevic.nikola@protonmail.com',
    long_description=readme_text,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    entry_points={
        'console_scripts': [
            'mpm-sim = mpm_sim.mpm_sim:cli'
        ]
    }
)
