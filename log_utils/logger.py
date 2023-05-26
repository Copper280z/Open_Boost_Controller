import os
import sys
from glob import glob
import serial
import datetime

DEBUG = True
max_file_length = 100000
max_number_files = 100
target = 'Adafruit'
log_dir = r'~/Documents/CircuitPy Boost Controller/logs'
date_fmt = '%Y-%m-%d %H:%M:S'

timedate = datetime.datetime.now().strftime(date_fmt)


def cleanup_files():
    files = glob(log_dir + '//*.bstlog')
    if len(files >= max_number_files):
        curr_time = datetime.datetime.now()
        age = []
        for file in files:
            try:
                datestr = file.split('/')[-1].split('_')
                diff = curr_time - datetime.datetime.strptime(datestr,date_fmt)
                age.append(diff.total_seconds())
            except:  # noqa
                age.append(1e9)

        # delete oldest file here


print(f'Log started on: {timedate}')

devices = glob('/dev/*')

dev_by_id = glob('/dev/serial/by-id/*')

target_dev_list = [dev for dev in dev_by_id if target in dev]

print(f'{[dev for dev in dev_by_id if target in dev]}\n')
# print(f'{[dev for dev in devices if "tty" in dev]}\n')

if len(target_dev_list) == 0 and not DEBUG:
    print('Device not found, exiting')
    sys.exit()

target_dev = target_dev_list[0]

n_files = 0
while True:
    filename = timedate + f'{n_files}.bstlog'
    n_lines = 0
    with serial.Serial(target_dev):
        with open(filename,'w') as f:
            while n_lines < max_file_length:
                line = serial.readline()
                f.writelines(line)
                n_lines += 1
