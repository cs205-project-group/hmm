#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include <fstream>
#include <assert.h>

#define NUM_STATES 5

using namespace graphlab;
using namespace std;

std::vector<flexible_type> vector_multiply(std::vector<flexible_type> a, 
        std::vector<flexible_type> b) {

    assert(a.size() == b.size());
    std::vector<flexible_type> result;
    result.resize(b.size());

    for (int i = 0; i < a.size(); i++) {
        result[i] = a[i] * b[i];
    }

    return result;
}

std::vector<flexible_type> vector_divide(std::vector<flexible_type> a,
        std::vector<double> b) {
    assert(a.size() == b.size());
    std::vector<flexible_type> result;
    result.resize(b.size());

    for (int i = 0; i < a.size(); i++) {
        result[i] = a[i] / b[i];
    }

    return result;
}

void get_gammas(gl_sgraph& g) {

}

gl_sgraph fp(gl_sgraph& g, std::vector<int> observation_seq) {

int t_iteration;
int obseqt;
double normalizer = 1;

    std::vector<double> normalizers(observation_seq.size() + 1,1);

    // compute alpha_i(t)
    for (t_iteration = 1; t_iteration < observation_seq.size() + 1; t_iteration++) {
        // https://github.com/dato-code/GraphLab-Create-SDK/blob/master/sdk_example/sgraph_weighted_pagerank.cpp
        // Normalization function
        // based on documentation at https://dato.com/products/create/sdk/docs/classgraphlab_1_1gl__sframe.html
        obseqt = observation_seq[t_iteration - 1]; 
        // note ait is 1-indexed while observation sequence is 0 indexed
     	g = g.triple_apply([t_iteration, obseqt, normalizer](edge_triple& triple) {
            triple.target["ait"][t_iteration] += triple.target["b"][obseqt] * (((float)triple.source["ait"][t_iteration-1] / normalizer) * (float)triple.edge["aij"]);

            if (triple.source["i"] == (triple.target["i"] - 1 + NUM_STATES) % NUM_STATES) {
                triple.target["ait"][t_iteration] += triple.target["b"][obseqt] * (((float)triple.target["ait"][t_iteration-1] / normalizer) * (float)triple.target["self"]);
                
            }


        }, {"ait", "aij", "b"});

        gl_sframe v = g.vertices();

        normalizer = v["ait"].apply([t_iteration](const std::vector<flexible_type>& x) { 
            return (float)x[t_iteration];
        }, flex_type_enum::FLOAT).sum();
        normalizers[t_iteration] = normalizer;

	}

	// calculate beta_i(t)
    for (t_iteration = observation_seq.size() -1; t_iteration >= 0; t_iteration--) {
        logprogress_stream << t_iteration;
        // https://github.com/dato-code/GraphLab-Create-SDK/blob/master/sdk_example/sgraph_weighted_pagerank.cpp
        // Normalization function
        // based on documentation at https://dato.com/products/create/sdk/docs/classgraphlab_1_1gl__sframe.html
        
        obseqt = observation_seq[t_iteration];
        logprogress_stream << "obseqt: ";
        logprogress_stream << obseqt;
        double normalizer = normalizers[t_iteration + 1];
        logprogress_stream << normalizers[t_iteration + 1];
        // Ding, note bit is 1-indexed while observation sequence is 0 indexed.
        // fuck off 
     	g = g.triple_apply([t_iteration, obseqt, normalizer](edge_triple& triple) {

		triple.source["bit"][t_iteration] += triple.target["b"][obseqt] * (((double)triple.target["bit"][t_iteration+1]) * (double)triple.edge["aij"]) / normalizer;

            if (triple.target["i"] == (triple.source["i"] - 1 + NUM_STATES) % NUM_STATES) {

		triple.source["bit"][t_iteration] += triple.source["b"][obseqt] * (((double)triple.source["bit"][t_iteration+1]) * (double)triple.source["self"]) / normalizer;
                
            }

        }, {"bit"});
	}

    g.vertices()["git"] = g.vertices()[{"ait", "bit"}].apply([normalizers](const std::vector<flexible_type>& x) { 
        return vector_divide(vector_multiply(x[0], x[1]), normalizers); 
    }, flex_type_enum::LIST);

    // update Xi, first edges, then self edges in vertices
    // Kevin, note bit is 1-indexed while observation sequence is 0 indexed.
    // Thanks, Ding. I love comments. They're so helpful. 
    g = g.triple_apply([observation_seq, normalizers](edge_triple& triple) {
        for (int t = 1; t < observation_seq.size(); t++) {
            triple.edge["xi"] += triple.source["ait"][t]*triple.edge["aij"]*triple.target["bit"][t+1]*triple.target["b"][observation_seq[t]] / (normalizers[t+1] * normalizers[t]);

        }


    },{"xi"});
    // self edges


    return g;
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "observation_seq"); // provide named parameters
END_FUNCTION_REGISTRATION
