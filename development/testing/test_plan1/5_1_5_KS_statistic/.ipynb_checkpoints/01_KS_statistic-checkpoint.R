# Supress Warnings in Prod
options(warn=-1)

########################################################################################################################
#' Installation of required packages - This part loads/ Installs packages that are required to perform model diagnostics
########################################################################################################################

full.list.of.packages <- c("dplyr","openxlsx","readr","bizdays","jrvFinance","xts","reshape2","ggplot2","moments","car","pROC")

new.packages <- full.list.of.packages[!(full.list.of.packages %in% utils::installed.packages()[,"Package"])]
if(length(new.packages)) utils::install.packages(new.packages)

# Import libraries
#inst <- lapply(full.list.of.packages, library, character.only = TRUE)

suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(bizdays))
suppressPackageStartupMessages(library(jrvFinance))
suppressPackageStartupMessages(library(xts))
suppressPackageStartupMessages(library(openxlsx))
suppressPackageStartupMessages(library(reshape2))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(moments))
suppressPackageStartupMessages(library(jsonlite))
suppressPackageStartupMessages(library(yaml))
suppressPackageStartupMessages(library(timeDate))
suppressPackageStartupMessages(library(rjson))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(car))
suppressPackageStartupMessages(library(pROC))

#' create the concatenate operator

'%+%' <- function(x,y) paste(x, y, sep="")

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

# Define KS function
KS <- function(data, pd, obs, n){
  ########################################################################
  #'
  #'  @param data: input dataset
  #'  @param pd: predicted value
  #'  @param obs: observed default variable
  #'  @param n: number of groups the data is to be splitted into
  #'  
  #'  @return KS statistic
  #'  
  ########################################################################
  
  #Sort data by decreasing PD
  data <- data[order(-data[pd]),]
  
  #Split data in n groups (grouped by probability of default): 
  ranks <- split(data, sort(rep_len(1:n, nrow(data[pd])))) #list of 20 datasets
  
  #number of bad (defaulted) per group:
  bad_counts <- sapply(ranks, function(x) sum(x[obs] == 1))
  
  #number of good (not defaulted) per group:
  good_counts <- sapply(ranks, function(x) sum(x[obs] == 0))
  
  #Calculate cumulative percentages of bad and good
  cumpercentage_bad <- 100*cumsum(bad_counts)/sum(bad_counts)
  cumpercentage_good <- 100*cumsum(good_counts)/sum(good_counts)
  
  #Calculate the absolute difference between good and bad cumulative percentages
  abs_diff <- abs(cumpercentage_good-cumpercentage_bad)
  
  # KS = maximum absolute difference of cumulative percentages
  ks <- max(abs_diff)
  return(ks)
}

# Specifying file paths

ROOT <- getCurrentFileLocation()
data_path = file.path(ROOT,"../../../data/interim")
#plot_loc <- ROOT %+% "/../../data/09_model_output/Graphs/"

# Get filename
params <- yaml.load_file(file.path(ROOT,"/../params.yaml"))
model_name <- paste(params$model_loading$model_name, '.RDS', sep='')
dpVar <- params$model_loading$bad_flag
n <- params$`KS-statistic`$num_of_groups

# Read Train Input Data File
X_train_File <- file.path(data_path,"X_train_transformed.csv")
y_train_File <- file.path(data_path,"y_train_transformed.csv")

X_train <- read.csv(X_train_File,check.names = FALSE)
y_train <- read.csv(y_train_File,check.names = FALSE)

train = cbind(X_train,y_train)

# Read Test Input Data File
X_test_File <- file.path(data_path,"X_test_transformed.csv")
y_test_File <- file.path(data_path,"y_test_transformed.csv")

X_test <- read.csv(X_test_File,check.names = FALSE)
y_test <- read.csv(y_test_File,check.names = FALSE)

test = cbind(X_test,y_test)

#full_data = rbind(train,test)

# Load model
Reg <- readRDS(file.path(ROOT,"../00_model_loading",model_name))

# Creating a new workbook for outputs or use an existing template
# wb <- createWorkbook()

print("Running KS statistic ...")

#training data
prob_train=predict(Reg,train,type=c("response"))
train$prob=prob_train

#testing data
prob_test=predict(Reg,test,type=c("response"))
test$prob=prob_test

#Calculate output
output_train <- KS(train, "prob", dpVar, n)
output_test <- KS(test, "prob", dpVar, n)

final <-data.frame(output_train,output_test)
names(final) = c("KS_statistic_train","KS_statistic_test")
final = final/100
#final <-data.frame("KS statistic"=output[1]/100)

# tryCatch({addWorksheet(wb, "KS statistic", gridLines = FALSE) }, error=function(e){})
# writeData(wb, "KS statistic", "KS statistic", startRow = 1,startCol = 1)
# writeDataTable(wb, "KS statistic", final, startRow = 2,startCol = 1, rowNames = FALSE, tableStyle = "TableStyleLight9")

# Output Results to Excel file placed at .../Output/Output Files
###################################################################################################

# fileName <- paste0(ROOT %+% "/../../data/09_model_output/Output_Files/Output_" %+% format(Sys.time(),"%Y%m%d%H%M") %+% "KS_statistic"  %+% ".xlsx")
# #print("Building Output ...")
# saveWorkbook(wb, fileName, overwrite = TRUE)
# #print("Output Ready ...")

###################################################################################################
# Output Results to JSON file placed at ../Statistical Test/docs
###################################################################################################

fileName <- paste0("output",".json")
fileNamePath = paste0(ROOT,"/output","/" ,fileName)

print("start writting JSON file...")
write_json(unbox(final), fileNamePath)
print("complete writing JSON file")
