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
# change to the path to your script
source('E:/path/to/this/script/functions.R')
# for example: source('E:/LandsatSentinel-preprocessing/functions.R')

# =============================================================================
# Part I - Best-Available-Pixel compositing
# =============================================================================

# Change year and path to your data
year <- 2014
dir_main <- paste('e:/data_krkonose/', as.character(year), sep='')
setwd(dir_main)
getwd()

# =============================================================================
# 1) Prepare input

# create list of desired image band files
l_files <- list.files(pattern='time_series_.*.tif$')
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
plot(cdists)

l_stacks[[7]] <- cdists
#vld <- raster::stack('imagery/bap/2014-2016_001-365_HL_TSA_LNDLG_VLD_TSS.tif')


# =============================================================================
# 2) Parameterization

# Composite 1
# parameters
target_year <- year
target_doy <- 175

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
comp <- raster::brick(c(l_composites, bapscore1$doy, bapscore1$score*10000))
print(comp)

dir.create('results')
outname <- paste0('results/composite_', toString(target_year), '-', 
                  toString(max_yoff), '_DOY', toString(target_doy), '-', 
                  toString(max_doff), '.tif')
writeRaster(comp, outname, format='GTiff', datatype = 'INT2U', overwrite=T,
            progress='text')

