#Load required package

suppressPackageStartupMessages(library(yaml))
suppressPackageStartupMessages(library(openxlsx))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(jsonlite))
suppressPackageStartupMessages(library(randomForest))

# get current file location
getCurrentFileLocation <-  function()
{
  this_file <- commandArgs() %>%
    tibble::enframe(name = NULL) %>%
    tidyr::separate(col=value, into=c("key", "value"), sep="=", fill='right') %>%
    dplyr::filter(key == "--file") %>%
    dplyr::pull(value)
  if (length(this_file)==0)
  {
    this_file <- rstudioapi::getSourceEditorContext()$path
  }
  return(dirname(this_file))
}

#-------------------------------------------------------------------------------------------------------------
# Specifying file paths
ROOT <- getCurrentFileLocation()
data_path = paste0(ROOT,"/../../data/interim")
inputFileName <- "TREPP_sample-dataset_term-defaults_post_dq.csv"
development_act <- read.csv(paste(data_path,inputFileName,sep="/"))  
#ncol <- ncol(development_act)
#development_act <-development_act[,2:ncol]

params <- yaml.load_file(file.path(ROOT,"/params.yaml"))
numerical_columns_as_features <- params$model_development$numerical_columns_as_features
bad_flag <- params$model_development$bad_flag

m<-length(numerical_columns_as_features)

# read the summary table
#num_file <- read.csv(paste(data_path, "summary_numerical_after_outlier_detection.csv", sep = "/"))
#n_var<- length(num_file$X)
#vars <- as.vector(num_file$X)

# defind the functions of capping
Capping <- function(input, vars, a, b){
  
  #x <- as.data.frame(input[ ,vars])
  #x <- x[is.numeric(x)]
  #x <- x[complete.cases(x),]
  
  num_of_treated_obs <- NULL
  pct_of_treated_obs <- NULL
  for(i in 1:length(vars)){
    y <- input[,vars[i]]
    #qnt <- quantile(y, probs=c(.25, .75), na.rm = T)
    #min <- sort(y)[.05*length(y)]
    #max <- sort(y)[.95*length(y)]
    caps <- quantile(y, probs=c(a, b), na.rm = T)
    #H <- 1.5 * IQR(y, na.rm = T)
    max <- y[y > (caps[2])]
    min <- y[y < (caps[1])]
    num_of_treated_obs <- c(num_of_treated_obs, length(min)+length(max))
    pct_of_treated_obs <- c(pct_of_treated_obs,(length(min)+length(max))/length(y))
    y[y < (caps[1])] <- caps[1]
    y[y > (caps[2])] <- caps[2]
    input[,vars[i]] <- y
  }
  list <- data.frame(vars, num_of_treated_obs, pct_of_treated_obs)
  return(list(input, list))
} 


# Read the list of chosen variables
params <- yaml.load_file(file.path(ROOT,"/params.yaml"))
b <- params$data_quality$cap
a <- params$data_quality$floor

vars <- numerical_columns_as_features
var_length <- length(vars)
#vars <- c()
#for(i in 1:var_length){vars <- c(vars, params$Capping$vars[[i]])}

# Run the R script
output <- Capping(development_act, vars, a, b)

# Export the data frame
output_csv_path <- paste(data_path,"Trepp_after_outlier_capping.csv",sep = "/")
write.csv(as.data.frame(output[1]), file = output_csv_path, row.names=F)
df_out = as.data.frame(output[1])
temp = as.data.frame(output[2])
#output_table = data.frame(cbind(num_file, temp[,2:3]))
#names(output_table)[names(output_table)=="X"] = "variable"

data_path = paste0(ROOT,"/../../data/interim/TREPP_sample-dataset_term-defaults_post_dq_capping.csv")
write.csv(df_out, file = data_path, row.names=F)
##########new json file creation######################

#output_csv_path1 <- paste0(ROOT,"/5_1_1_data_quality/output/output_summary.csv")
#write.csv(temp, output_csv_path1, row.names=F)
output_json_path2 <- paste0(ROOT,"/5_1_1_data_quality/output/output_summary.json")
write_json(temp, output_json_path2, row.names=F)


