// MIX-LRT-SITE fixture generator (provenance of mix_lrt_site.py JVM_FIXTURE; engine-coder, 2026-09-26; zero calls, no DB).
// Invokes the COMPILED Kotlin method SeparationNullBySizeTest.withinNodeCloud (private; by reflection) on two fixtures with
// java.util.Random seeds, and prints its outputs, the F2 inputs and ten java.util.Random(42).nextGaussian() values.
// Run (JDK 21; paths are the machine's of 2026-09-26; the class dir must hold a compile of blob 0b6e176f):
//   javac -d <tmp> WithinNodeCloudFixture.java && java -cp <tmp> WithinNodeCloudFixture > fixture_out.txt
// The class used on 2026-09-26: Z:/FAC/TUBerlin/THESIS/TaxoArena/build/classes/kotlin/test/taxonomy/SeparationNullBySizeTest.class
// (sha256 dfa5a30e7529cd1bc829a4c0502eff4be696a7daad81dd29c84458ffbd21a150, written 2026-09-25 20:43; the source file's last
// commit is 2026-09-23 and the main checkout's copy is unmodified). java version "21.0.6" 2025-01-21 LTS (GraalVM).
import java.net.*; import java.io.*; import java.util.*; import java.lang.reflect.*;
public class WithinNodeCloudFixture {
  static String row(double[] r) { StringBuilder s = new StringBuilder(); for (double x : r) s.append(Double.toString(x)).append(" "); return s.toString().trim(); }
  public static void main(String[] a) throws Exception {
    String M = "Z:/FAC/TUBerlin/THESIS/TaxoArena/build/classes/kotlin/";
    String[] jars = {"C:/Users/octav/.m2/repository/org/jetbrains/kotlin/kotlin-stdlib/2.0.21/kotlin-stdlib-2.0.21.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/org.slf4j/slf4j-api/2.0.16/172931663a09a1fa515567af5fbef00897d3c04/slf4j-api-2.0.16.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/org.jetbrains.kotlinx/kotlinx-serialization-json-jvm/1.6.3/2241746853abf04073e3ab0dcd9e6729d363b313/kotlinx-serialization-json-jvm-1.6.3.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/org.jetbrains.kotlinx/kotlinx-serialization-core-jvm/1.6.3/6b6c17d0312ba7192893adea9d52959941d0119b/kotlinx-serialization-core-jvm-1.6.3.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm/1.8.1/bb0e192bd7c2b6b8217440d36e9758e377e450/kotlinx-coroutines-core-jvm-1.8.1.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/org.junit.jupiter/junit-jupiter-api/5.11.4/308315b28e667db4091b2ba1f7aa220d1ddadb97/junit-jupiter-api-5.11.4.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/ch.qos.logback/logback-classic/1.5.16/113979db51dfad6dc895b34460d7b7ff64ffe7d2/logback-classic-1.5.16.jar",
      "C:/Users/octav/.gradle/caches/modules-2/files-2.1/ch.qos.logback/logback-core/1.5.16/4f17700f046900aea2fadf115e2d67fec921f7fd/logback-core-1.5.16.jar"};
    List<URL> cp = new ArrayList<>(); cp.add(new File(M+"test/").toURI().toURL()); cp.add(new File(M+"main/").toURI().toURL());
    for (String j : jars) cp.add(new File(j).toURI().toURL());
    URLClassLoader cl = new URLClassLoader(cp.toArray(new URL[0]), ClassLoader.getPlatformClassLoader());
    Class<?> c = cl.loadClass("taxonomy.SeparationNullBySizeTest");
    Method m = c.getDeclaredMethod("withinNodeCloud", double[].class, List.class, int.class, Random.class);
    m.setAccessible(true);
    Constructor<?> k = c.getDeclaredConstructor(); k.setAccessible(true); Object inst = k.newInstance();
    // F1
    double[] mu = {0.5, -0.25, 0.125, 0.75, -0.0625};
    List<double[]> cen = new ArrayList<>();
    cen.add(new double[]{0.1, -0.2, 0.05, 0.3, 0.0});
    cen.add(new double[]{-0.3, 0.1, 0.2, -0.1, 0.15});
    cen.add(new double[]{0.2, 0.1, -0.25, -0.2, -0.15});
    cen.add(new double[]{0.0, 0.0, 0.0, 0.0, 0.0});
    System.out.println("F1 seed 20260926 n 6");
    for (Object r : (List<?>) m.invoke(inst, mu, cen, 6, new Random(20260926L))) System.out.println(row((double[]) r));
    // F2
    double[] mu2 = new double[6]; for (int i = 0; i < 6; i++) mu2[i] = Math.sin(i + 1) * 0.3;
    List<double[]> c2 = new ArrayList<>();
    for (int jj = 0; jj < 12; jj++) { double[] v = new double[6]; for (int i = 0; i < 6; i++) v[i] = Math.cos(7 * jj + 3 * i) * 0.1; c2.add(v); }
    System.out.println("F2 seed 42 n 8 MU " + row(mu2));
    for (double[] v : c2) System.out.println("C " + row(v));
    for (Object r : (List<?>) m.invoke(inst, mu2, c2, 8, new Random(42L))) System.out.println(row((double[]) r));
    Random r = new Random(42L); double[] g = new double[10]; for (int i = 0; i < 10; i++) g[i] = r.nextGaussian();
    System.out.println("G42 " + row(g));
  }
}
