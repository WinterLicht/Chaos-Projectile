'''
Documentation cx_freeze: http://cx-freeze.readthedocs.org/en/latest/
To generate, type:
python setup.py build
'''

from cx_Freeze import setup, Executable

import sys

if sys.platform == "win32":
    base = "Win32GUI"
    bin_inc = []#'C:\\Python27\\Lib\\site-packages\\pygame'
    targetName = "Chaos-Projectile.exe"

else:
    base = None
    #pygame seems to have some problems with image libraries
    #it throws following error when executable starts:
    #    pygame.error: File is not a Windows BMP file
    #to resolve this, depending image libraries must be included here!
    bin_inc = [("/usr/lib/i386-linux-gnu/libjpeg.so.62.1.0","libjpeg.so.62"),
               ("/lib/i386-linux-gnu/libpng12.so.0.50.0","libpng12.so.0")]
    targetName = "Chaos-Projectile"

buildOptions = dict(excludes = [],
                    include_files = bin_inc,        
                    icon = "data/orb.ico")

setup( name = 'Chaos Projectile',
       version = '0.7',
       description = 'Chaos Projectile - Run n Gun meets RPG',
       options = dict(build_exe = buildOptions),
       executables = [Executable(script="game.py", base = base, targetName=targetName)] )
