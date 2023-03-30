# =============================================================================
# GCG - EARTH OBSERVATION
# BEST AVAILABLE PIXEL (BAP) COMPOSITING
# based on Griffith et al. 2013
# L. Nill, 2022
# =============================================================================

# =============================================================================
# load required packages
library(raster)

# =============================================================================
# scoring function
bap_score <- function(doy, year, cloud_dist, target_doy, target_year, 
                      w_doy=0.5, w_year=0.2, w_cloud_dist=0.3,
                      max_doy_offset=30, max_year_offset=1,
                      min_cloud_dist=0, max_cloud_dist=1000, 
                      valid_pixels=NULL){
  "Function to calculate BAP score based on provided DOY, year and cloud 
  distance information. Supplied objects must exhibit the same length to be
  braodcasted together.
  
  doy:            (numeric) Vector containing DOYs. Must be of same length as 
                  cloud_dist.
  year:           (numeric) Vector containing Years. Must be of same length as 
                  cloud_dist.
  cloud_dist:     (raster) Raster object representing distance to clouds (unit 
                  must match min_cloud_dist and max_cloud_dist)
  target_doy:     (int) Target day-of-year (mean of Gaussian PDF)
  target_year:    (int) Target year (peak of piecewise linear function)
  w_doy:          (float) Weight associated with the DOY score 
  w_year:         (float) Weight associated with the year score
  w_cloud_dist:   (float) Weight associated with the cloud distance score
  max_doy_offset: (int) Maximum at which DOY score = 0 
  max_year_offset:(int) Maximum at which year score = 0
  min_cloud_dist: (int) Minimum at which cloud score = 0
  max_cloud_dist: (int) Maximum at which cloud score = 1
  valid_pixels:   (raster, optional)
  
  returns:        (list) Raster (stack) containing pixel-wise index of maximum 
                  score [1], maximum score [2], doy [3] and year [4] of maximum 
                  score.
  "
  
  # assert if weights sum up to 1
  if (sum(w_doy, w_year, w_cloud_dist) != 1){
    stop('Error: Specified weights NEQ 1')
  }
  
  # assert if doy, year, cloud_dist are of same length
  zdim <- dim(cloud_dist)[3]
  if (length(unique(list(zdim, length(year), length(doy)))) != 1){
    stop('Error: Inputs doy, year, cloud_dist of different length')
  }
  
  # 1) DOY score (Gaussian kernel)
  print("1/5 Calculating DOY score.")
  score_doy <- exp(-0.5 * ((doy - target_doy) / (max_doy_offset/3))^2)
  
  # 2) Year score
  print("2/5 Calculating YEAR score.")
  score_year <- 1-(abs(target_year - year) / (max_year_offset+0.1))
  
  # plot year and doy scoring
  par(mfrow=c(2,1))
  plot(seq(0,365,1), exp(-0.5*((seq(0,365,1)-target_doy)/(max_doy_offset/3))^2),
       type = "l", xlab="Day of Year", ylab="Score")
  points(doy, score_doy, col=factor(year), lwd=1)
  legend("topleft",
         legend = levels(factor(year)),
         pch = 1,
         col = factor(levels(factor(year))))
  plot(seq(min(year)-1,max(year)+1,1), 
       1-(abs(target_year-seq(min(year)-1,max(year)+1,1))/(max_year_offset+0.1)),
       type = "l", xlab="Day of Year", ylab="Score")
  points(year, score_year, col="red")
  
  # 3) Cloud score
  print("3/5 Calculating cloud_dist score.")
  cloud_dist <- reclassify(cloud_dist, rcl=c(0, min_cloud_dist, NA), right=NA, 
                           datatype='INT2S')
  cloud_dist <- reclassify(cloud_dist, rcl=c(max_cloud_dist, Inf, max_cloud_dist), right=NA, 
                           datatype='INT2S')
  score_cloud <- (cloud_dist - min_cloud_dist) / (max_cloud_dist - min_cloud_dist)
  
  # net score
  print("4/5 Calculating NET score.")
  score <- score_doy*w_doy + score_year*w_year + score_cloud*w_cloud_dist
  if (!is.null(valid_pixels)){
    score <- score * valid_pixels
  }
  
  # get index of maximum score and associated scores
  print("5/5 Calculating index of MAX score.")
  idx_max <- which.max(score)
  score_max <- max(score, na.rm=T)
  
  # look-up for year and doy raster
  lu_doy <- cbind(1:zdim, doy)
  lu_year <- cbind(1:zdim, year)
  doy_max <- reclassify(idx_max, rcl=lu_doy, right=NA, datatype='INT2S')
  year_max <- reclassify(idx_max, rcl=lu_year, right=NA, datatype='INT2S')
  
  out_stack <- raster::brick(list(idx_max, score_max, doy_max, year_max))
  names(out_stack) <- c("idx", "score", "doy", "year")
  plot(out_stack)
  
  print("Done.")
  return(out_stack)
}

# =============================================================================
# function to create composites from imagery based on suitability/score layer

create_bap <- function(img_raster, idx_raster){
  "Function to create BAP composite from raster stack using index raster.
  
  img_raster:   (raster) Input (3D) image data for compositing.
  idx_raster:   (raster) Input (2D) index raster containing pixel-wise index
                along z-dimension of img_raster.
  
  returns:      (raster) Best-available-pixel composite (2D) image
  
  "
  # get unique selected scenes only
  idx_unique <- sort(unique(idx_raster, na.last=NA))
  img_raster <- img_raster[[idx_unique]]
  # reset index (because of sub-selection)
  idx_raster <- reclassify(idx_raster, 
                           rcl=cbind(idx_unique, 1:dim(img_raster)[3]))
  # read data into matrices
  img_matrix <- as.matrix(img_raster)
  idx_matrix <- as.vector(idx_raster)
  bap <- img_matrix[cbind(seq_len(nrow(img_matrix)), idx_matrix)]  # index
  bap <- raster(nrows=img_raster@nrows, 
                ncols=img_raster@ncols, 
                crs=img_raster@crs, 
                vals=bap,
                ext=extent(img_raster))
  return(bap)
}

# EOF