# NoProb (<ins>No</ins>n-<ins>pro</ins>ductive <ins>b</ins>inding fit)
**NoProb** is used to fit **raw QCM-D data** for kinetic parameters. This directory contains example files (.cvs, .png files) as well as the script.

1. Download and keep all .cvs and .py files in a same folder.

  - data.cvs = raw data, frequency overtone versus time. 

  - NoProb_parameters.csv = initial fitting and optimization limits.

2. Run **NoProb.py** in Python. Confirm the initial parameters by typing "y".

3. When the program finishes running, it will display the optimized parameters and a graph (graph.png) showing the raw data, the inital curve and the optimized curve, together with error in the inital model and error in the optimized model. 

    It will creates two output files: fitted_NoProb_parameters.csv and dtVsLoss.csv. 


*We'd like thank Daniel Kats for the help with the script.*
