import json
import sys, os
from hurry.filesize import size

def updateJSON(file, arg, content):
    try:
        with open(file) as of:
            data = json.load(of)
            data['Config'][0][arg] = content
            of.close()
            #print(data)
            with open(file, 'w+') as off:
                json.dump(data, off)
    except Exception as e:
        print(e)

def updateJSONargs(file, arg, content):
    try:
        with open(file) as of:
            data = json.load(of)
            data['Config'][0]['args'][arg] = content
            of.close()
            #print(data)
            with open(file, 'w+') as off:
                json.dump(data, off)
    except Exception as e:
        print(e)

def delVarJSON(file, arg):
    try:
        with open(file) as of:
            data = json.load(of)
            del data['Config'][0][arg]
            of.close()
            #print(data)
            with open(file, 'w+') as off:
                json.dump(data, off)
    except Exception as e:
        print(e)

def readJSON(file):
    with open(file) as of:
        data = json.loads(of)
        return data

def readJSONVar(file, var):
    with open(file) as of:
        data = json.load(of)
        for p in data['Config']:
            return p[var]

def getBranding():
    with open('configs/core/branding/branding.json') as of:
        data = json.load(of)
        for p in data['Config']:
            return (p['businessName'], p['aboutText'], p['logo'], p['favicon'])

def endisModule(module):
    if os.path.isfile(f'configs/core/modules/{module}'):
        #print('is')
        if readJSONVar(f'configs/core/modules/{module}', 'enabled'):
            updateJSON(f'configs/core/modules/{module}', 'enabled', False)
        else:
            updateJSON(f'configs/core/modules/{module}', 'enabled', True)
    #else:
        #print('not')

def moduleEnabled(module):
    return readJSONVar(f'configs/core/modules/{module}', 'enabled')

def Filesize(file):
    pass

# Add Filesize function
