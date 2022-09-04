from setuptools import setup
import versioneer

install_requires = [
    'PyQt5>=5.14,PyQt5<6',
    'SQLAlchemy>=1.4',
    'SQLAlchemy-Utils>=0.38',
    'pyqt5-fugueicons>=3.56',
    'cvm',
    'b3',
    'icvm'
]

setup(name             = 'Investint',
      version          = versioneer.get_version(),
      cmdclass         = versioneer.get_cmdclass(),
      description      = 'Stores data of public companies registered at CVM and listed on B3',
      author           = 'Giovanni L',
      author_email     = 'callmegiorgio@hotmail.com',
      url              = 'https://github.com/callmegiorgio/Investint/',
      packages         = ['investint'],
      install_requires = install_requires,
)