# gather all results from output files to csv
tail --lines 1 *.out > fullout.csv
tail --quiet --lines 1 *.out > data.csv
