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
#plot_loc <- ROOT %+% "/../../data/09_model_output/Graphs/"

# Get filename
params <- yaml.load_file(file.path(ROOT,"/../params.yaml"))
model_name <- paste(params$model_loading$model_name, '.RDS', sep='')

# Load model
Reg <- readRDS(file.path(ROOT,"../00_model_loading",model_name))

# Creating a new workbook for outputs or use an existing template
wb <- createWorkbook()

# Regression Summary
print("Running VIF ...")
VIF = vif(Reg)
final = data.frame(VIF)
final = cbind(Variable = rownames(final),final)
rownames(final) <- NULL # Brecht added

#tryCatch({addWorksheet(wb, "VIF Result", gridLines = FALSE, zoom = 80) }, error=function(e){})
#writeData(wb, "VIF Result", "VIF Result", startCol = 1, startRow = 1)
#writeDataTable(wb, "VIF Result", final, startRow = 2, startCol = 1, rowNames = FALSE, tableStyle = "TableStyleLight9")


###################################################################################################
# Output Results to Excel file placed at .../Output/Output Files
###################################################################################################

#fileName <- paste0(ROOT %+% "/../../data/09_model_output/Output_Files/Output_" %+% format(Sys.time(),"%Y%m%d%H%M") %+% "VIF_result"  %+% ".xlsx")
#print("Building Output ...")
#saveWorkbook(wb, fileName, overwrite = TRUE)
#print("Output Ready ...")


###################################################################################################
# Output Results to JSON file placed at ../Statistical Test/docs
###################################################################################################

fileName <- paste0("output",".json")
fileNamePath = paste0(ROOT,"/output","/" ,fileName)

print("start writting JSON file...")
write_json(final, fileNamePath)
print("complete writing JSON file")

