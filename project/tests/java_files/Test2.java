package project.tests.java_files;

import java.util.*;

public class Test2 {
    
    public void Test2(@QueryParam List<@NonNull Integer> ints) {throw new Exception(){};}
    public      Test2(@QueryParam List<@NonNull Integer> ints) {throw new Exception(){};}
    public void Test2(@QueryParam @Foo("Bar", "Baz") List<@NonNull Integer> ints) {throw new Exception(){};}
}
