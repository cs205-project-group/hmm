#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include<fstream>

using namespace graphlab;
using namespace std;

int t_iteration;
int obseqt;
float normalizer = 1;
void sum_shit(edge_triple& triple) {
   	if (t_iteration % 2 != (int)triple.edge["parity"]) {
   		triple.target["ait"][t_iteration] += triple.target["b"][obseqt] * (((float)triple.source["ait"][t_iteration-1] / normalizer) * (float)triple.edge["aij"]);
   	}
} 

gl_sgraph fp(gl_sgraph& g, std::vector<int> observation_seq) {

    for (t_iteration = 1; t_iteration < observation_seq.size() + 1; t_iteration++) {
        // https://github.com/dato-code/GraphLab-Create-SDK/blob/master/sdk_example/sgraph_weighted_pagerank.cpp
        // Normalization function
        // based on documentation at https://dato.com/products/create/sdk/docs/classgraphlab_1_1gl__sframe.html
        int parity = t_iteration % 2;
        
        obseqt = observation_seq[t_iteration];
    	g = g.triple_apply(sum_shit, {"ait", "aij", "b"});
        gl_sframe v = g.vertices();

        normalizer = v[v["parity"] == parity]["ait"].apply([](const std::vector<flexible_type>& x) { 
            return (float)x[t_iteration];
        }, flex_type_enum::FLOAT).sum();

	}

	return g;
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "observation_seq"); // provide named parameters
END_FUNCTION_REGISTRATION
