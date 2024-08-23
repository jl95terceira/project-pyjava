import mmap

import javasp

def main():
    
    with open('FooBar.java', mode='r') as f:

        source = f.read()

    javasp.parse(source)

if __name__ == '__main__': main()