import os

os.system('pyinstaller -w -F events.py')
os.system('pyinstaller --onefile updater.py')
os.system('pyinstaller --onefile run.py')