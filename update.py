# Simple script to push updates
import sys, os

os.system('git add -A')
os.system('git commit -a')
input('Push enter')
os.system('git push')
