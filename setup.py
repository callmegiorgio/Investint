from setuptools import setup, find_packages
import versioneer

setup(name             = 'investint',
      version          = versioneer.get_version(),
      cmdclass         = versioneer.get_cmdclass(),
      description      = 'Stores data of public companies registered at CVM and listed on B3',
      author           = 'Giovanni L',
      author_email     = 'callmegiorgio@hotmail.com',
      url              = 'https://github.com/callmegiorgio/Investint/',
      packages         = find_packages()
)