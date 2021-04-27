from setuptools import setup, find_packages

setup(
    name='pyliverecorder',
    version=__import__("PyLiveRecorder").__version__,
    packages=find_packages(),
    description='Monitor the start of live and download media stream automatically.',
    author='InJeCTrL',
    author_email='dap1933@hotmail.com',
    license='MIT',
    url='https://github.com/InJeCTrL/PyLiveRecorder/',
    install_requires=[
        "requests",
        "bs4",
        "PyExecJS",
        ]
    )
