- - -
<h2>5.1.4 Receiver Operating Characteristic curve</h2>
Receiver Operating Characteristic (ROC) is a curve in a unit square which is used to assess the accuracy of the diagnostic (e.g. rating) system. The area under curve (AUC) is the area under the ROC curve. Higher AUC means higher discriminatory power of model. 




| Area under curve | Gini coefficient |
| ---------------- | ---------------- |
| 0.7743           | 0.5487           |


<center>
    <p><img src="../03_testing/03_ROC_curve/docs/ROC_curve.png" alt="ROC curve image" width="700" crossorigin="anonymous"></p>
    </center>

As shown in the above table, the AUC value is higher than 0.7 and correspondingly the Gini value of the model is higher than 0.4, indicating that discriminatory power of the model is satisfactory. 


- - - 
<h2>5.1.5 KS statistic</h2>
The KS statistic is used to measure the discriminatory power of the PD model. It is defined as the maximum difference between the cumulative percentage of good samples (i.e., non-defaulters) and the cumulative percentage of bad samples (i.e., defaulters). A higher KS value implies a good fit of the model.

The test returns a KS value.


| Ks statistic train | Ks statistic test |
| ------------------ | ----------------- |
| 0.4219             | 0.3811            |


As shown in the above table, the KS value is higher than 0.4, indicating that discriminatory power of the model is good.

