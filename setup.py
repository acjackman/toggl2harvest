from setuptools import setup, find_packages

setup(
    name='Toggl2Harvest',
    version='0.1dev',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'python-dateutil',
        'requests',
        'ruamel.yaml',
    ],
    entry_points="""
        [console_scripts]
        toggl2harvest=toggl2harvest.scripts.toggl2harvest:cli
    """
)
