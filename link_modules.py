import os
import site
import subprocess
from pathlib import Path

site_packages = site.getsitepackages()[0]
print(f'Site packages directory: {site_packages}')
command = f'ln -s {str(Path().absolute())} {site_packages}/four_in_a_row_online'.split(' ')
print(command)
subprocess.call(command)
print('successfuly linked this folder to sitepackages/four_in_a_row_online')
