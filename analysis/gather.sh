# gather all results from output files to csv
tail --lines 1 *.out > fullout.csv
echo "NUM_STATES,NUM_OBS,OBS_LEN,SERIAL,PARALLEL" > data.csv
tail --quiet --lines 1 *.out >> data.csv
