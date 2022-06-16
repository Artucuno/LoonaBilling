# Simple script to push updates
import sys, os
import shutil

for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        if name == '__pycache__':
            shutil.rmtree(os.path.join(root, name))

try:
    shutil.rmtree('products')
except Exception as e:
    input(e)

try:
    shutil.rmtree('configs')
except Exception as e:
    input(e)

try:
    shutil.rmtree('logs')
    os.mkdir('logs')
    open('logs/README.md', 'w+')
except Exception as e:
    input(e)

a = input("""
LoonaBilling Update Script
1. Main Branch
2. Development Branch

>>> """)

os.system('pipreqs . --force')
os.system('git add -A')
if a == '1':
    os.system('git checkout main')
elif a == '2':
    os.system('git checkout development')
else:
    print('Invalid option')
    exit()
os.system('git commit -a')
input('Push enter')
if a == '1':
    os.system('git push origin HEAD:main')
elif a == '2':
    os.system('git push origin HEAD:development')
else:
    print('Invalid option')
    exit()
