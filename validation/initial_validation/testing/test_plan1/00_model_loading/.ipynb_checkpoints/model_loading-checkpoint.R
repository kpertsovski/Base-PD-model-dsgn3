# Packages
#install.packages('reticulate', repos="http://cran.r-project.org")
library(reticulate)
library(yaml)

# Get root directory
root <- getwd()

# Get filename
params <- yaml.load_file(file.path(root,"params.yaml"))
model_name <- paste(params$model_loading$model_name, '.csv', sep='')
bad_flag <- params$model_loading$bad_flag

# Load logistic regression model parameters and coefficients in CSV file
logit_model_dev <- read.csv(file.path(dirname(root),"../data/processed",model_name), stringsAsFactors=FALSE, check.names=FALSE)

X_train <- read.csv(file.path(dirname(root),"../data/interim","X_test_transformed.csv"), stringsAsFactors=FALSE, check.names=FALSE)

if ('const' %in% logit_model_dev[,c('Parameter')]) {
    print('Model with intercept')
    formula <- as.formula(paste(bad_flag, paste(logit_model_dev[,c('Parameter')][2:length(logit_model_dev[,c('Parameter')])], collapse=' + '), sep=' ~ '))
} else {
    print('Model without intercept')
    formula <- as.formula(paste(bad_flag, paste(logit_model_dev[,c('Parameter')], collapse=' + '), sep=' ~ '))
}

# Reconstruct model development in Python to use in R
logit_model <- glm(formula, data=X_train, family='binomial')
print(summary(logit_model))
logit_model$coefficients <- logit_model_dev[,c('Coef.')]
names(logit_model$coefficients) <- logit_model_dev[,c('Parameter')]
print(summary(logit_model))

saveRDS(logit_model, file.path(root,"00_model_loading",gsub(pattern="\\.csv$", ".RDS", model_name)))

