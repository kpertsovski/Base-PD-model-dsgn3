a) 'data' 
Contains data (raw, interim, and processed) that is required for model generation and perform the requisite tests.

b) 'code'
Contains code for data processing, model creation that are required by validation team to replicate the model.
dvc.yaml is used to design model code flow and establish the modular structure of the given model. Inclusion of additional script/step in model development would require incorporating those changes in the dvc.yaml file.

c) 'testing'
Subfolders are created for test plans that are to be carried out by model validator to assess model performance and evaluate key model statistics. Each test plan could be a collection of number of independent tests.Independent folders are created for tests that are to be carried out by model validator to assess model performance and evaluate key model statistics.
dvc.yaml is used to create testing code flow and establish the modular structure of the selected test plans.Subsequent addition of new tests would require creating folder for the respective test and incorporating the same in modular design established in the dvc.yaml file.


d)'documentation'
Final Validation documentaiton files are present at this location. Final documentation is created using docs.config.yaml.  
The requisite test results and images are extracted from 'code' folder and 'testing'