import argparse

import project.package as java

if __name__ == '__main__':

    class A:

        FILE_PATH = 'f'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    =f"Parse and print Java file\nThis script serves as an example of how to make use of the module, using as handler the built-in {repr(java.parsers.StreamPrinter.__name__)}\nUse that handler as a template for your own {repr(java.handlers.entity.Handler)}.")
    p.add_argument(f'{A.FILE_PATH}',
                   help='file name or path')
    get = p.parse_args().__getattribute__
    # ...
    with open(get(A.FILE_PATH), mode='r') as f:

        java.StreamParser(handler=java.parsers.StreamPrinter()).parse_whole(f.read())
