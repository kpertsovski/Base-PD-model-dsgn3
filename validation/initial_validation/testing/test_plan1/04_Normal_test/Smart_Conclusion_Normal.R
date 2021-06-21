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
Normal_threshold <- thresholds_params$model_testing$Normal_test$Threshold

#2. Import results from output.json
json_object <- paste0(ROOT,"/output/output.json")
results <- rjson::fromJSON(file = json_object)
Normal_result = c()
for(i in 1:length(results)){Normal_result = c(Normal_result, as.numeric(results[[i]]$`normal.test.p-value`))}

#3. Compare results with the threshold

if (all(Normal_result > Normal_threshold)) {
  conclusion = paste0("As shown in the above table, the p-value of Normal test for all segments is higher than ",Normal_threshold, ", which means the null hypothesis cannot be rejected and there is evidence that the predicted PD does not deviate from the long run average of observed values. Therefore, the accuracy of the model is adequate.")
} else{
  conclusion = paste0("As shown in the above table, the p-value of Normal test for some segments is lower than ",Normal_threshold, ", which means the null hypothesis is rejected and there is evidence that the predicted PD does deviate from the long run average of observed values. Therefore, the accuracy of the model is not adequate.")
}


#4. Export the conclusion
conclusionName = paste0("conclusion",".md")
conclusionNamePath = paste0(ROOT,"/output/",conclusionName)
markdown::renderMarkdown(text = conclusion, output = conclusionNamePath)
