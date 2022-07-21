import sys, os
import shutil
# https://stackoverflow.com/questions/41836988/git-push-via-gitpython
for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        if name == '__pycache__':
            shutil.rmtree(os.path.join(root, name))

rmtrees = ["products", "data", "static/assets/prodimages","configs"]
for i in range(6):
    if i == 1:
        os.remove('setup')
    else:
        if i == 6:
            shutil.rmtree('logs')
            os.mkdir('logs')
            open('logs/README.md', 'w+')
        else:
            shutil.rmtree(rmtrees[i])

a = input("LoonaBilling Update Script \n1. Main Branch \n2. Development Branch\n>>> """)
if isinstance(a, int) == False:
    raise TypeError
if a == '1':
    os.system('git checkout main')
elif a == '2':
    os.system('git checkout development')
else:
    print('Invalid option')
    exit()

os.system('pipreqs . --force')
os.system('git add -A')
os.system('git commit -a')
input('Push enter')
if a == '1':
    os.system('git push origin HEAD:main')
elif a == '2':
    os.system('git push origin HEAD:development')
else:
    print('Invalid option')
    exit()
