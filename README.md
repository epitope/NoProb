# NoProb (<ins>No</ins>n-<ins>pro</ins>ductive <ins>b</ins>inding fit)
**NoProb** is used to fit **raw QCM-D data** for kinetic parameters. This directory contains example files (.cvs, .png files) as well as the script.

1. Download and keep all .cvs and .py files in a same folder.

  - data.cvs = example raw data, frequency overtone versus time (replace data in this file with your QCM-D data). 

  - NoProb_parameters.csv = initial fitting and optimization limits.

2. Run **NoProb.py** in Python. Confirm the initial parameters by typing "y".

3. When the program finishes running:
  - It will display the optimized parameters and a graph (graph.png) showing the raw data, the inital curve and the optimized curve, together with error in the initial model and error in the optimized model. 
  
  - It will creates two output files: fitted_NoProb_parameters.csv and dtVsLoss.csv. 

**Note:**
#### Run in an Python environment with the following required libraries:

*from* __future__ *import* **print_function**

*from* **matplotlib** *import* **pyplot** *as* **plt**

*import* **csv**

*import* **math**

*import* **numpy** *as* **np**

*import* **random**

*import* **sys**

*import* **scipy.optimize**

*import* **warnings**


*We'd like thank Daniel Kats for the help with the script.*
