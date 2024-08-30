import sys

import javasp

def main():
    
    with open(sys.argv[1], mode='r') as f:

        source = f.read()

    javasp.parse_whole(source)

if __name__ == '__main__': main()