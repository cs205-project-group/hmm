#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include<fstream>
#include <assert.h>

using namespace graphlab;
using namespace std;

int t_iteration;

void sum_shit(edge_triple& triple) {
   	if (t_iteration % 2 != (int)triple.edge["parity"]) {
   		triple.target["ait"][t_iteration] += ((float)triple.source["ait"][t_iteration-1] * (float)triple.edge["aij"]);
   	}
}

/*
 * stuff andy wrote
float vector_multiply(std::vector<flexible_type> a, 
        std::vector<flexible_type> b) {

    assert(a.size() == b.size());
    std::vector<flexible_type> result;
    result.resize(b.size());

    for (int i = 0; i < a.size(); i++) {
        result[i] = a[i] * b[i];
    }

    return result
}

float vector_divide(std::vector<flexible_type> a,
        std::vector<flexible_type> b) {
    assert(a.size() == b.size());
    std::vector<flexible_type> result;
    result.resize(b.size());

    for (int i = 0; i < a.size(); i++) {
        result[i] = a[i] / b[i];
    }

    return result
}

void get_gammas(gl_sgraph& g) {

    verts = g.get_vertices();
    gammas = verts.apply([](const std::vector<flexible_type>& x) { 
                                    return vector_multiply(x[0], x[1]); 
                                    }, flex_type_enum:FLOAT);
    // column sums
    //gammas_normalizer =  
}

*/

gl_sgraph fp(gl_sgraph& g, std::vector<int> observation_seq) {

    // fill in Bi* for each vertex i
    // https://dato.com/products/create/sdk/docs/page_userguide_sframe.html
    //gl_sarray arr = g.vertices()["b"];
    //FILE *f = fopen("test.txt", "w");
    /*
    for (std::vector<flexible_type> a: arr.range_iterator()) {
        for (float ai : a) {
            fprintf(f, "%f\n", ai);
        }
        fprintf(f, "\n");
    }
	*/
    //fclose(f);
    FILE *f = fopen("egbert.txt", "w");

    for (t_iteration = 1; t_iteration < observation_seq.size() + 1; t_iteration++) {
    	g = g.triple_apply(sum_shit, {"ait", "aij"});
        // https://github.com/dato-code/GraphLab-Create-SDK/blob/master/sdk_example/sgraph_weighted_pagerank.cpp
        // Normalization function
        // based on documentation at https://dato.com/products/create/sdk/docs/classgraphlab_1_1gl__sframe.html
        gl_sframe v = g.vertices();
        int parity = t_iteration % 2;
        
        int obseqt = observation_seq[t_iteration];
        
        g.vertices()["ait"] = g.vertices()[{"ait", "b"}].apply([f, obseqt](const std::vector<flexible_type>& x) {
            fprintf(f, "%f %f\n", x[0][t_iteration], x[1][obseqt]);
            return x[0][t_iteration] * x[1][obseqt];
        }, flex_type_enum::FLOAT);

        float normalizer = v[v["parity"] == parity]["ait"].apply([f](const std::vector<flexible_type>& x) { 
            fprintf(f, "%d %f\n", t_iteration, (float)x[t_iteration]);
            return (float)x[t_iteration];
        }, flex_type_enum::FLOAT).sum();

        fprintf(f, "%f\n", normalizer);
	}
        fclose(f);

	return g;
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "observation_seq"); // provide named parameters
END_FUNCTION_REGISTRATION
