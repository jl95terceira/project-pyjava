package project.tests.java_files;

import java.util.Map;

public class Test1 {
    
    private                  int         a1;
                static       boolean     a2;
    protected                String[]    a3;
    public      static       Object      a4;
    private     static final int         b1     = 123;
                       final boolean     b2     =   true;
    protected                String      b3     =  "abc";
    public      static final Object[][]  b4     = new Object[]{};
    public      static final Object      c1[]   =null;
    public      static final Object      c2[][] =null;
    public      static final Object[]    c3[]   =null;
    public      static final Object[]    c4[][] =null;
    public      static final Object[][]  c5[][] =null;

    {
        System.out.println("Hello");
    }
    static {
        System.out.println("Hello, static");
    }

    public  Test1(Map<String, String> properties,
                  Boolean             awesome) {}
    private Test1(byte[]              data)    {
        Test1(null, false);
    }
    Test1(){}
}
