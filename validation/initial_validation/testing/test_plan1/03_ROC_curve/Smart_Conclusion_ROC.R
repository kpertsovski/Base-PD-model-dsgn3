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
# Smart Documentation - 1. Import thresholds from params.yaml, 2. Import results from output.json
#                       3. Compare the result with threshold and choose the suitable conclusion, and 
#                       4. Export the text conclusion for results.md                       
###################################################################################################                   

#1. Get thresholds
thresholds_params <- yaml.load_file(file.path(ROOT,"/../params.yaml"))
AUROC_threshold <- thresholds_params$model_testing$AUROC$Threshold
Gini_threshold <- thresholds_params$model_testing$Gini$Threshold

#2. Import results from output.json
json_object <- paste0(ROOT,"/output/output.json")
results <- rjson::fromJSON(file = json_object)
AUROC_result <- results[[1]]$Area.Under.Curve
Gini_result <- results[[1]]$Gini.Coefficient

#3. Compare results with the threshold

if(AUROC_result > AUROC_threshold & Gini_result > Gini_threshold) {
  conclusion = paste0("As shown in the above table, the AUC value is higher than ",AUROC_threshold, " and the Gini value of the model is higher than ", Gini_threshold, ", indicating that discriminatory power of the model is good.")
} else if(AUROC_result < AUROC_threshold & Gini_result > Gini_threshold) {
  conclusion = paste0("As shown in the above table, the AUC value is less than ",AUROC_threshold, " and the Gini value of the model is higher than ", Gini_threshold, ", indicating that discriminatory power of the model is not sufficient")
} else if(AUROC_result > AUROC_threshold & Gini_result < Gini_threshold) {
  conclusion = paste0("As shown in the above table, the AUC value is higher than ",AUROC_threshold, " and the Gini value of the model is lower than ", Gini_threshold, ", indicating that discriminatory power of the model is not sufficient")
} else {
  conclusion = paste0("As shown in the above table, the AUC value is less than ",AUROC_threshold, " and the Gini value of the model is less than ", Gini_threshold, ", indicating that discriminatory power of the model is not sufficient")
}


#4. Export the conclusion
conclusionName = paste0("conclusion",".md")
conclusionNamePath = paste0(ROOT,"/output/",conclusionName)
markdown::renderMarkdown(text = conclusion, output = conclusionNamePath)
