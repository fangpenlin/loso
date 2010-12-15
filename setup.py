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
        'serve': scripts.ServeCommand
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
        'pyyaml'
    ],
    **extra
)
