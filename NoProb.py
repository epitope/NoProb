# Run in an Python environment with the following required libraries

from __future__ import print_function
from matplotlib import pyplot as plt
import csv
import math
import numpy as np
import random
import sys
import scipy.optimize
import warnings


# Parameters to be tuned with the gradient decent method
TUNED_PARAMS = ["k1", "n0", "n1", "n2"]
# Function will  find dt, a value between dt_min and dt_max - set by the user. 
# Graph_cutoffs define the domain that the autogenerated python graph will fall in.
# Optimization_cutoffs define the domain of empirical data that the tuned parameters are being fit to
USER_DEFINED_PARAMS = set(["dt_min", "dt_max","c3", "r", "graph_left_cutoff", "graph_right_cutoff", "optimization_left_cutoff", "optimization_right_cutoff"])
# Input file must be in the active directory
# Format of this .csv file should be 1 column with each row being a string:
# "parameter_name= 'float'" - minus the "" and ''. 
INPUT_FILE = "NoProb_parameters.csv"
# Output file is autogenerated. If a file with this name already exists, it will be overwritten.
OUTPUT_FILE = "fitted_NoProb_parameters.csv"
# This is the raw data file. It should have 2 columns where every row is a time, frequency datapoint.
DATA_FILE = "data.csv"
MAX_ITER = 5000

"""
These are the methods specific to the function being optimized
"""

################################################################################################
	
def get_saturation_gradient (t, parameters, aux_parameters):
	"""Saturation gradient is a vector in the following order:
		* df_dK1
		* df_dN0
		* df_dN1
		* df_dN2
		
	"""
	K1 = parameters[0]
	N0 = parameters[1]
	N1 = parameters[2]
	N2 = parameters[3]
	dt = aux_parameters["dt"]
	T = N0 / K1
	C3 = aux_parameters["c3"]
	Cvert = aux_parameters["cvert"]
	r = aux_parameters["r"]

	df_dk1 = (-1/(C3*np.exp(r*(dt-t))))*((((dt-t)*np.exp((-K1*(dt-t))/(N1)))/(K1*N1)) - (1-np.exp((-K1*(dt-t))/(N1)))/K1**2)
	df_dN0 = -(dt-t)*np.exp((K1*(dt-t))/(N0))/((N0**2)*(C3*np.exp(r*(dt-t))+1))
	df_dN1 = (t-dt)/((N1**2)*(C3*np.exp(r*(dt-t))+1))
	df_dN2 = (dt-t)/(N2**2)

	return np.array([df_dk1, df_dN0, df_dN1, df_dN2])
	
def mod_maxwell(time, parameters, aux_parameters):

	K1 = parameters[0]
	N0 = parameters[1]
	N1 = parameters[2]
	N2 = parameters[3]
	dt = aux_parameters["dt"]
	T = N0 / K1  # very large, when K1 very small; and this is a positive #
	C3 = aux_parameters["c3"]
	Cvert = aux_parameters["cvert"]
	r = aux_parameters["r"]
	adjusted_t = time - dt


	return -1 * ((1/K1) * (1 - np.exp(-1 * (adjusted_t) / T)) + (adjusted_t)/N1)
	
def s_curve (time, parameters, aux_parameters):

	dt = aux_parameters["dt"]
	C3 = aux_parameters["c3"]
	Cvert = aux_parameters["cvert"]
	r = aux_parameters["r"]
	
	return 1/(1+C3*np.exp((-time + dt)*r))
	
def steady(time, parameters, aux_parameters):
	N2 = parameters[3]
	dt = aux_parameters["dt"]
	C3 = aux_parameters["c3"]
	Cvert = aux_parameters["cvert"]
	r = aux_parameters["r"]
	
	return (time-dt)/N2 + Cvert
	
def saturation_function(time, parameters, aux_parameters):
	"""Parameters is a vector in the following order:
		* K1
		* N0
		* N1
		* N2
		* dt
		* C3 
		* Cvert
		* r
		
	"""
	
	return mod_maxwell(time, parameters, aux_parameters) * s_curve(time, parameters, aux_parameters) + steady(time, parameters, aux_parameters)

##################################################################

def get_obj_function(X, Y, aux_parameters):
	"""Return the function which must be minimized."""

	return lambda parameters: np.sum((Y - saturation_function(X, list(parameters), aux_parameters))** 2)

def get_gradient_function(X, Y, aux_parameters):
	"""Return the function which evaluates gradient."""

	return lambda parameters: get_gradient(X, Y, parameters, aux_parameters)


"""
Function-agnostic methods.
This is the meat of the program
"""

def get_gradient(X, Y, parameters, aux_parameters):
	"""Return gradient over all parameters.
	Will return 0 for all parameters other than first 5, because not optimizing those."""

	obj_grad = np.zeros(len(parameters), dtype=np.float64)

	# compute gradients for all data points
	grad = get_saturation_gradient(X, parameters, aux_parameters)

	for i in range(len(obj_grad)):
		obj_grad[i] = np.sum(-2 * Y * grad[i] + 2 * saturation_function(X, parameters, aux_parameters) * grad[i])

	return obj_grad

def get_loss(X, Y, parameters, aux_parameters):
	"""Return float that gives loss of function being optimized compared to ideal scenario.
	"""

	return np.sum((Y - saturation_function(X, parameters, aux_parameters)) ** 2)

	
def read_parameters_from_file():
	"""Read user-defined parameters from a file."""

	parameters = np.zeros(len(TUNED_PARAMS)) * 1.0
	d = {}

	with open(INPUT_FILE, "rb") as fp:
		for line in fp:
			if line.startswith("#") or len(line.strip()) == 0:
				continue
			row = [item.strip() for item in line.split("=")]
			if row[0].lower().strip() in TUNED_PARAMS:
				i = TUNED_PARAMS.index(row[0].strip().lower())
				parameters[i] = np.float64(row[1].strip())
			elif row[0].lower().strip() in USER_DEFINED_PARAMS:
				d[row[0].lower().strip()] = np.float64(row[1].strip())
			else:
				print("[ERROR] Read invalid item %s" % row[0])
				sys.exit(1)

	missing_keys = USER_DEFINED_PARAMS.difference(set(d.keys()))
	if len(missing_keys) > 0:
		print("[ERROR] User must specify the following keys:")
		print(", ".join( missing_keys))
		sys.exit(1)
				
	# show parameters for tuning
	for i in range(len(TUNED_PARAMS)):
		print("%s = %s" % (TUNED_PARAMS[i], str(parameters[i])))

	# show user-defined fixed parameters
	for k in sorted(d.keys()):
		v = d[k]
		print("%s = %s" % (k, str(v)))
		
	# get confirmation
	user_in = "x"
	
	while user_in not in ["y", "n"]:
		user_in = raw_input("This is OK? [y/n] ")
		
	if user_in == "y":
		return parameters, d
	else:
		sys.exit(1)

def set_parameters():
	return read_parameters_from_file()
	
def scipy_optimize(X, Y, aux_parameters, parameters):

            
       	obj_fn = get_obj_function(X, Y, aux_parameters)
       	grad_obj_fn = get_gradient_function(X, Y, aux_parameters)
       	new_params = scipy.optimize.fmin_bfgs(obj_fn, parameters, fprime=grad_obj_fn, maxiter=MAX_ITER)
        
        
       	new_fn = lambda p: (Y - saturation_function (X, p, aux_parameters))
       	optimized_params = scipy.optimize.leastsq (new_fn, new_params)[0]
       	loss = get_loss(X, Y, optimized_params, aux_parameters)
       	
   	return optimized_params, loss
	
def load_data():
	"""Return time, f5 as np.array tuple."""

	time = []
	f5 = []
	header = True

	with open(DATA_FILE, "rb") as fp:
		reader = csv.reader(fp, delimiter=",")
		for row in reader:
			if header:
				header = False
			else:
				t = np.float64(row[0])
				time.append(t)
				f5.append(np.float64(row[1]))

	return (np.array(time), np.array(f5))

def show_data(X, Y, parameter_guess, optimized_params, aux_parameters):
	"""Show pretty plot of F5 vs. Time to make sure data imported correctly."""
	
	guess_fitted = saturation_function(X, parameter_guess, aux_params)
	optimized_fitted = saturation_function(X, optimized_params, aux_params)

	plt.plot(X, Y, 'bo', X, guess_fitted, 'r+', X, optimized_fitted, 'r-')
	plt.show()

	
def trim_data (X, Y, left_cutoff, right_cutoff):
	new_Y = Y[np.where(X >= left_cutoff)]
	new_X = X[np.where(X >= left_cutoff)]
	
	new_Y = new_Y[np.where(new_X <= right_cutoff)]
	new_X = new_X[np.where(new_X <= right_cutoff)]
	return new_X, new_Y

def getAsymtote_Y(parameters, aux_parameters):
        dt = aux_parameters['dt']
        ddB_dt = abs((saturation_function(dt, parameters, aux_parameters) - saturation_function((dt-1), parameters, aux_parameters)) - (saturation_function((dt+1), parameters, aux_parameters) - saturation_function(dt, parameters, aux_parameters)))
        #use dt as the guess interval 
        #i==0 would be left of the function which starts at optimization_left_cutoff (parameters[8]) so skipped
        for i in range(1, 100): 
            dB_asym_guess_1 = saturation_function((dt*i), parameters, aux_parameters) - saturation_function((dt*i-1), parameters, aux_parameters)
            dB_asym_guess_2 = saturation_function((dt*i+1), parameters, aux_parameters) - saturation_function(dt*i, parameters, aux_parameters)
            ddB_asym_guess = dB_asym_guess_1 - dB_asym_guess_2
            print(ddB_dt*0.01, ddB_asym_guess, i)
            if ddB_dt*0.01 > abs(ddB_asym_guess): 
                print(ddB_dt*0.01, ddB_asym_guess, i)
                if (dB_asym_guess_2 < 0):
                    print("regular RT", ddB_asym_guess)
                    return saturation_function (dt*i, parameters, aux_parameters)
                else:
                    print("inverse RT")
                    #return the inverse
                    return saturation_function (dt*i, parameters, aux_parameters) - dt*i*dB_asym_guess_2
            else:
                continue
        print("Could not find asymtote for Rt")
        sys.exit(1)

if __name__ == "__main__":
	# load data from file
	raw_X, raw_Y = load_data()
	# load user-defined parameters from file
	parameter_guess, aux_params = set_parameters()

	# simply remove the data which should not be optimized for
	# make sure that Y is also trimmed
	optimization_X, optimization_Y = trim_data(raw_X, raw_Y, aux_params["optimization_left_cutoff"], aux_params["optimization_right_cutoff"])
	display_X, display_Y = trim_data(raw_X, raw_Y, aux_params["graph_left_cutoff"], aux_params["graph_right_cutoff"])
	span_dt, span_cvert = trim_data(raw_X, raw_Y, aux_params["dt_min"], aux_params["dt_max"])
	
	guess_dt = []
	guess_cvert = []
	#shorten span_dt, span_cvert even further so that you only do a certain number of itterations
	max_itterations = 200
	span_length = len(span_dt)
	if span_length > max_itterations:
	    max_index = span_length-1
	    index_interval = int(max_index/max_itterations)
	    #print(max_index, span_dt[max_index])
	    for i in range(0, max_itterations):
	        span_index = i*index_interval
	        #print(span_index, span_dt[91])
                guess_dt.append(span_dt[span_index])
                guess_cvert.append(span_cvert[span_index])
            
	
	loss = 0
	best_guess_index = 0
	loss_array = []
	loss_array.append(['dt', 'loss'])
	
	
	print("itterating through guess array of length %s" % (len(guess_dt)))
	for index in range(0, len(guess_dt)):
	   aux_params['dt'] = guess_dt[index]
	   aux_params['cvert'] = guess_cvert[index]
	   guess_params, guess_loss = scipy_optimize(optimization_X, optimization_Y, aux_params, parameter_guess)
           loss_array.append([guess_dt[index], guess_loss])

	   if loss == 0 or guess_loss < loss:
	       new_params = guess_params
	       loss = guess_loss 
	       best_guess_index = index
	       print("best guess is now %.2f at dt of %s" % (loss, guess_dt[index]))
	   else:
	       continue

        string_name = 'dtVsLoss.csv'
	#write loss vs dt graph
        with open(string_name, 'w+') as fp: 
            a = csv.writer(fp)
            for y in range(len(loss_array[0])):
                a.writerow([x[y] for x in loss_array]) 
                          
	print("Final best guess was at dt = %s" % guess_dt[best_guess_index])

	aux_params['dt'] = guess_dt[best_guess_index]
	aux_params['cvert'] = guess_cvert[best_guess_index]
	
        asymptote_Y = getAsymtote_Y(new_params, aux_params)
	aux_params['bt'] = asymptote_Y - saturation_function(aux_params['optimization_left_cutoff'], new_params, aux_params)
	print("dt = %.2f cvert = %.2f bt = %.2f" % (aux_params['dt'], aux_params['cvert'], aux_params['bt']))

	if new_params is not None:
		# write the parameters to disk
		with open (OUTPUT_FILE, "w") as fp:
			for i in range(len(TUNED_PARAMS)):
				fp.write("%s = %s\n" % (TUNED_PARAMS[i].upper(), str(new_params[i])))
				print("%s = %s" % (TUNED_PARAMS[i].upper(), str(new_params[i])))
			for k in sorted(USER_DEFINED_PARAMS):
				fp.write("%s = %s\n" % (k, str(aux_params[k])))
			fp.write("%s = %s\n" % ('dt', aux_params['dt']))
			fp.write("%s = %s\n" % ('cvert', aux_params['cvert']))
			fp.write("%s = %s\n" % ('bt', aux_params['bt']))

	
		show_data(display_X, display_Y, parameter_guess, new_params, aux_params)