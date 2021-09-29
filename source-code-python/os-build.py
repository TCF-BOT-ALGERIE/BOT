import os

os.system(f'pyinstaller -w -F events.py')
os.system(f'pyinstaller --onefile updater.py')
os.system(f'pyinstaller --onefile run.py')