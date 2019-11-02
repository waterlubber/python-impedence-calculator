# Each electrical comment has a class. The class handles characteristics of a particular "model" of component; eg a 1uF capacitor in a series configuration.
# Classes also contain some functions, for example, the .impede method will calculate the affect a component has on impedence.
# This class-based approaches makes it easier to add electrical components later.
from math import pi
from math import tan
from constants import c


class Capacitor:
    def __init__(self, cap, freq, configuration):
        self.cap = cap  # in Farads
        self.shunt = configuration  # Series (0) or Shunt (1)
        self.reactance = 1 / (2 * pi * freq * self.cap)
        self.type = 'c'
        self.freq = freq

    def getData(self, n):
        return "C{0}: {1:8.4g} F\tX: -{2:8.4g}j".format(n, self.cap, self.reactance)

    def impede(self, inz):
        if self.shunt:
            # Shunt components are best handled by adding their admittance to the admittance of the rest of the circuit.
            inz = 1 / inz  # convert to admittance
            inz += 1 / complex(0, -1 * self.reactance)  # add the admittance of the capacitor
            return 1 / inz  # convert back to impedence
        else:
            return inz + complex(0, -1 * self.reactance)  # add the capacitive reactance of the capacitor


class Inductor:
    def __init__(self, ind, freq, configuration):
        self.ind = ind  # in Henry
        self.shunt = configuration  # Series or Shunt
        self.reactance = 2 * pi * freq * self.ind
        self.type = 'l'
        self.freq = freq

    def getData(self, n):
        return "L{0}: {1:8.4g} H\tX: +{2:8.4g}j".format(n, self.ind, self.reactance)

    def impede(self, inz):
        if self.shunt:
            inz = 1 / inz  # convert to admittance
            inz += 1 / complex(0, self.reactance)  # add the admittance of the inductor
            return 1 / inz  # convert back to impedence
        else:
            return inz + complex(0, self.reactance)  # add the inductive reactance of the inductor

class TransmissionLine:
    # Transmission lines are much more complicated, and thus are only modelled for series configuration.
    # length = physical length, characteristic = characteristic impedence, vf = velocity factor, configuration = shunt/series
    # TODO: Figure out how to handle stubs and other transmission lines
    def __init__(self, plength, characteristic, vf, freq, configuration):
        self.length = plength * vf
        self.impedence = characteristic
        self.shunt = configuration
        self.type = 't'
        self.freq = freq

    def getData(self, n):
        return "T{0}: ".format(n) + str(self.impedence) + " Ω\t{0:.1f} m\t{1:8.4g} λ".format(self.length, self.length / (c / self.freq))

    def impede(self, inz):
        waveNumber = 2 * pi / (c / self.freq)  # wavenumber = 2pi / λ
        zOut = self.impedence * complex(inz, self.impedence * tan(waveNumber * self.length))
        zOut /= complex(self.impedence, inz * tan(waveNumber * self.length))
        return zOut


class Resistor:
    def __init__(self, r, configuration):
        self.resistance = r
        self.shunt = configuration
        self.type = 'r'

    def getData(self, n):
        return "R{0}: {1:8.4g} Ω".format(n, self.resistance)

    def impede(self, inz):
        if self.shunt:
            inz = 1 / inz
            inz += 1/complex(self.resistance, 0)
            return 1 / inz
        else:
            return inz + complex(self.resistance, 0)