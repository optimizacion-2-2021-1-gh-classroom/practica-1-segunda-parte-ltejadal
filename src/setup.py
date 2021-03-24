#see: https://setuptools.readthedocs.io/en/latest/userguide/package_discovery.html
from setuptools import setup, find_packages

setup(name="ant_colony",
      version="0.1",
      description=u"Ant Colony Implementation",
      url="",
      author="equipo 1, Optimizacion Avanzada",
      author_email="",
      license="MIT",
      packages=find_packages(),
      ## falta actualizar paquetes correctos dependiendo del codigo de Ant Colony: 
      install_requires = [
                          "numpy",
                          "pandas",
                          "nose"
                          ],
      )
