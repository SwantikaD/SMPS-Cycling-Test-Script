########################################################
#HkpsThermalCyclingScript.py
#Created on: Feb 21, 2024
#Author: Swantika Dhundia
########################################################


import pyvisa
import time
import csv
from datetime import datetime
import msvcrt
import sys

def query_HV_Sorenson(query):

    for attempt in range(3):
        try:
            reply = inst1.query(query, delay = 0.1)
        except Exception as e:
            print(e)
            if attempt == 2:
                 print(datetime.now(), 'HV PSU not responding...')
                 reply = '-1'
            else:
                 print(datetime.now(), 'Resend query to HV PSU...')
                 time.sleep(2)
                 continue  
        else: 

            break

    return reply


def query_Eload_8602(query, loadType):
	if loadType == 'Primary':
	    for attempt in range(3):
	        try:
	            reply = inst2.query(query, delay = 0.1)
	        except Exception as e:
	            print(e)
	            if attempt == 2:
	                 print(datetime.now(), 'Primary eload not responding...')
	                 reply = '-1'
	            else:
	                 print(datetime.now(), 'Resend query to primary eload...')
	                 time.sleep(2)
	                 continue  
	        else: 

	            break
	elif loadType == 'Secondary':
	    for attempt in range(3):
	        try:
	            reply = inst3.query(query, delay = 0.1)
	        except Exception as e:
	            print(e)
	            if attempt == 2:
	                 print(datetime.now(), 'Secondary eload not responding...')
	                 reply = '-1'
	            else:
	                 print(datetime.now(), 'Resend query to secondary eload...')
	                 time.sleep(2)
	                 continue  
	        else: 

	            break

	return reply


def datalog(logFile,time_on_off):

	for i in range(int(time_on_off)):

		hv_volt = float(query_HV_Sorenson('MEAS:VOLT?'))

		time.sleep(0.05)

		hv_curr = float(query_HV_Sorenson('MEAS:CURR?'))

		time.sleep(0.05)

		priEload_volt = float(query_Eload_8602(':MEAS:VOLT?', 'Primary'))

		time.sleep(0.05)

		priEload_curr = float(query_Eload_8602(':MEAS:CURR?', 'Primary'))

		time.sleep(0.05)

		secEload_volt = float(query_Eload_8602(':MEAS:VOLT?', 'Secondary'))

		time.sleep(0.05)

		secEload_curr = float(query_Eload_8602(':MEAS:CURR?', 'Secondary'))

		time.sleep(0.05)

		ts = datetime.now()
		ts_trunc = ts.replace(microsecond=0)

		#Print to console
		#print(ts_trunc, volt, curr)

		#write to csv file
		info = {'Timestamp': ts_trunc , 'HV_Voltage': hv_volt, 'HV_Current': hv_curr, \
		'PriEload_Voltage': priEload_volt, 'PriEload_Current': priEload_curr, \
		'SecEload_Voltage': secEload_volt, 'SecEload_Current': secEload_curr}
		
		with open('C:\\Data\\'+logFile, 'a', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames)
			csv_writer.writerow(info)

		#wait
		time.sleep(0.3)

#Generate csv filename
now = datetime.now()
now_str = now.strftime('%Y-%m-%d_%H-%M-%S')
csv_filename = 'HKPS_TC_testdata-{}.csv'.format(now_str)
print(csv_filename)

#Create data log file with headers
fieldnames = ['Timestamp','HV_Voltage','HV_Current','PriEload_Voltage','PriEload_Current',\
 'SecEload_Voltage', 'SecEload_Current']
with open('C:\\Data\\' + csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames)
    csv_writer.writeheader()

#Get user inputs: V_set, I_set, t_on, t_off
v_set = input('Enter voltage setting in volts: ')
i_set = input('Enter current setting in amps: ')
t_on = input('Enter 400V on time in sec: ')
t_off = input('Enter 400V off time in sec: ')

#List visa resources
print('\nConnecting to instrument....')
rm = pyvisa.ResourceManager()
print('List of visa resources')
print(rm.list_resources())
inst1 = rm.open_resource('ASRL6::INSTR')
inst2 = rm.open_resource('GPIB0::2::INSTR')
inst3 = rm.open_resource('GPIB0::1::INSTR')

#configure measurement instrument
inst1.read_termination = '\r'
inst1.write_termination = '\r'
inst1.timeout = 5000

inst2.read_termination = '\n'
inst2.write_termination = '\n'
inst2.timeout = 5000

inst3.read_termination = '\n'
inst3.write_termination = '\n'
inst3.timeout = 5000

###############################Configure HV PSU######################################################

#check communication with HV PSU
instrConnStatus = query_HV_Sorenson('*IDN?')
if instrConnStatus == '-1':
	sys.exit(1)
print(instrConnStatus)

print('Configuring the HV PSU...')

#Turn off if on
instrStatus = query_HV_Sorenson('OUTP?')
if instrStatus == '1':
    inst1.write('OUTP OFF')
    time.sleep(0.1)
    print('HV was on. Now turned: ' + query_HV_Sorenson('OUTP?'))
elif instrStatus == '0':
    print('HV is off')

#Enter settings
inst1.write('VSET ' + v_set)
time.sleep(0.1)
if float(query_HV_Sorenson('VSET?')) != float(v_set):
	sys.exit(1)

inst1.write('ISET ' + i_set)
time.sleep(0.1)
if float(query_HV_Sorenson('ISET?')) != float(i_set):
	sys.exit(1)

print('HV PSU configuration complete...')

###############################Configure Pri Eload######################################################

#check communication with Pri Eload
instrConnStatus = query_Eload_8602('*IDN?', 'Primary')
if instrConnStatus == '-1':
	sys.exit(1)
print(instrConnStatus)

print('Configuring the primary eload...')

#Turn off if on
instrStatus = query_Eload_8602('INP?', 'Primary')
if instrStatus == '1':
    inst2.write('INP OFF', 'Primary')
    time.sleep(0.1)
    print('Eload was on. Now turned: ' + query_Eload_8602('INP?', 'Primary'))
elif instrStatus == '0':
    print('Eload is off')

#Enter settings
inst2.write('FUNC RES')
time.sleep(0.1)
if query_Eload_8602('FUNC?', 'Primary') != 'RESISTANCE':
	sys.exit(1)

inst2.write('RES 22')
time.sleep(0.1)
if query_Eload_8602('RES?', 'Primary') != '22':
	sys.exit(1)

inst2.write('CURRent:PROTection:STATe 1')
time.sleep(0.1)
if query_Eload_8602('CURRent:PROTection:STATe?', 'Primary') != '1':
	sys.exit(1)

inst2.write('CURRent:PROTection:LEVel 3')
time.sleep(0.1)
if query_Eload_8602('CURRent:PROTection:LEVel?', 'Primary') != '3':
	sys.exit(1)

print('Primary eload configuration complete...')

###############################Configure Sec Eload######################################################

#check communication with Sec Eload
instrConnStatus = query_Eload_8602('*IDN?', 'Secondary')
if instrConnStatus == '-1':
	sys.exit(1)
print(instrConnStatus)

print('Configuring the secondary eload...')

#Turn off if on
instrStatus = query_Eload_8602('INP?', 'Secondary')
if instrStatus == '1':
    inst3.write('INP OFF')
    time.sleep(0.1)
    print('Eload was on. Now turned: ' + query_Eload_8602('INP?', 'Secondary'))
elif instrStatus == '0':
    print('Eload is off')

#Enter settings
inst3.write('FUNC RES')
time.sleep(0.1)
if query_Eload_8602('FUNC?', 'Secondary') != 'RESISTANCE':
	sys.exit(1)

inst3.write('RES 16')
time.sleep(0.1)
if query_Eload_8602('RES?', 'Secondary') != '16':
	sys.exit(1)

inst3.write('CURRent:PROTection:STATe 1')
time.sleep(0.1)
if query_Eload_8602('CURRent:PROTection:STATe?', 'Secondary') != '1':
	sys.exit(1)

inst3.write('CURRent:PROTection:LEVel 3')
time.sleep(0.1)
if query_Eload_8602('CURRent:PROTection:LEVel?', 'Secondary') != '3':
	sys.exit(1)

print('Secondary eload configuration complete...')

try:

	while True:

		#Turn on pri eload
		inst2.write('RES 22')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('RES?', 'Primary')
		if instrStatus != '22':
		     raise Exception('Primary eload not set to 22ohm')
		time.sleep(1)

		inst2.write('INP ON')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('INP?', 'Primary')
		if instrStatus != '1':
		     raise Exception('Primary eload did not turn on')
		time.sleep(1)

		#Turn on sec eload
		inst3.write('INP ON')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('INP?', 'Secondary')
		if instrStatus != '1':
		     raise Exception('Secondary eload did not turn on')
		time.sleep(1)

        #Turn on 400V
		inst1.write('OUTP ON')
		time.sleep(0.5)
		instrStatus = query_HV_Sorenson('OUTP?')
		if instrStatus != '1':
		     raise Exception('HV did not turn on')
		print('HV is on...\n')
		time.sleep(1)

		#log data
		datalog(csv_filename, t_on)

		#Turn off sec eload
		inst3.write('INP OFF')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('INP?', 'Secondary')
		if instrStatus != '0':
		     raise Exception('Secondary eload did not turn off')
		time.sleep(1)

		"""
		#Turn off pri eload
		inst2.write('INP OFF')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('INP?', 'Primary')
		if instrStatus != '0':
		     raise Exception('Primary eload did not turn off')
		time.sleep(1)
		"""

		#Change pri load for FC discharge
		inst2.write('RES 60')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('RES?', 'Primary')
		if instrStatus != '60':
		     raise Exception('Primary eload not set to 60ohms')
		
		"""
		#Turn on pri eload
		inst2.write('INP ON')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('INP?', 'Primary')
		if instrStatus != '1':
		     raise Exception('Primary eload did not turn on')
		time.sleep(1)
		"""

		#Turn off 400V
		inst1.write('OUTP OFF')
		time.sleep(0.5)
		instrStatus = query_HV_Sorenson('OUTP?')
		if instrStatus != '0':
			raise Exception('HV did not turn off')
		print('HV is off...\n')

		#log data
		datalog(csv_filename, t_off)

		inst2.write('INP OFF')
		time.sleep(0.5)
		instrStatus = query_Eload_8602('INP?', 'Primary')
		if instrStatus != '0':
		     raise Exception('Primary eload did not turn off')

		time.sleep(1)
                            
except (KeyboardInterrupt, Exception) as e:
    print(e)
    inst2.write('INP OFF')
    time.sleep(0.1)
    inst3.write('INP OFF')
    time.sleep(0.1)
    inst1.write('OUTP OFF')
    time.sleep(0.1)
    inst1.close()
    inst2.close()
    inst3.close()
    rm.close()
    print('Program complete....')
    k = input('Press any key to close the console window...')

