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

# Specifying file paths

ROOT <- getCurrentFileLocation()
data_path = file.path(ROOT,"../../../data/interim")
#plot_loc <- ROOT %+% "/../../data/09_model_output/Graphs/"

# Get filename
params <- yaml.load_file(file.path(ROOT,"../params.yaml"))
model_name <- paste(params$model_loading$model_name, '.RDS', sep='')
dpVar <- params$model_loading$bad_flag

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

full_data = rbind(train,test)
Indicator = full_data[,dpVar]

# Load model
Reg <- readRDS(file.path(ROOT,"../00_model_loading",model_name))

# Creating a new workbook for outputs or use an existing template
#wb <- createWorkbook()

print("Running ROC curve ...")
prob=predict(Reg,full_data,type=c("response"))
full_data$prob=prob
#rocFormula <- dpVar %+% " ~ " %+% "prob"
g <- roc(Indicator ~ prob,data=full_data)
plot(g)
aucOutput<-auc(g)
GiniCalc<-(2*aucOutput[1]) - 1
#full_data$predictedClass<- ifelse(prob > 0.5, 1, 0)

aucDF<-data.frame("Area Under Curve"=aucOutput[1])
giniDF<-data.frame("Gini Coefficient"=GiniCalc)
final = cbind(aucDF,giniDF)

# tryCatch({addWorksheet(wb, "ROC Curve", gridLines = FALSE) }, error=function(e){})
# writeData(wb, "ROC Curve", "Area Under Curve", startRow = 1,startCol = 1)
# writeDataTable(wb, "ROC Curve", aucDF, startRow = 2,startCol = 1, rowNames = FALSE, tableStyle = "TableStyleLight9")
# writeData(wb, "ROC Curve", "Gini Coefficient", startRow = 1,startCol = 4)
# writeDataTable(wb, "ROC Curve", giniDF, startRow = 2,startCol = 4, rowNames = FALSE, tableStyle = "TableStyleLight9")
# writeData(wb, "ROC Curve", "ROC Curve", startRow = 4,startCol = 1)

# ##saving plot
# png(plot_loc %+% "ROC_curve.png",1000,1000,res=100)
# par(mfrow=c(2,2)) # init 4 charts in 1 panel
# plot(g)
# dev.off()
# 
# insertImage(wb,"ROC Curve" ,plot_loc %+% "ROC_curve.png",startRow = 5, width = 16, height = 10,units = "cm")

###################################################################################################
# Output Results to Excel file placed at .../Output/Output Files
###################################################################################################
# 
# fileName <- paste0(ROOT %+% "/../../data/09_model_output/Output_Files/Output_" %+% format(Sys.time(),"%Y%m%d%H%M") %+% "ROC_curve"  %+% ".xlsx")
# #print("Building Output ...")
# saveWorkbook(wb, fileName, overwrite = TRUE)
# #print("Output Ready ...")
# 
###################################################################################################
# Output Results to JSON file placed at ../Statistical Test/docs
###################################################################################################

fileName <- paste0("output",".json")
fileNamePath = paste0(ROOT,"/output","/" ,fileName)

print("start writting JSON file...")
write_json(final, fileNamePath)
print("complete writing JSON file")

#### Saving Image
png(paste0(ROOT,"/output","/","ROC_curve.png"),1000,1000,res=100)
par(mfrow=c(2,2)) # init 4 charts in 1 panel
plot(g)
dev.off()

