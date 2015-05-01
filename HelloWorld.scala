object HelloWorld extends App {
    import util.Random.nextDouble
    import org.apache.spark.mllib.random
    import org.apache.spark.mllib.linalg

    val u = new random.UniformGenerator()
    // http://stackoverflow.com/questions/2381908/how-to-create-and-use-a-multi-dimensional-array-in-scala-2-8
    var A = new scala.Array[Array[Double]](4)
    A = A.map(x => new scala.Array[Double](4))
    A = A.map(x => x.map (r => u.nextValue()))
    val norms = A.map(a => a.sum)
    // http://stackoverflow.com/questions/9137644/how-to-get-the-element-index-when-mapping-an-array-in-scala
    A = A.zipWithIndex.map{case (s, i) => s.map(st => st / norms.apply(i))}


    

 }
