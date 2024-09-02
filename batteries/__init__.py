import os.path
import signal
import sys
import typing

def is_module(path:str):

    return path.endswith('.py') or (os.path.isdir(path) and os.path.exists(os.path.join(path,'__init__.py')))

def is_this_windows():

    return sys.platform == 'win32'

TEMP_DIR = 'C:\\Temp' if is_this_windows() else '/tmp'

def get_user_env(name  :str,
                 expand:bool=False):
    
    return (os.popen(f'powershell -NoProfile -Command "(Get-Item -Path HKCU:\\Environment).GetValue(\'{name}\')"') if expand else \
            os.popen(f'powershell -NoProfile -Command "(Get-Item -Path HKCU:\\Environment).GetValue(\'{name}\', $null, \'DoNotExpandEnvironmentNames\')"')).read()

class Enumerator[T]:

    def __init__(self):

        self._managed:list[T] = list()
    
    def E(self, x):

        """
        DEPRECATED
        """
        return self(x)
    
    def __call__(self, x):

        self._managed.append(x)
        return x

    def __iter__(self):

        return self._managed.__iter__()

#_SIGINT_HOOKS:list[typing.Callable[[],None]] = []
#def _SIGINT_MASTER_HANDLER(sig, frame):
#
#    for hook in _SIGINT_HOOKS: hook()
#
#signal.signal(signal.SIGINT, _SIGINT_MASTER_HANDLER)
#def add_sigint_hook(hook:typing.Callable[[],None]):
#
#    _SIGINT_HOOKS.append(hook)
#
#add_sigint_hook(lambda: print('--------SIGINT--------'))
class XorResult():

    def __init__(self,b): self._b = b
    def __bool__(self)  : return self._b

XOR_TRUE          = XorResult(True)
XOR_FALSE_ALL     = XorResult(False)
XOR_FALSE_NOT_ANY = XorResult(False)
def xor(predicate:typing.Callable[[typing.Any],bool], *aa):

    return XOR_FALSE_ALL     if     all(map(predicate, aa)) else \
           XOR_FALSE_NOT_ANY if not any(map(predicate, aa)) else \
           XOR_TRUE

def xor_None(*aa):

    return xor(lambda a: a is not None, *aa)

def agetter(o:typing.Any):

    def _f(a:str): return getattr(o,a)
    return _f

_SYS_ARGV_ITER = iter(sys.argv[1:])
def a():

    next(_SYS_ARGV_ITER)
