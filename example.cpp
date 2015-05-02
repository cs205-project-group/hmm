#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include<fstream>

using namespace graphlab;
using namespace std;
void sum_shit(edge_triple& triple) {
    triple.target["ait"] += triple.edge["aij"] * triple.source["ait"];
}

gl_sgraph fp(gl_sgraph& g, std::vector<std::vector<float>> B) {

   // fill in Bi* for each vertex i
   // https://dato.com/products/create/sdk/docs/page_userguide_sframe.html
   g.vertices()["i"] = g.vertices().apply([&B](const std::vector<flexible_type>& row) { 
        FILE *file = fopen("test.txt", "w+");

        for (float b : row)
            fprintf(file, "%f ", b);
        printf("\n");
        fclose(file);
        (void)B;
        float x = row[0];
            return x; },

  flex_type_enum::FLOAT);
  return g.triple_apply(sum_shit, {"ait", "aij"});
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "B"); // provide named parameters
END_FUNCTION_REGISTRATION
