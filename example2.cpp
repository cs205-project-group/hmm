#include <graphlab/sdk/toolkit_function_macros.hpp>
#include <graphlab/sdk/gl_sgraph.hpp>
#include <iostream>
#include <fstream>
#include <assert.h>

#define NUM_STATES 5
#define NUM_OBSERVATIONS 5
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

	logprogress_stream << "next iteration";

	int t_iteration;
	int obseqt;
	double normalizer = 1;
    	int OBSEQ_SIZE = observation_seq.size();
    	std::vector<double> normalizers(OBSEQ_SIZE + 1,1);

	logprogress_stream << "compute alpha_t";
    // compute alpha_i(t)
    for (t_iteration = 1; t_iteration < OBSEQ_SIZE + 1; t_iteration++) {
	logprogress_stream << t_iteration;

        // https://github.com/dato-code/GraphLab-Create-SDK/blob/master/sdk_example/sgraph_weighted_pagerank.cpp
        // Normalization function
        // based on documentation at https://dato.com/products/create/sdk/docs/classgraphlab_1_1gl__sframe.html
        obseqt = observation_seq[t_iteration - 1]; 
        // note ait is 1-indexed while observation sequence is 0 indexed
	logprogress_stream << "triple apply";
     	g = g.triple_apply([t_iteration, obseqt, normalizer](edge_triple& triple) {
	  //   logprogress_stream << "edge apply";
	    logprogress_stream << triple.target["git"];

            triple.target["ait"][t_iteration] += triple.target["b"][obseqt] * (((float)triple.source["ait"][t_iteration-1] / normalizer) * (float)triple.edge["aij"]);
	//	logprogress_stream << "Rihanna";
            if (triple.source["i"] == (triple.target["i"] - 1 + NUM_STATES) % NUM_STATES) {
                triple.target["ait"][t_iteration] += triple.target["b"][obseqt] * (((float)triple.target["ait"][t_iteration-1] / normalizer) * (float)triple.target["self"]);
                
            }


        }, {"ait"});

        gl_sframe v = g.vertices();

        normalizer = v["ait"].apply([t_iteration](const std::vector<flexible_type>& x) { 
            return (float)x[t_iteration];
        }, flex_type_enum::FLOAT).sum();
        normalizers[t_iteration] = normalizer;

	}
	logprogress_stream << "ait finished";

	// calculate beta_i(t)
    for (t_iteration = OBSEQ_SIZE -1; t_iteration >= 0; t_iteration--) {
        // https://github.com/dato-code/GraphLab-Create-SDK/blob/master/sdk_example/sgraph_weighted_pagerank.cpp
        // Normalization function
        // based on documentation at https://dato.com/products/create/sdk/docs/classgraphlab_1_1gl__sframe.html
        
        obseqt = observation_seq[t_iteration];
        double normalizer = normalizers[t_iteration + 1];
        // Ding, note bit is 1-indexed while observation sequence is 0 indexed.
        // fuck off 
     	g = g.triple_apply([t_iteration, obseqt, normalizer](edge_triple& triple) {

		triple.source["bit"][t_iteration] += triple.target["b"][obseqt] * (((double)triple.target["bit"][t_iteration+1]) * (double)triple.edge["aij"]) / normalizer;

            if (triple.target["i"] == (triple.source["i"] - 1 + NUM_STATES) % NUM_STATES) {

		triple.source["bit"][t_iteration] += triple.source["b"][obseqt] * (((double)triple.source["bit"][t_iteration+1]) * (double)triple.source["self"]) / normalizer;
                
            }

        }, {"bit"});
	}

	logprogress_stream << "bit finished";
        g.vertices()["git"] = g.vertices()["ait"] * g.vertices()["bit"] / normalizers;
/*    g.vertices()["git"] = g.vertices()[{"ait", "bit"}].apply([normalizers](const std::vector<flexible_type>& x) { 
        return vector_divide(vector_multiply(x[0], x[1]), normalizers); 
    }, flex_type_enum::LIST);*/
	logprogress_stream << "git finished";

    int obseq_size = OBSEQ_SIZE;
    g.vertices()["git_sum"] = g.vertices()[{"git"}].apply([obseq_size](const std::vector<flexible_type>& x) { 
	float git_sum = 0;
	for (int t = 1; t <= obseq_size; t++) {
		git_sum += (float)x[t];
	}
	return git_sum;
    }, flex_type_enum::FLOAT);


	logprogress_stream << "git_sum finished";

    // update Xi, first edges, then self edges in vertices
    // Kevin, note bit is 1-indexed while observation sequence is 0 indexed.
    // Thanks, Ding. I love comments. They're so helpful. 
    g = g.triple_apply([observation_seq, normalizers, OBSEQ_SIZE](edge_triple& triple) {
        float xi = 0;

	for (int t = 1; t < OBSEQ_SIZE; t++) {
        	xi += (float)(triple.source["ait"][t]*triple.edge["aij"]*triple.target["bit"][t+1]*triple.target["b"][observation_seq[t]] / (normalizers[t+1] * normalizers[t]));
        }

	triple.edge["aij"] = xi/triple.source["git_sum"];

    },{"aij"});

    g.vertices()["self"] = g.vertices()[{"ait", "self", "bit", "b", "git_sum"}].apply([observation_seq, normalizers, OBSEQ_SIZE](const std::vector<flexible_type>& x) {
	float self_sum = 0.0;
	for (int t = 1; t < OBSEQ_SIZE; t++) {
		self_sum += (float)x[0][t] * (float)x[1] * (float)x[2][t + 1] * (float)x[3][observation_seq[t]] / (normalizers[t] * normalizers[t+1]);
        }
	return self_sum / x[4];

    }, flex_type_enum::FLOAT);

    // self edges
    g.vertices()["b"] = g.vertices()[{"git"}].apply([observation_seq](const std::vector<flexible_type>& x) {
	    std::vector<double> result;
	    result.resize(NUM_OBSERVATIONS);
	    for (int i = 0; i < NUM_OBSERVATIONS; i++) {
		result[i] = 0.0;
		float summ = 0;
		for (int j = 0; j < observation_seq.size(); j++) {
			if (observation_seq[j] == i) {
				result[i] += (float)(x[j+1]);
			}
			summ+=(float)(x[j+1]);

		}
	    	result[i] /= summ;
            }
	    return result;
    }, flex_type_enum::VECTOR);

    g.vertices()["bit"] = g.vertices().apply([OBSEQ_SIZE](const std::vector<flexible_type>& x) {
	std::vector<double> result(OBSEQ_SIZE + 1, 0.0);
	result[OBSEQ_SIZE] = 1.0;
	return result;    	
    }, flex_type_enum::VECTOR);


    g.vertices()["ait"] = g.vertices()[{"git"}].apply([OBSEQ_SIZE](const std::vector<flexible_type>& x) {
	std::vector<double> result(OBSEQ_SIZE + 1, 0.0);
	result[0] = x[0][0];
	return result;    	
    }, flex_type_enum::VECTOR);

/*    g.vertices()["git"] = g.vertices().apply([OBSEQ_SIZE](const std::vector<flexible_type>& x) {
	std::vector<flexible_type> result(OBSEQ_SIZE + 1, 0.0);
	return result;    	
    }, flex_type_enum::LIST);
*/

    g.vertices()["git_sum"] = 0.0;

    return g;
}

BEGIN_FUNCTION_REGISTRATION
REGISTER_FUNCTION(fp, "g", "observation_seq"); // provide named parameters
END_FUNCTION_REGISTRATION
