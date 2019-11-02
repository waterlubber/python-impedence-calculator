from math import pi
from math import tan

frequency = 0
c = 299792458 # Speed of light

# Each electrical comment has a class. The class handles characteristics of a particular "model" of component; eg a 1uF capacitor in a series configuration.
# Classes also contain some functions, for example, the .impede method will calculate the affect a component has on impedence.
# This class-based approaches makes it easier to add electrical components later.
class Capacitor:
    def __init__(self, cap, configuration):
        self.cap = cap  # in Farads
        self.shunt = configuration  # Series (0) or Shunt (1)
        self.reactance = 1 / (2 * pi * frequency * self.cap)
        self.type = 'c'

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
    def __init__(self, ind, configuration):
        self.ind = ind  # in Henry
        self.shunt = configuration  # Series or Shunt
        self.reactance = 2 * pi * frequency * self.ind
        self.type = 'l'

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
    def __init__(self, plength, characteristic, vf, configuration):
        self.length = plength * vf
        self.impedence = characteristic
        self.shunt = configuration
        self.type = 't'

    def getData(self, n):
        return "T{0}: ".format(n) + str(self.impedence) + " Ω\t{0:.1f} m\t{1:8.4g} λ".format(self.length, self.length / (c / frequency))

    def impede(self, inz):
        waveNumber = 2 * pi / (c / frequency)  # wavenumber = 2pi / λ
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


def getImpedence(prompt): # This function will query the user for an impedence value.
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


def printcircuit(circ): # This function generates an ASCII art image of the circuit, for reference purposes.
    nC = nL = nT = nR = 0  # Counts for the types
    # Generate a map of the circuit, as well as values for each element.
    sep = " — "
    sepB = "   "
    diagram = ["Zi"]
    diagramB = ["  "]  # Bottom Diagram
    data = []
    for i in circ:
        # TODO: Rewrite this to not use if blocks and instead use a more adaptive approach.
        # It's pretty messy, but it works well.
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
    # Query for series or shunt configuration.
    while True:
        egg = input("Series (se) or Shunt (sh): ").lower()
        if "sh" in egg:
            return True
        elif "se" in egg:
            return False
        else:
            print('Error: Invalid input. Please enter "series" or "shunt"')

def calculateoutput(inz, circuit):
    # Thanks to the impedence transforms being located in the component classes, this is a very, very short bit of code.
    # It simply applies all of the component's changes one after another
    for item in circuit:
        inz = item.impede(inz)
    return inz


# START OF PROGRAM FLOW
# This is where the program actually beings.
impedence = getImpedence("Please enter the input (load) impedence in form a ± bj: ")
while frequency is 0:
    frequency = float(input("Please enter a frequency in Hz: "))
circuit = []

# Main User Input Loop
helpMenu = "C: Add Capacitor\tL: Add Inductor\t\tR: Add Resistor\tT: Add Transmission Line\nP: Print Circuit\tD: Calculate Output\tX: Clear Data\tH: Help\tQ: Quit"
print("Please enter an action.")
print(helpMenu)
while True:
    action = input("Action: ").lower()
    # why can't we have switch cases :(
    if action == 'q': # Quit
        raise SystemExit
    elif action == 'd': # Calculate Output data
        Zo = calculateoutput(impedence, circuit)
        print("Impedence at Z₀: {:.2f} Ω".format(Zo))
        Zi = 50
        Gamma = (Zi - Zo)/(Zi + Zo)
        SWR = (1 + abs(Gamma)) / (1 - abs(Gamma))
        print("SWR Relative to 50+j0 Ω Load: {0:.1f}:1".format(SWR))
    elif action == 'p': # Print Circuit
        printcircuit(circuit)
    elif action == 'x': # Clear Circuit
        circuit = []
        print("Network cleared.")
    elif action == 'h': # Help
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
        config = False # Shunt transmission lines? What was I thinking?
        print("Adding series transmission line...")
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
