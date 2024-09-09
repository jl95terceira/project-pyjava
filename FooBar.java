package foo.bar;

import java.io.File;
import java.util.*;
import static java.util.logging.Level.*;

/**
 * This is a multi-line comment.
 */
@DataClass
public abstract class FooBar<A,B> extends Object implements Foo,Bar {

    private static       Object   ab;
    private              long     cde     = 123L;
    public  static final String   answer  = "forty two";
    public               String[] answer2 = new String[]{"for\\ty             \"two\""};
    /**
     * this is another multi-line comment with            a             lot           of    space
     */
    public static        byte  [] raw;
    public         final String   answer3 = "".join(" ",List.of("forty", "two")); // one-line

    static {

        System.out.println("Hello, static constructor");
    }

    public FooBar() {
        
        System.out.println("Hello, constructor");
    }
    public FooBar(String something, byte b, byte[] bb) {
        
        System.out.println(String.format("Hello, %s", something));
    }

    protected       Boolean myMethod(String  x,
                               Integer y,
                               final Long z) {

        return (new Thingy() {
            {
                {
                    // lots of braces :)
                }
            }
        }).get();
    }
    private         int[]            ayoh    (String[] aa, String a) {}
    public          void             coiso   () {}
    public abstract Optional<String> coisa   ();

    public interface YelloPink {

        public static void main(String[] aa) {}
        public static void another_main(Integer [ ] bb) {}   
    }

    public enum FooEnum1 {

        VALUE_A;
    }
    public enum FooEnum2 {

        VALUE_A,
        VALUE_B;
    }
    public enum FooEnum3 {

        VALUE_A(123);

        FooEnum3(Object x) {}
    }
    public enum FooEnum4 {

        VALUE_A(123),
        VALUE_B("D EF");

        FooEnum4(final Object x) {}
    }
}
