# =============================================================================
# GCG - EARTH OBSERVATION
# SESSION 4: Higher level image features
# Name, Name, ...
# =============================================================================

# =============================================================================
# load required packages
l_packages <- c("raster", "rgdal", "lubridate")
for (p in l_packages){
  if(! p %in% installed.packages()){
    install.packages(p, dependencies = TRUE)
  }
  library(p, character.only = T)
}

# path to the bap_compositing-function including .R suffix
getwd()
source('E:/LandsatSentinel-preprocessing/functions.R')

# =============================================================================
# Part I - Best-Available-Pixel compositing
# =============================================================================

year <- 2022
dir_main <- paste('e:/data_krkonose/', as.character(year), sep='')
setwd(dir_main)
getwd()

# =============================================================================
# 1) Prepare input

# create list of desired image band files
l_files <- list.files(pattern='time_series_.*.tif')
print(l_files)

# read raster stacks
l_stacks <- lapply(l_files, raster::stack)

# retrieve necessary variables for compositing (DOYs and year vectors)
dates <- unlist(as.list(read.delim('acquisition_dates.txt', header=FALSE, colClasses="character")$V1))
datestring <- lapply(dates, function(x) as.Date(x, "%Y%m%d"))
doys <- as.numeric(lapply(datestring, yday))
years <- as.numeric(lapply(datestring, year))

# read cloud distance and valid pixels (masks) stacks

cdists <- raster::stack(list.files(pattern='*CDIST.tif')[[1]])
cdists <- cdists * 10 # needs to be converted to meters, cloud distance rasters from earth explorer are in 0.1m
#vld <- raster::stack('imagery/bap/2014-2016_001-365_HL_TSA_LNDLG_VLD_TSS.tif')


# =============================================================================
# 2) Parameterization

# Composite 1
# parameters
target_year <- 2022
target_doy <- 200

w_year <- 0.0
w_doy <- 0.5
w_cdist <- 0.5

max_doff <- 100
max_yoff <- 0

min_cdist <- 0
max_cdist <- 200

# call bap_score-function for 1st composite
bapscore1 <- bap_score(doy=doys, year=years, cloud_dist=cdists, 
                       target_doy=target_doy, target_year=target_year, 
                       w_doy=w_doy, w_year=w_year, w_cloud_dist=w_cdist, 
                       max_doy_offset=max_doff, max_year_offset=max_yoff, 
                       min_cloud_dist=min_cdist, max_cloud_dist=max_cdist)

# create composites for each band from index object
l_composites <- lapply(l_stacks, create_bap, idx_raster=bapscore1$idx)

# create stack of composite rasters + DOY and YEAR info and write to disc
comp <- raster::brick(c(l_composites, bapscore1$doy, bapscore1$score))
print(comp)

outname <- paste0('test_', toString(target_year), '-', 
                  toString(max_yoff), '_DOY', toString(target_doy), '-', 
                  toString(max_doff), '.tif')
writeRaster(comp, outname, format='GTiff', datatype = 'INT2U', overwrite=T,
            progress='text')

# Composite 2
# ...


# =============================================================================
# Part II - Spectral-Temporal-Metrics
# =============================================================================
# ..


evi <- stack('imagery/time-series/2014-2016_001-365_HL_TSA_LNDLG_EVI_TSS.tif')
tcb <- stack('imagery/time-series/2014-2016_001-365_HL_TSA_LNDLG_TCB_TSS.tif')
tcg <- stack('imagery/time-series/2014-2016_001-365_HL_TSA_LNDLG_TCG_TSS.tif')

# retrieve temporal information from bandnames
library(lubridate)
datestring <- unlist(lapply(names(tcb), function(x) substr(x, 2, 9)))
dates <- as.POSIXlt(datestring, format = "%Y%m%d")

# on this date-object, we can perform logical operations
# for example, let's find the indices for the months June-August only
condition <- (year(dates) %in% 2014:2016) & (month(dates) %in% 8:11)

# convert raster subset to matrix
evi_matrix <- as.matrix(evi[[which(condition)]])
tcg_matrix <- as.matrix(tcg[[which(condition)]])
tcb_matrix <- as.matrix(tcb[[which(condition)]])

# calculate P10 across rows in matrix
# evi_p10 <- apply(evi_matrix, 1, FUN=quantile, probs = c(.10), na.rm=T)
# evi_p10 <- apply(evi_matrix, 1, FUN=sd, na.rm=T)
evi_p10 <- apply(evi_matrix, 1, FUN=quantile, probs = c(.85), na.rm=T)
tcg_p10 <- apply(tcg_matrix, 1, FUN=quantile, probs = c(.85), na.rm=T)
tcb_p10 <- apply(tcb_matrix, 1, FUN=sd, na.rm=T)

# write results to empty raster
evi_p10_raster <- raster(nrows=evi@nrows, 
                         ncols=evi@ncols, 
                         crs=evi@crs, 
                         vals=evi_p10,
                         ext=extent(evi))

tcg_p10_raster <- raster(nrows=evi@nrows, 
                         ncols=evi@ncols, 
                         crs=evi@crs, 
                         vals=tcg_p10,
                         ext=extent(evi))

tcb_p10_raster <- raster(nrows=evi@nrows, 
                         ncols=evi@ncols, 
                         crs=evi@crs, 
                         vals=tcb_p10,
                         ext=extent(evi))



outname_stm <- 'tcb_811_sd.tif'
writeRaster(tcb_p10_raster, outname_stm, format='GTiff', datatype = 'INT2S', overwrite=T,
            progress='text')

# plot result
plot(evi_p10_raster)
