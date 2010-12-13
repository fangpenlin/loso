from setuptools import setup

setup(
    name='Plurk_Loso',
    version='0.1',
    license='MIT',
    author='Plurk Inc.',
    author_email='opensource@plurk.com',
    description='Chinese segmentation library',
    long_description=__doc__,
    packages=['loso'],
    install_requires=[
        'redis'
    ]
)
