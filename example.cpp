#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include<fstream>

using namespace graphlab;
using namespace std;
void sum_shit(edge_triple& triple) {
    triple.target["ait"] += triple.edge["aij"] * triple.source["ait"];
}

gl_sgraph fp(const gl_sgraph& g, std::vector<std::vector<float>> B) {

   // https://dato.com/products/create/sdk/docs/page_userguide_sframe.html
   g.vertices().apply([](const std::vector<flexible_type>& row) { return row[0] + row[1]; },

  flex_type_enum::VECTOR));
   return g.triple_apply(sum_shit, {"ait", "aij"});
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "B"); // provide named parameters
END_FUNCTION_REGISTRATION
