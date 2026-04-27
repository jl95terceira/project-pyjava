import argparse
import typing

import project.package as java

class CountingHandler(java.parsers.SilentHandler):

    def __init__(self):

        self._nr_classes    = 0
        self._nr_attributes = 0
        self._nr_methods    = 0

    @typing.override
    def handle_class      (self, class_     :java.handlers.decl.ClassHeaderDeclaration):
        self._nr_classes += 1
    @typing.override
    def handle_attribute  (self, attribute  :java.handlers.decl.AttributeDeclaration):
        self._nr_attributes += 1
    @typing.override
    def handle_method     (self, method     :java.handlers.decl.MethodDeclaration):
        self._nr_methods += 1

if __name__ == '__main__':

    class A:
        FILE_PATH = 'f'
        ENCODING = 'enc'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    =f"""
                                Stream-parse a Java file and count the number of each entity type
                                This script serves as an example of how to make use of the module to stream-parse a Java file to count the number of classes, of attributes and of methods that are encountered.
                                """)
    p.add_argument(f'{A.FILE_PATH}',
                   help='file name or path')
    p.add_argument(f'--{A.ENCODING}',
                   help='file encoding')
    get = p.parse_args().__getattribute__
    # ...
    handler = CountingHandler()
    with open(get(A.FILE_PATH), mode='r', encoding=get(A.ENCODING)) as f:

        java.StreamParser(handler=handler).parse_whole(f.read())

    print(f'Number of classes:    {handler._nr_classes}')
    print(f'Number of attributes: {handler._nr_attributes}')
    print(f'Number of methods:    {handler._nr_methods}')
