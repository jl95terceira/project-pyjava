package foo.bar;

import java.io.File;
import java.util.*;
import static java.util.logging.Level.*;

@DataClass
public class FooBar extends Object implements Foo,Bar {

    private static Object ab;
    private long   cde     = 123L;
    public  static String answer  = "forty two";
    public  String answer2 = "for\\ty \"two\"";
    public String answer3 = "".join(" ",List.of("forty", "two"));

    protected void myMethod(String  x,
                            Integer y);
}