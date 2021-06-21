i) 'data' 
Contains data (raw, interim, and processed) that is required for model development and perform the requisite tests.

ii) 'code'
Contains scripts to create model object- including data preprocessing, feature engineering, train model. 
dvc.yaml is used to design model code flow and establish the modular structure of the given model. Inclusion of additional script/step in model development would require incorporating those changes in the dvc.yaml file.


iii) 'testing'
Independent folders are created for tests that are to be carried out by model developer to assess model performance and evaluate key model statistics.
dvc.yaml is used to create testing code flow and establish the modular structure of the selected test plan. User can pick relevant tests from test repository and drop the same in an independent subfolder in the respective test plans. Subsequent addition of new tests would require creating folder for the respective test and incorporating the same in modular design established in the dvc.yaml file.
 

iv)'documentation'
Model documentaiton files are present at this location. Final documentation is created using docs.config.yaml.  
The requisite test results and images are extracted from 'code/model_pipeline' folder and 'testing' 