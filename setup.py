#usar con "python setup.py py2exe --verbose"
#usar con "python setup.py clean"


from distutils.core import setup
import py2exe
import os
#import app.config

os.system("cls")

setup(

    windows = [
        {
            "script": "polar.py",
        }
    ],
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    zipfile = None,
#    version=app.config.app_version,
    description='Polar Risk Assessment Tool',
    author='Alfonso Usero',
    author_email='contacto@alfonsousero.es',
    url='https://alfonsousero.es',
    packages=['app'],

)

input('>')
