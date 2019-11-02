from math import pi
from math import tan
import cmath as cx

frequency = 0
c = 299792458


class Capacitor:
    def __init__(self, capacitance, configuration):
        self.cap = capacitance  # in Farads
        self.shunt = configuration  # Series (0) or Shunt (1)
        self.reactance = 1 / (2 * pi * frequency * self.cap)
        self.type = 'c'

    def getData(self, n):
        return "C{0}: {1:8.4g} F\tX: -{2:8.4g}j".format(n, self.cap, self.reactance)

    def impede(self, inz):
        if self.shunt:
            inz = 1 / inz  # convert to admittance
            inz += 1 / complex(0, -1 * self.reactance)  # add the admittance of the capacitor
            return 1 / inz  # convert back to impedence
        else:
            return inz + complex(0, -1 * self.reactance)  # add the capacitive reactance of the capacitor


class Inductor:
    def __init__(self, inductance, configuration):
        self.ind = inductance  # in Henry
        self.shunt = configuration  # Series or Shunt
        self.reactance = 2 * pi * frequency * self.ind
        self.type = 'l'

    def getData(self, n):
        return "L{0}: {1:8.4g} H\tX: +{2:8.4g}j".format(n, self.ind, self.reactance)

    def impede(self, inz):
        if self.shunt:
            inz = 1 / inz  # convert to admittance
            inz += 1 / complex(0, *self.reactance)  # add the admittance of the inductor
            return 1 / inz  # convert back to impedence
        else:
            return inz + complex(0, *self.reactance)  # add the inductive reactance of the inductor


class TransmissionLine:
    # length = physical length, characteristic = characteristic impedence, vf = velocity factor, configuration = shunt/series
    #TODO: Figure out how to handle stubs and other transmission lines
    def __init__(self, length, characteristic, vf, configuration):
        self.length = length * vf
        self.impedence = characteristic
        self.shunt = configuration
        self.type = 't'

    def getData(self, n):
        return "T{0}: ".format(n) + str(self.impedence) + " Ω\t{0:.1f} m\t{1:8.4g} λ".format(self.length,
                                                                                             self.length / (
                                                                                                         c / frequency))

    def impede(self, inz):
        waveNumber = 2 * pi / (c / frequency)  # wavenumber = 2pi / λ
        zOut = self.impedence * complex(inz, self.impedence * tan(waveNumber * self.length))
        zOut /= complex(self.impedence, inz * tan(waveNumber * self.length))
        return zOut


class Resistor:
    def __init__(self, resistance, configuration):
        self.resistance = resistance
        self.shunt = configuration
        self.type = 'r'

    def getData(self, n):
        return "R{0}: {1:8.4g} Ω".format(n, self.resistance)

    def impede(self, inz):
        if self.shunt:
            inz = 1 / inz
            inz += complex(self.resistance, 0)
            return 1 / inz
        else:
            return inz + complex(self.resistance, 0)


# TODO: Figure out what to do with this mess.
# class Impedence:
#     def __init__(self, imp):
#         self.impedence = imp

def getImpedence(prompt):
    while True:
        impedenceString = input(prompt)
        impedenceString = impedenceString.replace(" ", "")
        try:
            impedence = complex(impedenceString)
        except ValueError as e:
            print("Error: " + str(e))
            print("Ensure that you are inserting j after the number")
            impedence = None
        if impedence is not None:
            return impedence


def printcircuit(circ):
    nC = nL = nT = nR = 0  # Counts for the types
    # Generate a map of the circuit, as well as values for each element.
    sep = " — "
    sepB = "   "
    diagram = ["Zi"]
    diagramB = ["  "]  # Bottom Diagram
    data = []
    for i in circ:
        if i.type == "c":
            nC += 1
            if i.shunt:
                diagram.append("\/")
                diagramB.append("C" + str(nC))
            else:
                diagram.append("C" + str(nC))
                diagramB.append("  ")
            data.append(i.getData(nC))
        elif i.type == "l":
            nL += 1
            if i.shunt:
                diagram.append("\/")
                diagramB.append("L" + str(nL))
            else:
                diagram.append("L" + str(nL))
                diagramB.append("  ")
            data.append(i.getData(nL))
        elif i.type == "t":
            nT += 1
            if i.shunt:
                diagram.append("\/")
                diagramB.append("T" + str(nT))
            else:
                diagram.append("T" + str(nT))
                diagramB.append("  ")
            data.append(i.getData(nT))
        elif i.type == "r":
            nR += 1
            if i.shunt:
                diagram.append("\/")
                diagramB.append("R" + str(nR))
            else:
                diagram.append("R" + str(nR))
                diagramB.append("  ")
            data.append(i.getData(nR))
    diagram.append("Zo")
    print("Circuit Diagram:")
    print(sep.join(diagram))
    print(sepB.join(diagramB))
    print("Component Data:\n")
    # Then, print out the values for each component.
    print('\n'.join(data) + '\n' + '\n')


def getconfig():
    while True:
        egg = input("Series (se) or Shunt (sh): ").lower()
        if "sh" in egg:
            return True
        elif "se" in egg:
            return False
        else:
            print('Error: Invalid input. Please enter "series" or "shunt"')


def calculateoutput(inz, circuit):
    for item in circuit:
        inz = item.impede(inz)
    return inz


# Program Start
impedence = getImpedence("Please enter the input (load) impedence in form a ± bj: ")
while frequency is 0:
    frequency = float(input("Please enter a frequency in Hz: "))
circuit = []

# User Input Time
helpMenu = "C: Add Capacitor\tL: Add Inductor\t\tR: Add Resistor\tT: Add Transmission Line\nP: Print Circuit\tD: Calculate Output\tX: Clear Data\tH: Help\tQ: Quit"
print("Please enter an action.")
print(helpMenu)
while True:
    action = input("Action: ").lower()
    # why can't we have switch cases :(
    if action == 'q':
        raise SystemExit
    elif action == 'd':
        calculateoutput(circuit)
    elif action == 'p':
        printcircuit(circuit)
    elif action == 'x':
        circuit = []
    elif action == 'h':
        print(helpMenu)
    elif action == 'c':
        config = getconfig()
        capacitance = float(input("Please enter a capacitance in Farad: "))
        circuit.append(Capacitor(capacitance, config))
    elif action == 'l':
        config = getconfig()
        inductance = float(input("Please enter an inductance in Henry: "))
        circuit.append(Inductor(inductance, config))
    elif action == 't':
        config = getconfig()
        length = float(input("Please enter the length in meters: "))
        z = getImpedence("Please enter the characteristic impedence in the form a ± bj: ")
        vf = float(input("Please enter the Velocity Factor as a fraction of c: "))
        circuit.append(TransmissionLine(length, z, vf, config))
    elif action == 'r':
        config = getconfig()
        resistance = float(input("Please enter the resistance in Ohm: "))
        circuit.append(Resistor(resistance, config))
    else:
        print(
            "C: Add Capacitor\tL: Add Inductor\tT: Add Transmission Line\tR: Add Resistor\nP: Print Current Circuit\tC: Calculate Output Impedence\tH: Help\tQ: Quit")
