import argparse

import project.package as java

if __name__ == '__main__':

    class A:
        FILE_PATH = 'f'
        ENCODING = 'enc'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    =f"""
                                Stream-parse a Java file
                                This script serves as an example of how to make use of the module to stream-parse a Java file where you must define what to do with each entity that is encountered (e.g. a class, an attribute, a method...).
                                This script uses as handler the included {repr(java.parsers.StreamPrinter.__name__)}. Take said handler as a template for your own {repr(java.handlers.entity.Handler)} to process Java entities according to your specific need.
                                """)
    p.add_argument(f'{A.FILE_PATH}',
                   help='file name or path')
    p.add_argument(f'--{A.ENCODING}',
                   help='file encoding')
    get = p.parse_args().__getattribute__
    # ...
    with open(get(A.FILE_PATH), mode='r', encoding=get(A.ENCODING)) as f:

        java.StreamParser(handler=java.parsers.StreamPrinter()).parse_whole(f.read())
