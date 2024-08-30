package foo.bar;

import java.io.File;
import java.util.*;
import static java.util.logging.Level.*;

/**
 * This is a multi-line comment.
 */
@DataClass
public abstract class FooBar extends Object implements Foo,Bar {

    private static Object ab;
    private long   cde     = 123L;
    public  static String answer  = "forty two";
    public  String answer2 = "for\\ty \"two\"";
    public final String answer3 = "".join(" ",List.of("forty", "two"));
    private Map<String,String> props = new HashMap<>() {};

    static {

        System.out.println("Hello, static constructor");
    }

    public FooBar() {
        
        System.out.println("Hello, constructor");
    }

    protected Boolean myMethod(String  x,
                               Integer y,
                               final Long z) {

        return (new Thingy() {

            more { braces {}}

        }).get();
    }
    public          void coiso() {}
    public abstract void coisa();

    public interface YelloPink {

        
    }
}
