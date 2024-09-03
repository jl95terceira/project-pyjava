import sys

import project.package as java

def main():
    
    with open(sys.argv[1], mode='r') as f:

        source = f.read()

    java.parse_whole(source)

if __name__ == '__main__': main()