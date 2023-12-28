from setuptools import setup, find_packages
from fluxo import __version__


setup(
    name='fluxo',
    version=__version__,
    description='Simple data flow with execution in separate threads and easy scheduling configuration.',
    maintainer='Mailson Náscin',
    maintainer_email='mailson.nascin@gmail.com',
    packages=find_packages(),
    package_data={
        '': ['fluxo_server/assets/**/*'],
    },
)
