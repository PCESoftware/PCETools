from setuptools import setup, find_packages

setup(
    name='pce',
    version='1.0.7',
    description='PCETools, a basic library for PCE softwares',
    author='Scihacker',
    author_email='sjtuzlp@gmail.com',
    url='https://github.com/PCESoftware/PCETools',
    packages=find_packages(),
    install_requires=[
        "pytest",
        "PyMuPDF",
        "svgwrite",
        "pyautogui",
        "keyboard",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
