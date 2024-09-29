# SMPS-Cycling-Test-Script

## Overview
This Python script automates testing of the SMPS (Switched Mode Power Supply) PCB, which converts high voltage (HV) input to two low voltage (LV) outputs. Using the PyVISA library, it controls the Sorenson XG600-1.4 high voltage power supply and BK Precision Electronic Load 8602. The script cycles power to the SMPS under user-defined conditions and loads the outputs to validate functionality and assess durability. Diagnostics are logged every second for reference or troubleshooting.

For ease of use, the repository includes both the Python script (.py) for customization and an executable (.exe) for direct implementation without requiring any additional setup.


## Features
- Instrument communication check: Automatically verifies connectivity with the power supply and electronic loads at the start of each test.
- User-configurable PSU settings: Allows control of input voltage, current, and power cycle timing.
- Electronic load setup: Configures ELoad1 to 22 ohms and ELoad2 to 16 ohms, with current protection enabled.
- 1-second data logging: Records voltage and current values from the power supply and loads.
- Retry mechanism: Retries communication with instruments up to 3 times before aborting the test.
- Safe shutdown: Easily stop the test and power off all instruments with CTRL+C.


## Prerequisites 

***For running/customizing the Python script (SMPSThermalCyclingScript.py):***

- Python 3.10 (or higher)
- PyVISA (`pip install pyvisa==1.13.0` or `pip install -r requirements.txt`)
- National Instruments VISA (or another VISA backend)
  
You can download the NI-VISA drivers from the [NI website](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html).

***For running the Executable (SMPSThermalCyclingScript.exe):***

- National Instruments VISA (or another VISA backend)
  
You can download the NI-VISA drivers from the [NI website](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html).


## Usage
1. Clone this repository: 
    git clone https://github.com/SwantikaD/SMPS-Cycling-Test-Script

2. Create `Data` folder in C drive to store the test data logs. 

3. Open command prompt, navigate to the repo location and run the executable:
    cd <path/to/executable>
    SMPSThermalCyclingScript.exe

4. Enter the settings for input HV Power Supply when prompted. See example below:
    Enter voltage setting in volts: 400
    Enter current setting in amps: 0.8
    Enter power on time in sec: 900
    Enter power off time in sec: 900

5. The test starts automatically after configuration.

6. Press Ctrl+C to stop the test at any time. 


# Logging
Test data is logged every second and saved as `HKPS_TC_testdata-{}.csv` in the C:/Data folder. The log captures the following parameters with timestamps:

- HV Voltage (HV_V)
- HV Current (HV_I)
- Load 1 Voltage (Load1_V)
- Load 1 Current (Load1_I)
- Load 2 Voltage (Load2_V)
- Load 2 Current (Load2_I)


# Troubleshooting
1. Connection Issues
    - Ensure all hardware connections are correct and secure.
    - Verify that the instruments are using the correct serial port and GPIB addresses:
        HV PSU: ASRL6::INSTR
        Load 1: GPIB0::2::INSTR
        Load 2: GPIB0::1::INSTR

2. Communication Errors
    If the script connects but fails to communicate (i.e., all 3 retry attempts fail):
    - Power cycle the instrument and rerun the script.
    - If the issue persists, use Keysight Command Expert to reset the instrument:
        - Install Keysight Command Expert.
        - Connect to the instrument and send a reset SCPI command.
        - For a tutorial, watch this video: https://www.youtube.com/watch?v=nHSU6RjHCqE

    





