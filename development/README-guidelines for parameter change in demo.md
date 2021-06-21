Parameters are changed using params.yaml at below location 
'development/code/model_pipeline'

Below parameters are used in the PD model. The respective range for the parameteres is mentioned alongside.

1)size_cutoff: length of dataset used in development. This essentially creates a subset of raw data that is further used in model development.
Range:   should be subset of data size (1,734,473) 

2)Sampling: Split data into training datasets and test datasets
  test_size: 0.2
  Range:   .05 to .40

3)Variable selection: Select variables used in model development
  
  *numerical_columns_as_features: 
  - 'priorfydscr'
  - 'mrfytdocc'
  - 'debt_yield_p1'
  - 'priorfyocc'
  *categorical_columns_as_features:
  - 'Division'
  - 'interestonly'
  
  *model_with_intercept: 'yes' or 'no'
  Def: The intercept (often labeled the constant) is the expected mean value of Y when all X=0. Start with a regression equation with one   predictor, X. If X sometimes equals 0, the intercept is simply the expected mean value of Y at that value. ... It's the mean value of Y at the chosen value of X.


key changes to notice as a result of change in any of the above parameter:
1. DVC metrices: gini_train, gini_test, KS_statistic_train and KS_statistic_test
2. Change in Information values and model coefficients (in Model Documentation)
3. ROC curve and KS statistic test results (in Model Documentation)
