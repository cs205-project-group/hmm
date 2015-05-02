#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include<fstream>

using namespace graphlab;
using namespace std;

int t_iteration;

void sum_shit(edge_triple& triple) {
    //triple.target["ait"] += triple.edge["aij"] * triple.source["ait"];

   	if (t_iteration % 2 != (int)triple.edge["parity"]) {
   		triple.target["ait"][t_iteration] += ((float)triple.source["ait"][t_iteration-1] * (float)triple.edge["aij"]);
   	}
    //triple.target["ait"][0] = 0;

}

gl_sgraph fp(gl_sgraph& g, std::vector<int> observation_seq) {



   // fill in Bi* for each vertex i
   // https://dato.com/products/create/sdk/docs/page_userguide_sframe.html
    //gl_sarray arr = g.vertices()["b"];
    FILE *f = fopen("test.txt", "w");
    /*
    for (std::vector<flexible_type> a: arr.range_iterator()) {
        for (float ai : a) {
            fprintf(f, "%f\n", ai);
        }
        fprintf(f, "\n");
    }
	*/
    //fclose(f);
    for (t_iteration = 1; t_iteration < observation_seq.size() + 1; t_iteration++) {
    	g = g.triple_apply(sum_shit, {"ait", "aij"});
    	fprintf(f, "%d\n", t_iteration);
    	fflush(f);
	}
	fclose(f);

	return g;
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "observation_seq"); // provide named parameters
END_FUNCTION_REGISTRATION
