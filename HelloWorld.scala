object HelloWorld extends App {
    import util.Random.nextDouble
    A.map(r =>nextDouble)
    A.map(r => (r.map (x => nextDouble)))
    A.map(a => a.map (x => x / a.sum))
 }
