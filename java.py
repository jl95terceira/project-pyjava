import sys

import project.package as java
import project.tests.test_

def main():
    
    with open(sys.argv[1], mode='r') as f:

        source = f.read()

    java.parse_whole(source)

if __name__ == '__main__': main()