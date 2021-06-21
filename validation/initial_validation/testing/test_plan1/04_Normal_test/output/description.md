- - - 
<h2>5.2.4 Normal Test</h2>
The aim of the test is to evaluate the adequacy of observed default rates comparing to predicted PD. The test is performed on the level of rating grade. It is applied under the assumption that the mean default rate does not vary too much over time and that default events in different years are independent. The normal test is motivated by the Central Limit Theorem and is based on a normal approximation of the distribution of the time-averaged default rates.
With high enough (>30) number (n) of observations which are independent, Point in Time (PIT) observed default rate (ODR) is expected to be normally distributed. The algorithm of the test is to calculate time-weighted (or simple arithmetic) average of all PiT ODRs, calculate standard error of this statistic and derive confidence interval for it. 

The test returns a table of p values and a brief interpretation of the test result for each rating grade.
