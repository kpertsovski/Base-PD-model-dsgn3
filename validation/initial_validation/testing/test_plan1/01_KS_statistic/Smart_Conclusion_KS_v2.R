# Supress Warnings in Prod
options(warn=-1)

########################################################################################################################
#' Installation of required packages - This part loads/ Installs packages that are required to perform model diagnostics
########################################################################################################################

full.list.of.packages <- c("dplyr","openxlsx","readr","bizdays","jrvFinance","xts","reshape2","ggplot2","moments","car","pROC","markdown","rjson")

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
suppressPackageStartupMessages(library(markdown))
suppressPackageStartupMessages(library(rjson))

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

###################################################################################################
# Smart Documentation - 0. Get test name
#                       1. Import thresholds from params.yaml, 2. Import results from output.json
#                       3. Compare the result with threshold and choose the suitable conclusion, and 
#                       4. Export the text conclusion for results.md                       
###################################################################################################                   
#0. Get test name
thresholds_params <- yaml.load_file(file.path(ROOT,"/../performance_testing.yaml"))
test_name <- thresholds_params$model_testing$Test_name
  
#1. Get thresholds

threshold <- thresholds_params$model_testing$Threshold

#2. Import results from output.json
json_object <- paste0(ROOT,"/output/output.json")
results <- rjson::fromJSON(file = json_object)
output_train = results$KS_statistic_train
output_test = results$KS_statistic_test

#3. Compare the threshold to results from 
##Train
if (output_train >= threshold) {
  train_conclusion = paste0("For training sample, the ",test_name, " is ", output_train, ", which satisfies the acceptance criteria of ",threshold, 
                            ", indicating that the model is performing well.")
} else{
  train_conclusion = paste0("For training sample, the ",test_name, " is ", output_train, ", which breaches the acceptance criteria of ",threshold, 
                            ", indicating that the model performance is not sufficient.")
}

##Test
if (output_test >= threshold) {
  test_conclusion = paste0("For testing sample, the ",test_name, " is ", output_test, ", which satisfies the acceptance criteria of ",threshold, 
                           ", indicating that the model is performing well.")
} else{
  test_conclusion = paste0("For testing sample, the ",test_name, " is ", output_test, ", which breaches the acceptance criteria of ",threshold, 
                           ", indicating that the model performance is not sufficient.")
}

#4. Export the conclusion
KS_conclusion = paste(train_conclusion, test_conclusion, collapse = '\n')
conclusionName = paste0("conclusion",".md")
conclusionNamePath = paste0(ROOT,"/output/",conclusionName)
markdown::renderMarkdown(text = KS_conclusion, output = conclusionNamePath)
