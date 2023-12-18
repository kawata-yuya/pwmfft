from setuptools import setup, find_packages

def requirements_from_file(file_name):
    return open(file_name).read().splitlines()


setup(
    name='pwmfft',
    version='0.0.1',
    author="kawawta-yuya",
    description="オシロスコープの波形をDFT変換し管理する",
    url="https://github.com/kawata-yuya/pwmfft",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts':[
            'pwmfft = pwmfft.cli:main',
        ],
    },
    python_requires='>=3.8',
    install_requires=requirements_from_file('requirements.txt'),
)
