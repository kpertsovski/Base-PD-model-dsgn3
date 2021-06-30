# Normal Test

# Normal test is used to perform through-the cycle (TTC) assessment of model calibration. 
# It is a multi-period (minimum 5 years) test of correctness of a default probability 
# forecast for a single rating category.

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

#-------------------------------------------------#

#' Normal test
########################################################################
#'
#' The normal test is a multi-period test of correctness of a default
#' probability forecast for a single rating category.
#'
#' @param x a data frame with input data.
#' @param default.col a character string with the name of the column in \code{x}
#'   which contains the default status. This column should be a logical vector
#'   or be convertable to a logical vector (e.g. if 1 indicates a default and 0
#'   a non-default status)
#' @param estimated.pd.col a character string with the name of the column in
#'   \code{x} which contains the probability of default for each person or
#'   entity as estimated by the model.
#' @param rating.col a character string with the name of the column in \code{x}
#'   which contains the label for the rating class.
#' @param time.tag.col a character string with the name of the column in
#'   \code{x} which contains information on the time period for which the data
#'   holds. This column may be one of the \code{\link{DateTimeClasses}} or a
#'   factor.
#' @param time.tag.spec a conversion specification which is used to convert the
#'   column referenced by \code{time.tag.col} from a date or datetime object to
#'   a character vector. See \code{\link{strptime}} for more details on
#'   conversion specifications.
#' @param tbl.caption a character string which will be attached as a caption to
#'   the table with results.
#' @param ... additional arguments passed on to \code{\link{normalTest}}. At
#'   this point this is only \code{confidence}, a numeric value for the
#'   confidence level at which to perform the test.
#' @examples scores <- dataScorecard()
#' scores$year <- factor(rep_len(2019, nrow(scores))) # assume everything is from a single year
#' nt <- ot5 <- OT5(scores, "default", "estimated.pd", "rating", "year", confidence = 0.005)
#' @seealso This function wraps \code{\link{normalTest}}.
#' @return A \code{\link{taskResult}} object with a single table called
#'   \code{normal.test}. The table has column \code{rating} and the columns
#'   returned by \code{\link{normalTest}}.
#' @export
#' 
########################################################################


############################################################################################

OT5 <- function(x, default.col, estimated.pd.col, rating.col,
                time.tag.col, time.tag.spec = "%Y", tbl.caption = "Normal test", ...) {
  
  if (!is.data.frame(x)) { #check if x is a dataframe
    print ("not a dataframe")
    stop("cannot compute statistics for an object of class '",
         class(x)[1], "'")
  }
  
  if (!all(c(estimated.pd.col, default.col, rating.col) %in% names(x))) { #check if all the variables exists in the input data
    stop("selected variables do not exist in the input data: ",
         paste(c(estimated.pd.col,
                 default.col,
                 rating.col)[!c(estimated.pd.col,
                                default.col,
                                rating.col) %in% names(x)], collapse = ", "))
  }
  
  if (any(duplicated(c(estimated.pd.col, default.col, rating.col)))) { #if existing duplicates, stop
    stop("duplication in selected variables: ",
         paste(c(estimated.pd.col,
                 default.col,
                 rating.col)[duplicated(c(estimated.pd.col,
                                          default.col,
                                          rating.col))], collapse = ", "))
  }
  
  # convert the column with default status to a logical vector if it is not already:
  if (!is.logical(x[[default.col]])) {
    default.status <- try(as.logical(x[[default.col]]), silent = TRUE)
    
    if (inherits(default.status, "try-error")) {
      stop("cannot interpret column '", default.col, "' as a TRUE/FALSE column")
    } else {
      x[[default.col]] <- default.status
    }
  }
  
  # convert the column with dates and/or times to a factor if it is not already:
  
  x[[time.tag.col]] <-as.Date(x[[time.tag.col]], origin="1899-12-30")
  
  x[[time.tag.col]] <- as.Date(as.character(x[[time.tag.col]]), time.tag.spec) #convert numeric column into date format - Year
  
  if (inherits(x[[time.tag.col]], c("Date", "POSIXt"))) {
    # column refered to by 'time.tag.col' is a date or datetime object, convert
    # to a factor:
    time.tag <- try(format(x[[time.tag.col]], time.tag.spec), silent = TRUE)
    
    if (inherits(time.tag, "try-error")) {
      stop("cannot convert 'time.tag.col' from a datetime class to character using 'time.tag.spec'")
    } else {
      x[[time.tag.col]] <- as.factor(time.tag)
    }
  } else {
    # column is not a date or datetime object, therefore it must be a factor,
    # else an error is thrown:
    if (!is.factor(x[[time.tag.col]])) {
      stop("'time.tag.col' doesn't reference a column that is a DateTimeClass or a factor")
    }
  }
  
  # split the input data based on rating class:
  x.grouped <- split(x, x[[rating.col]])
  
  do.call(rbind, lapply(x.grouped, function(x) {
    res <- normalTest(default = x[[default.col]],
                      estimated.pd = x[[estimated.pd.col]],
                      time.tag = x[[time.tag.col]])#, ...)
    
    # add group label to result:
    res$rating <- x[[rating.col]][1]
    data.frame(res, stringsAsFactors = FALSE)
  })) -> normal.test
  
  #caption(normal.test) <- tbl.caption
  
  #taskResult(tables = list(normal.test = normal.test))
  list(normal.test = normal.test)
  
  #row.names(result) <- NULL
  
}
########################################################################

#' Calculate key statistics for the normal test
#'
#' @param default a logical vector with default observations (\code{TRUE} = a
#'   default event has occured)
#' @param estimated.pd a numeric vector with the estimated probability of
#'   default per person/entity
#' @param time.tag a factor which, for each person/entity, indicates for which
#'   time period the default observation and/or estimation is
#' @param confidence a (positive) numeric scalar value to indicate the
#'   confidence level at which to perform the test
#' @details The null hypothesis is that the true probabilities (i.e. observed
#'   probabilities of default) in the years \eqn{t=1, \ldots, T}{t=1,...,T} are
#'   no greater than the (mean of the) probabilities of default estimated by the
#'   model. In mathematical terms this is denoted as
#'
#'   \deqn{\frac{\sum_{t=1}^T (d_t - PD_t)}{\sqrt{T \cdot \tau^2}} > z_\alpha}{%
#'   sum_{t=1,...,T} (dt - PDt)/sqrt(T * tau^2)}
#'
#'   where \eqn{d_t}{dt} is the observed probability of default in time period
#'   \eqn{t}, \eqn{PD_t}{PDt} is the (mean) estimated probability of default in
#'   period \eqn{t}, and \eqn{\tau^2}{tau^2} is calculated using
#'
#'   \deqn{\tau^2 = \frac{1}{1 - T} \biggl( \sum_{t=1}^T (d_t - PD_t)^2 - %
#'   \frac{1}{T} \bigl( \sum_{t=1}^T (d_t - PD_t) \bigr)^2 \biggr)}{1/(1 - T) %
#'   * (sum_{t=1,...,T} (dt - PDt)^2 - (1/T)*(sum_{t=1,...,T} (dt - PDt))^2 )}
#'
#' @importFrom stats aggregate pnorm
#' @export
########################################################################

#Changing the confidence to 0.10 (earlier it was 0.01)

normalTest <- function(default, estimated.pd, time.tag, confidence = 0.001) {
  stopifnot(is.logical(default))
  stopifnot(is.numeric(estimated.pd))
  stopifnot(is.factor(time.tag))
  stopifnot(length(default) == length(estimated.pd))
  stopifnot(is.numeric(confidence) && confidence > 0)
  
  # determine indices per (time.tag) group:
  group.indices <- split(seq_along(time.tag), time.tag)
  # number of groups:
  n <- length(group.indices)
  
  # calculate various group statistics:
  do.call(rbind, lapply(group.indices, function(group) {
    n.tot <- length(group)
    n.def <- sum(default[group])
    
    data.frame(
      n.tot = n.tot,
      n.def = n.def,
      pd.obs = n.def/n.tot,
      pd.model = mean(estimated.pd[group]),
      stringsAsFactors = FALSE
    )
  })) -> group.stats
  
  sum.diff <- sum(group.stats$pd.obs - group.stats$pd.model)
  sum.squared.diff <- sum((group.stats$pd.obs - group.stats$pd.model)^2)
  
  tau.squared <- (sum.squared.diff - sum.diff^2/n)/(n - 1)
  
  z <- sum(group.stats$pd.obs - group.stats$pd.model)/sqrt(n*tau.squared)
  #print (z)
  p.value <- 1 - pnorm(abs(z))
  #print (p.value)
  list(
    n.tags = n,
    p.value = p.value,
    result = ifelse(p.value < confidence,
                    "To be investigated",
                    "Acceptable")
  )
}

# Specifying file paths

ROOT <- getCurrentFileLocation()
data_path = file.path(ROOT,"../../../data/interim")
#plot_loc <- ROOT %+% "/../../data/09_model_output/Graphs/"


# Get filename
params <- yaml.load_file(file.path(ROOT,"/../params.yaml"))
model_name <- paste(params$model_loading$model_name, '.RDS', sep='')
dpVar <- params$model_loading$bad_flag
rating_class = params$`Normal-test`$rating_class


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

# Read rating class
print("****")
print(ROOT)
print("****")

rating_class_FileName <- paste0(ROOT,"../data/raw/",rating_class)
rating_class <- read.csv(rating_class_FileName)

# Load model
print("****")
print(ROOT)
print("****")
Reg <- readRDS(file.path(ROOT,"../00_model_loading",model_name))

# Creating a new workbook for outputs or use an existing template
#wb <- createWorkbook()

print("Running Normal test ...")
prob=predict(Reg,full_data,type=c("response"))
full_data$prob=prob

# Assign Rating Class to PD
full_data$rating_class = cut(full_data$prob,breaks = c(0,rating_class$PD), labels = rating_class$Rating)

full_data = full_data[,c("masterloanidtrepp","observation_date","rating_class",dpVar,"prob")]

#Calculate output
output <- OT5(full_data,default.col = dpVar, estimated.pd.col = "prob", rating.col = "rating_class",
              time.tag.col = "observation_date", time.tag.spec = "%Y", tbl.caption = "Normal test")

output = as.data.frame(output)

# Adding Default Rate
default_rate_df = as.data.frame(table(full_data$bad_flag_final_v3,full_data$rating_class))
default_rate_df = dcast(default_rate_df,Var2~Var1,value.var="Freq", fun.aggregate=sum)
names(default_rate_df) = c("rating_class","good","bad")
default_rate_df$default.rate = default_rate_df$bad/(default_rate_df$bad + default_rate_df$good)

# Adding Rating Class upper limits
final = merge(output,default_rate_df[,c("rating_class","default.rate")],by.x ="normal.test.rating",by.y ="rating_class" ,all.x = TRUE)
final$normal.test.n.tags= NULL
final = merge(final,rating_class,by.x = "normal.test.rating",by.y = "Rating",all.x = TRUE)

final <- final %>% rename(rating.class = normal.test.rating,
                          predicted.PD.upper.boundary = PD,
                          "normal.test.p-value" = normal.test.p.value)

final = final[,c("rating.class","predicted.PD.upper.boundary","default.rate","normal.test.p-value","normal.test.result")]
final$rating.class = as.numeric(final$rating.class)

#Formatting numbers
final$predicted.PD.upper.boundary = paste(round(100* final$predicted.PD.upper.boundary,2),"%",sep="")
final$default.rate = paste(round(100* final$default.rate,2),"%",sep="")
final = final[order(final$rating.class),]

#tryCatch({addWorksheet(wb, "Normal test", gridLines = FALSE) }, error=function(e){})
#writeData(wb, "Normal test", "Normal test", startRow = 1,startCol = 1)
#writeDataTable(wb, "Normal test", final, startRow = 2,startCol = 1, rowNames = FALSE, tableStyle = "TableStyleLight9")

# Output Results to Excel file placed at .../Output/Output Files
###################################################################################################

#fileName <- paste0(ROOT %+% "/../../data/09_model_output/Output_Files/Output_" %+% format(Sys.time(),"%Y%m%d%H%M") %+% "Normal_test"  %+% ".xlsx")
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
