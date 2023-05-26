from target_tables import target_table as target
import MS_can_def as can_def
from interp import interp2d

try:
    from ulab import numpy as np
except:  # noqa
    import numpy as np  # noqa
import time
import PID_CPY as PID
import canio
import gc
import digitalio
import board
import struct
import pwmio as p
from analogio import AnalogIn

DEBUG = False

KP = 0.0135   # 0.01
KI = 0.025   # 0.03
KD = 0.0013  # 0.0017

valve_frequency = 30
sample_time = 0.05


def get_can_data():
    data = {}
    while True:
        message = listener.receive()
        if message is not None:
            # print(f'CAN Message - ID:{message.id}')
            data[message.id] = message

            if all(key in data for key in (1520, 1523, 1522)):
                break
    return data


def get_voltage(pin, gain):
    pin_volts = (pin.value * 3.3) / 65536

    corr_volts = pin_volts / gain

    return (pin_volts, corr_volts)


# If the CAN transceiver has a standby pin, bring it out of standby mode
if hasattr(board, 'CAN_STANDBY'):
    standby = digitalio.DigitalInOut(board.CAN_STANDBY)
    standby.switch_to_output(False)
# If the CAN transceiver is powered by a boost converter, turn on its supply
if hasattr(board, 'BOOST_ENABLE'):
    boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
    boost_enable.switch_to_output(True)


can = canio.CAN(rx=board.CAN_RX,
                tx=board.CAN_TX,
                baudrate=500_000,
                auto_restart=True)

listener = can.listen(timeout=.1)
old_bus_state = None

pid = PID.PID(KP,
              KI,
              KD,
              sample_time=sample_time,
              setpoint=5,
              output_limits=(0, 1),
              integral_in_band=(-500, 30))

pwmPin1 = p.PWMOut(board.D5,
                   duty_cycle=65535,
                   frequency=valve_frequency)

duty_cycle = 65535
decoded_data = {}
decoded_data['remote'] = 0
decoded_data['remote_value'] = 65535

# setup analog channels
a_gain = 0.6
ain0 = AnalogIn(board.A0)
ain1 = AnalogIn(board.A1)

while True:

    t0 = time.monotonic_ns()

    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
    data = get_can_data()

    t1 = time.monotonic_ns()

    for key in data:
        if key in can_def.keys.keys():
            decoded_data.update(can_def.decode(data[key]))
        elif key == 1320:
            decoded_data['remote'] = struct.unpack('>H', data[key].data[0:2])[0]
            decoded_data['remote_value'] = struct.unpack('>H', data[key].data[2:4])[0]

    coords = (decoded_data['RPM'], decoded_data['TPS'])
    target_val = interp2d(coords, target)

    pid.setpoint = target_val  # 170
    control = pid(decoded_data['MAP'])

    if decoded_data['MAP'] < 90 or decoded_data['RPM'] < 400:
        duty_cycle = 65535  # set valve to open, min boost, while throttle is closed
    else:
        duty_cycle = int((1.0 - control) * 65535)

    if decoded_data['remote'] == 1:
        pwmPin1.duty_cycle = decoded_data['remote_value']
    else:
        pwmPin1.duty_cycle = duty_cycle

    gc.collect()
    t2 = time.monotonic_ns()

    # print(f"RPM: {decoded_data['RPM']} - TPS:{decoded_data['TPS']} - MAP: {decoded_data['MAP']} - Target: {target_val} - DC: {duty_cycle}")
    print(f"({decoded_data['RPM']},{decoded_data['TPS']},{decoded_data['MAP']},{target_val},{duty_cycle}, {pid.components[0]}, {pid.components[1]}, {pid.components[2]})")

    if DEBUG:
        print(f'Wait for CANbus Time - {(t1-t0)/1e9:.4f}s')
        print(f'Calculation Time - {(t2-t1)/1e9:.4f}s')
        print(f'PID Components: {pid.components}')
        print(f'PID Error: {pid.error}')
        print(f"process_val: {decoded_data['MAP']}")
        print(f'target_val: {target_val}')
        print(f'control: {control}')
        print(f'duty_cycle: {duty_cycle}')
        print('\n')

    # print(f'Analog input 0 voltage: {get_voltage(ain0,0.6)}')
    # print(f'Analog input 1 voltage: {get_voltage(ain1,180)}')
    # print('\n')
    # time.sleep(0.1)
