import numpy as np
from matplotlib import pyplot as plt
import glob
import re

path = r'../logs/'
filenames = glob.glob(path + '//screenlog.*')

with open(filenames[0],'r') as f:
    contents = f.readlines()

values = []
for line in contents:
    numbers = [float(n) for n in re.findall("[(,]*([^(,]*?)[,)]", line)]
    if len(numbers) > 0:
        values.append(numbers)

# print(values)

values = np.asarray(values)

ax = plt.subplot(311)
ax2 = ax.twinx()
ax3 = ax.twinx()

ln1 = ax.plot(values[:,0],'b')  # RPM
ln2 = ax2.plot(values[:,1],'r')  # TPS
ln3 = ax3.plot(values[:,4],'k')  # DC

plt.legend(ln1 + ln2 + ln3, ['RPM',
                             'TPS',
                             'Duty Cycle'])

plt.subplot(312, sharex=ax)
plt.plot(values[:,2],'g')  # MAP
plt.plot(values[:,3],'m')  # MAP Target

plt.legend(['MAP', 'Boost Target'])


plt.subplot(313, sharex=ax)

plt.plot(values[:,5])
plt.plot(values[:,6])
plt.plot(values[:,7])

plt.legend(['P Component',
            'I Component',
            'D Component'])
plt.show()
