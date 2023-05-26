# Open_Boost_Controller
This project is intended to implement a PID boost controller which retrieves engine data from a Megasquirt based ECU over the can bus. The ECU is configued in dash broadcast mode and the data definition is stored in MS_can_def.py. If you're using a different ECU, modify this file to match the can bus definition published by the manufacturer. 

Setpoint is determined by a lookup table of RPM vs TPS, the value is determined by a linear interpolation using the current state and the 4 points on the table bounding it. Additional tables can easily be added using whatever parameters you desire, so long as they're available on the CAN bus. An example might be a modifier table based on coolant temperature, which is setup to subtract from the setpoint when the engine is too cold or too hot.

Integral windup protection is implemented by zeroing out the integral term unless the process is within some defined band around the setpoint. This, combined with an appropriate value for the P term, ensures that there's minimal overshoot during the initial spool up phase.

This has been implemented using an Adafruit Feather M4 CAN, which drives a common 4 port solenoid using an IRLZ44n MOSFET. Note a ~30v zener diode is strongly recommended to protect the mosfet from the inductive voltage spike which occurs when the circuit is opened. This also gives the controller better control authority over the solenoid in comparison to a flyback diode.
