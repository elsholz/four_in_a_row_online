import os
import site
import subprocess
from pathlib import Path

site_packages = site.getsitepackages()[0]
print(f'Site packages directory: {site_packages}')
link_name = f'{site_packages}/four_in_a_row_online'
print('link name:', link_name)
subprocess.call(f'rm {link_name}'.split(' '))
command = f'ln -s {str(Path().absolute())} {link_name}'.split(' ')
print(command)
subprocess.call(command)
print('successfuly linked this folder to sitepackages/four_in_a_row_online')
