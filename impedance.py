from math import pi as pi


def radToDeg(v):
    return 180.0*v/pi

def parallel(Z1,Z2):
    return 1.0/(1.0/Z1 + 1.0/Z2)

def series(Z1,Z2):
    return Z1 + Z2

class Component(object):
    def __init__(self, value, name=''):
        self.value = value
        self.name = name
    def Z(self,f):
        """Override this function."""

class Capacitor(Component):
    def Z(self,f):
        return complex(0,-1.0/(2*pi*f*self.value))

class Resistor(Component):
    def Z(self,f):
        return complex(self.value,0)


class Circuit(object):

    """ Base class. """

    def __init__(self, name):
        """init class"""
        self.name = name

    def Z_tot(self):
        """Should override this function"""


class HEMTCircuit(Circuit):
    def __init__(self,name, Rg=1e12, Cgs=100e-12):
        super(HEMTCircuit, self).__init__(name)
        self.Rg = Resistor(Rg,'Rg')
        self.Cgs = Capacitor(Cgs,'Cgs)')
        
    def Z_tot(self, freq):
        # gate to source resistance and gate to source capacitance in parallel
        Zt = parallel(self.Rg.Z(freq), self.Cgs.Z(freq))
        return Zt
    

class OpAmp(Circuit):
    def __init__(self,name, Rfb=1e20, Cfb=20e-12):
        super(OpAmp, self).__init__(name)
        self.Rfb = Resistor(Rfb,'Rfb')
        self.Cfb = Capacitor(Cfb,'Cfb)')

    def Z_fb(self, freq):
        Z = parallel(self.Rfb.Z(freq), self.Cfb.Z(freq))
        return Z

    def Z_tot(self, freq):
        return 0
    

class BJT(Circuit):
    def __init__(self,name):
        super(BJT, self).__init__(name)

    def Z_tot(self, freq):
        return 0
    

        


class ChargeCircuit(Circuit):

    """Description of charge circuit for ionization readout for SCDMS."""

    def __init__(self, name, Cdet=200.0e-12, Rbias=100e6, Rbleed=100e6, Cc=10e-9, Ccg=10e-12, Cfb=1e-12, Rfb=400e6, Rmirror=1e2, HEMT=None, opamp=None, bjt=None):
        """init class"""
        super(ChargeCircuit, self).__init__(name)
        self.Cdet = Capacitor(Cdet, 'Cdet')
        self.Rbias = Resistor(Rbias, 'Rbias')
        self.Rbleed = Resistor(Rbleed, 'Rbleed')
        # coupling capacitor to the HEMT gate at 4K
        self.Ccg = Capacitor(Ccg, 'Ccg')
        # coupling capacitor to the coax wire at MC stage
        self.Cc = Capacitor(Cc, 'Cc')
        self.Cfb = Capacitor(Cfb, 'Cfb')
        self.Rfb = Resistor(Rfb, 'Rfb')
        self.Rmirror = Resistor(Rmirror,'Rmirror')
        if not opamp:
            self.opamp = OpAmp('OpAmp')
        if not HEMT:
            self.HEMT = HEMTCircuit('HEMT')
        if not bjt:
            self.bjt = BJT('BJT')
    
    def Z_MC1(self, freq):
        """Impendance of circuitry at on lower coax PCB at MC stage."""

        # bias and detector are in parallel
        Z1 = parallel(self.Rbias.Z(freq), self.Cdet.Z(freq))

        # Z1 in series with coupling capacitor
        Z2 = series(Z1, self.Cc.Z(freq))

        #Z2 in parallel with bleed resistor
        Z3 = parallel(Z2,self.Rbleed.Z(freq))

        return Z3

    def Z1_tot(self,freq):
        """Impedance from MC stage and HEMT."""
        # impedance at 4K
        Z1_4K = series(self.Z_MC1(freq), self.Ccg.Z(freq))
        # in parallel to HEMT impedance
        Z1 = parallel(self.Z_HEMT(freq),Z1_4K)
        return Z1

    def Z_HEMT(self, freq):
        """Impedance of HEMT circuit"""
        return self.HEMT.Z_tot(freq)

    def Z_fb(self, freq):
        """Impedance of feedback cap and resistor network."""
        Z = parallel(self.Cfb.Z(freq), self.Rfb.Z(freq))
        return Z

    def Z6(self, freq):
        """Impedance of opamp feedback network."""
        Z = self.opamp.Z_fb(freq)
        return Z

    def Z5(self, freq):
        """Impedance of opamp comparator bias network."""
        C118 = Capacitor(100e-9,'C118')
        R115 = Resistor(3.3e3,'R115')
        R114 = Resistor(3.3e3,'R114')
        R1140 = Resistor(1e3,'R1140')
        Z1 = parallel(R114.Z(freq),R115.Z(freq))
        Z2 = parallel(Z1,C118.Z(freq))
        Z = series(R1140.Z(freq), Z2)
        return Z3


    def Z3(self, freq):
        """Impedance of pole cancellation network."""
        C1120 = Capacitor(10e-9,'C1120')
        R113 = Resistor(1.6e3,'R113')
        R1110 = Resistor(1e2,'R1110')
        Z1 = series(R1110.Z(freq), C1120.Z(freq))
        Z = parallel(Z1, R113.Z(freq))
        return Z

    def Z4(self, freq):
        """Impedance of load resistance in current mirror."""
        return self.Rmirror.Z(freq)


    def Z_BJT(self,freq):
        """Impedance of BJT mirror."""
        return self.BJT.Z_tot(freq)


    def Z_tot(self, freq):
        return 0.


    

    
