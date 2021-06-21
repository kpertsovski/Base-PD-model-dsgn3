<center>

<img src="../04_documentation/docs/generic_bank_logo.png" alt="generic_bank_logo" width="100" crossorigin="anonymous">

<h1>"Bank Name"</h1>

<h2>MODEL DEVELOPMENT GROUP <br>

Model Development Report

CRE loan balances - Probability of Default Model
(Model ID 894 Version 3.2)
</h2>
</center>

<center>
<table cellpadding="5">
<tr>
<td>
Prepared by: 
</td>
<td>
<p>First Name, Last Name</p>
<p>Title, Model Development (MD)</p>
</td>
<tr>
<td>
Reviewed by:
</td>
<td>
<p>First Name, Last Name</p>
<p>Title, Model Development (MD)</p>
</td>
</tr>
</table>
</center>

<h3>Identification</h3>
<table cellpadding="5" border="1">
<tr bgcolor=green>
<td>
ID
</td>
<td>
Model Version Number
</td>
<td>
Model
</td>
<td>
File Name
</td>
</tr>

<td>
894
</td>
<td>
3.2
</td>
<td>
CRE loan balances - Probability of Default model
</td>
<td>
Model Development
</td>
</tr>
</table>

<hr>

<div id="toc_container">
<h2><p class="toc_title">Table of Contents</p></h2>
<ul class="toc_list">
  <li><a>1 EXECUTIVE SUMMARY</a></li>
  <li><a>2 INTRODUCTION</a>
    <ul>
      <li><a>2.1 Model source</a></li>
      <li><a>2.2 Model composition</a></li>
      <li><a>2.3 Model version</a></li>
      <li><a>2.4 Model usage and product definition</a></li>
    </ul>
  </li>
  <li><a>3 MODEL DESCRIPTION</a>
    <ul>
      <li><a>3.1 Model overview</a></li>
      <li><a>3.2 Theoretical background</a></li>
      <li><a>3.3 Significant assumptions and limitations</a></li>
      <li><a>3.4 Model input</a></li>
      <li><a>3.5 Model output</a></li>
    </ul>
  </li>
  <li><a>4 MODEL METHODOLOGY</a>
    <ul>
      <li><a>4.1 Literature review</a></li>
      <li><a>4.2 Conceptual soundness</a></li>
        <ul>
          <li><a>4.2.1 Model Framework and Calculation Method</a></li>
          <li><a>4.2.2 Alternate Methodologies</a></li>
          <li><a>4.2.3 Model Segmentation</a></li>
          <li><a>4.2.4 Model Driver/Variable Selection</a></li>
        </ul>
      <li><a>4.3 Assesment of input data</a></li>
      <li><a>4.4 Bias and fairness</a></li>
      <li><a>4.5 Performance monitoring approach</a></li>
    </ul>
  </li>
  <li><a>5 MODEL PERFORMANCE</a>
    <ul>
      <li><a>5.1 Performance testing</a></li>
        <ul>
          <li><a>5.1.1 Data quality</a></li>
          <li><a>5.1.2 Information value</a></li>
          <li><a>5.1.3 Model coefficient</a></li>
          <li><a>5.1.4 Receiver Operating Characteristic curve</a></li> 
          <li><a>5.1.5 KS statistic</a></li> 
        </ul>
      <li><a>5.2 Conclusions and recommendations</a></li>
      <li><a>5.3 Model limitations</a></li>
    </ul>
  </li>
  <li><a>6 REFERENCES</a>
  <li><a>7 APPENDIX</a>
    <ul>
      <li><a>7.1 Final MDR</a></li>
      <li><a>7.2 Other MD materials</a></li>
    </ul>
  <li><a>8 ASSESSMENT OF REGULATORY REQUIREMENTS</a>
  <li><a>9 ISSUE LOG</a>
</ul>
</div>

<hr>
<h2>5. Model Performance</h2>

Model developers have built v3.2 of the CRE loan balances PD model. The model is developed using logistic regression technique with 7 independent variables. Data was sourced from TREPP and was split into training and testing data by random sampling approach. The development of the model is in Python.

In the current development exercise, model developers have performed the following activities for the selected varibles:
Performance testing of the PD model - information value of risk drivers, calculation of model coefficients, data quality checks and Gini.

The definations of the selected variables are listed below:
<li><a>priorfydscr:Preceding Fiscal Year DSCR (NOI). A ratio of net operating income (NOI) to debt service for the most recent fiscal year end statement available as reported by the servicer.</a></li>
<li><a>mrfytdocc: Most Recent Occupancy Rate. The most recent available percentage of rentable space occupied. Should be derived from a rent roll or other document indicating occupancy consistent with most recent documentation.</a></li>
<li><a>debt_yield_p1: Debt yield of preceding financial year.</a></li>
<li><a>priorfyocc:Preceding Fiscal Year Occupancy Rate. A percentage of rentable space occupied as of the most recent fiscal year end operating statement available. Should be derived from a rent roll or other document indicating occupancy, and in most cases should be within 45 days of the most recent fiscal year end financial statement.</a></li>
<li><a>OLTV:LTV at the time of origination.</a></li>
<li><a>Division: Division created from the states of US.</a></li>
<li><a>interestonly:Interest Only (Y/P/N). If loan is interest only for life, then Y; if loan has more than one interest only period but is not fully interest only then P; else N.</a></li>

The details of the above are provided in the sections below.
