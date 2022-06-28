import json
import sys, os

def updateJSON(file, arg, content):
    try:
        with open(file) as of:
            data = json.load(of)
            data['Config'][0][arg] = content
            of.close()
            print(data)
            with open(file, 'w+') as off:
                json.dump(data, off)
    except Exception as e:
        print(e)
