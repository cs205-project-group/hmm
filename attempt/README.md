Previous attempt at parallelization using a different graph structure. 

To compile the cpp file, run the following on Linux:

```
g++ -std=c++11 attempthmm.cpp -I /path/to/graphlab-sdk -shared -fPIC -o attempthmm.so
```

and the following on Mac:

```
clang++ -stdlib=libc++ -std=c++11 attempthmm.cpp -I /path/to/graphlab-sdk -shared -fPIC -o attempthmm.so -undefined dynamic_lookup
```
