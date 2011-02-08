from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

extra = {}

try:
    from loso import scripts
except ImportError:
    pass
else:
    extra['cmdclass'] = {
        'interact': scripts.InteractCommand,
        'feed': scripts.FeedCommand,
        'reset': scripts.ResetCommand,
        'serve': scripts.ServeCommand,
        'dump': scripts.DumpCommand,
        'info': scripts.InfoCommand
    }

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
        'redis',
        'pyyaml',
        'lxml'
    ],
    **extra
)
