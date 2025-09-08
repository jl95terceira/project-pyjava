import argparse
import pprint
print = pprint.pprint

import project.package as java

if __name__ == '__main__':

    class A:

        FILE_PATH = 'f'
        ENCODING = 'enc'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    =f"""
                                Load a whole Java file as a Python object
                                This script serves as an example of how to make use of the module to load Java files into a tree-like structure that can then be traversed. 
                                It is more useful than just stream-parsing when you want to make multiple passes over the data. However, it is slower (as it still stream-parses the file first) and more memory-intensive.
                                """)
    p.add_argument(f'{A.FILE_PATH}',
                   help='file name or path')
    p.add_argument(f'--{A.ENCODING}',
                   help='file encoding')
    get = p.parse_args().__getattribute__
    # ...
    with open(get(A.FILE_PATH), mode='r', encoding=get(A.ENCODING)) as f:

        print(java.load(f.read()))
