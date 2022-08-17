import sys, os
import json
from colorama import Fore, Back, Style
from colorama import init
import imp
from core.utils import files as fls
import traceback

automods = {}
autopro = []

for path, dirs, files in os.walk("core/modules/automation", topdown=False):
    for fname in files:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                automods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                autopro += [(getattr(automods[fname], 'module').name, fls.getFuncts(automods[fname]), fname)]
                print(Fore.GREEN + f'[Automation Util] ' + Style.RESET_ALL + 'Imported', automods[fname].module.name)
                #globals()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

def getAutomations():
    a = []
    for f in autopro:
        #print(f)
        print(f[0])
        for ff in f[1]:
            a += [ff['args'][0]]
    return a

def getAutomationArgs(automation):
    for f in autopro:
        #print(f)
        #print(f[0])
        for ff in f[1]:
            if automation == ff['args'][0]:
                return ff['args'][1]
    return False

def runAutomation(automation, fnc, args=None):
    print('\n\n', automation, fnc, args, '\n\n')
    try:
        for f in autopro:
            #print(f)
            #print(f)
            if f[0] == automation:
                for ff in f[1]:
                    try:
                        if fnc == ff['args'][0]:
                            print('Automation found 56')
                            print(f[2])
                            a = getattr(automods[f[2]], fnc)(args)
                            print(a)
                            return a
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(traceback.format_exc())
                        print(e, exc_type, fname, exc_tb.tb_lineno)
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
        return False
