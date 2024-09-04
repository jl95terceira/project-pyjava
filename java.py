import sys

import project.package as java
import project.tests

def main():
    
    with open(sys.argv[1], mode='r') as f:

        java.StreamParser().parse_whole(f.read())

if __name__ == '__main__': main()