library(data.table)

# if you don't have this library installed, run
# install.packages('data.table')

# read the data
runtimes.raw <- read.csv('data.csv')

# manually input the number of cores used
# cross-verified from looking at the fullout.csv file
cores <- rep(c(16, 2, 32, 4, 8), rep(18, 5))
runtimes.raw$CORES <- cores

# remove the missing ones (the ones that didn't run)
runtimes <- data.table(na.omit(runtimes.raw))

# convert NUM_STATES to numbers
runtimes[, NUM_STATES:=as.numeric( levels(NUM_STATES) )[NUM_STATES] ]
# ignore the warning message about NAs. It's there because there really are
# NAs in the original data but not after we do na.omit
numStates <- sort(unique(runtimes[, NUM_STATES]))
obsLen <- sort(unique(runtimes[, OBS_LEN]))
cores <- sort(unique(runtimes[, CORES]))

# create directory for figures
dir.create("../figure")
# will give a warning if this directory already exists. Can safely ignore it

# show runtime vs. processors
for (n in numStates) {
    for (obs in obsLen) {
        if ( (n == 1024) && (obs == 500) ) {
            # no observations here
            next
        }
        subtitle <- sprintf("N=%d, M=%d, T=%d", n, n, obs)
        pdat <- runtimes[NUM_STATES==n & NUM_OBS==n & OBS_LEN==obs, 
                        list(SERIAL, PARALLEL, CORES)]
        pdat <- pdat[order(CORES)]

        fname <- sprintf("../figure/runtime-N_%d-T_%d.pdf", n, obs)
        pdf(fname) # plot will be written to pdf
        plot(pdat[, CORES], pdat[, PARALLEL], type='b',
             ylim=c(min(pdat[, SERIAL]), max(pdat[, PARALLEL])), 
             main=paste("Runtime", subtitle, sep='\n'), 
             xlab="Number of Cores", ylab="Runtime (s)")
        points(pdat[, CORES], pdat[, SERIAL], pch=19, type='b', lty=2)
        legend('right', legend=c("Parallel", "Serial"), pch=c(1, 19),
               lty=c(1,2))
        dev.off()
        #print("Press [ENTER] to continue:")
        #lin <- readline()
    }
}

# show scaling
for (core in cores) {
    for (obs in obsLen) {
        pdat <- runtimes[CORES==core & OBS_LEN==obs, 
                         list(NUM_STATES, SERIAL=log2(SERIAL), 
                              PARALLEL=log2(PARALLEL))]
        pdat <- pdat[order(NUM_STATES)]
        pdat[, NUM_STATES:=log2(NUM_STATES)]
        subtitle <- sprintf("T=%d, %d cores", obs, core)

        fname <- sprintf("../figure/scaling-cores_%d-T_%d.pdf", core, obs)

        pdf(fname) # plot will be written to pdf
        plot(pdat[, NUM_STATES], pdat[, PARALLEL], type='b', 
            ylim=c(min(pdat[, SERIAL]), max(pdat[, PARALLEL])), 
            main=paste("Scaling", subtitle, sep='\n'), 
            xlab="log2(Number of states N)", ylab="log2(Runtime (s))")
        points(pdat[, NUM_STATES], pdat[, SERIAL], pch=19, type='b')
        legend('bottomright', legend=c("Parallel", "Serial"), pch=c(1, 19),
               lty=c(1,2))
        dev.off()
        #print("Press [ENTER] to continue:")
        #lin <- readline()
    }
}
