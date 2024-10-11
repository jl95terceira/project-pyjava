import project.package as java

if __name__ == '__main__':

    with open('Example.java', mode='r') as f:

        java.StreamParser(handler=java.parsers.StreamPrinter()).parse_whole(f.read())
