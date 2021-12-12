import java.util.regex.Pattern;
import java.util.regex.Matcher;
//import junit
import org.junit.Test;
import static org.junit.Assert.*;
public class Test {
    public boolean testRegex(String testString) {
        //random regex pattern
        String regex = "^[a-zA-Z][a-zA-Z-']{1,39}$";
        //matcher object
        Pattern pattern = Pattern.compile(regex);
        Pattern pattern2 = Pattern.compile("'.*'");
        Pattern pattern3 = Pattern.compile("--");
        //create a matcher
        Matcher matcher = pattern.matcher(testString);
        Matcher matcher2 = pattern2.matcher(testString);
        Matcher matcher3 = pattern3.matcher(testString);
        //if the string matches the pattern, check if it contains --,else return false
        if (matcher.matches()) {
            if (matcher2.find() || matcher3.find()) {
                return false;
            }
            return true;
        }
        return false;
    }
    @Test
    public void test_alphaname(){
    assertTrue(testRegex("Sommerville"));
    }

    @Test
    public void test_double_quotes(){
    assertFalse(testRegex("'Sommerville'"));
    }
    @Test
    public void test_namestartwithhyphen(){
    assertFalse(testRegex("-Sommerville"));
    }
    @Test
    public void test_namestartwithquote(){
    assertFalse(testRegex("'Sommerville"));
    }
    @Test
    public void test_nametoolong(){
    assertFalse(testRegex("Thisisalongstringwithmorethan40charactersfrombeginningtoend");
    }
    @Test
    public void test_nametooshort(){
    assertFalse(testRegex("S"));
    }
    @Test
    public void test_namewithdigit(){
    assertFalse(testRegex("C-3PO"));
    }
    @Test
    public void test_namewithdoublehyphen(){
    assertFalse(testRegex("Sommerville--"));
    }
    @Test
    public void test_namewithhyphen(){
    assertTrue(testRegex("Sommer-ville"));
    }
    @Test
    public void test_namewithinvalidchar(){
    assertFalse(testRegex("Sommerville!"));
    }
    @Test
    public void test_namewithquote(){
    assertTrue(testRegex("O'Reilly"));
    }
    @Test
    public void test_namewithspace(){
    assertFalse(testRegex("Sommerville Sommerville"));
    }
    @Test
    public void test_shortname(){
    assertTrue(testRegex("Sx"));
    }

}
public class Main {



    public static void main(String[] args) {
        test = new Test();
        test.test_alphaname();
        test.test_double_quotes();
        test.test_namestartwithhyphen();
        test.test_namestartwithquote();
        test.test_nametoolong();
        test.test_nametooshort();
        test.test_namewithdigit();
        test.test_namewithdoublehyphen();
        test.test_namewithhyphen();
        test.test_namewithinvalidchar();
        test.test_namewithquote();
        test.test_namewithspace();
        test.test_shortname();
    }
}