x = 500
y = 500

ax = x/1280.0
ay = y/768.0

rx = 100
ry = 40


# Problem 4 - Op Amps

# Non-inverting Op Amp
r_1 = 10000.0
r_2 = 10000.0
k = (r_1+r_2)/r_2

v_1 = 7.0
v_o = k*(v_1 -5) + 5

# Inverting Op Amp
r_1 = 20000
r_2 = 10000.0
k = -r_1/r_2

v_2 = 5.0
v_o = k*(v_2-5) + 5


# Transimpedence Amplifier
r1 = 100000000.0
r2 = 1700.0
r3 = 170000.0
pmt = -10.0*(10.0**-12)

vo = pmt*r1
vout = (-r3/r2)*vo


# Audio Mixer
a = 0.79
r1 = r2 = r3 = 4000.0 * (1.0-a)
r4 = r5 = r6 = 460.0
r7 = 4600.0
r8 = 2600.0
r9 = 26000.0

v1 = 0.013
v2 = 0.067
v3 = 0.042

pmt = 8.16136527457305e-05
vo = pmt*r7
vout = (-r9/r8)*vo

print vout
