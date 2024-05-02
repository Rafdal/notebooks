
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from frontend.PlotterPage import PlotterPage
from frontend.MainWindow import MainWindow

class RTPlotterModel:
    def __init__(self, function, parameters):
        self.function = function
        self.parameters = parameters


class App:
    def __init__(self, function, parameters):
        self.model = RTPlotterModel(function, parameters)

    def run(self):
        self.app = QApplication(sys.argv)
        pages = [
            PlotterPage()
        ]
        ex = MainWindow(pages=pages, model=self.model, title="Real Time Plotter")
        sys.exit(self.app.exec_())


from Parameters import ParameterList, NumParam, BoolParam, ChoiceParam
import numpy as np
import scipy.signal as signal
import sympy as sp

if True:
    parameters = ParameterList(
        ChoiceParam(
            name="type", 
            options=["NotchM", "Notch2", "Resonator"], 
            value="NotchM", 
            text="Filter Type"),
        NumParam(name="size", interval=(0, 10000), step=10, value=1000, text="Points"),
        NumParam(name="wrel", interval=(0, 1), step=0.001, value=0.5, text="w0 / pi"),
        NumParam(name="ro", interval=(0, 0.999), step=0.001, value=0.9, text="ro de los polos"),
        NumParam(name="m", interval=(1, 10), step=1, value=2, text="Orden M"),
        NumParam(name="G", interval=(0, 10), step=0.01, value=1, text="Ganancia"),
    )

    def N(z, nexp):
        return 1 - z**(-int(nexp))
    
    def NotchM(z, ro, M):
        num = N(z, M) * ((1 + ro**M)/2)
        den = N(z / ro, M)
        return num, den
    
    def Notch2(z, R, w0):
        num = 1 - 2 * np.cos(w0) * z**(-1) + z**(-2)
        den = 1 - 2 * R * np.cos(w0) * z**(-1) + R**2 * z**(-2)
        return num, den
    

    def Resonator(z, R, w0):
        num = 1
        den = 1 - 2 * R * np.cos(w0) * z**(-1) + R**2 * z**(-2)
        return num, den


    def function(params):
        size = int(params["size"])
        wrel = params["wrel"]
        ro = params["ro"]
        m = params["m"]
        ftype = params["type"]
        G = params["G"]

        z = sp.Symbol('z')
        w0 = wrel * np.pi

        # Filter type selection
        if ftype == "NotchM":
            num, den = NotchM(z, ro, m)
        elif ftype == "Notch2":
            num, den = Notch2(z, ro, w0)
        elif ftype == "Resonator":
            num, den = Resonator(z, ro, w0)


        num, den = sp.simplify(num / den).expand().simplify().as_numer_denom()

        # Solve for zeros and poles
        zeros = sp.solve(num, z)
        poles = sp.solve(den, z)

        # convert to numpy values
        zeros = np.array([complex(zero) for zero in zeros])
        poles = np.array([complex(pole) for pole in poles])


        # Substitute z values into the function
        H = G * num / den
        H_func = sp.lambdify(z, H, 'numpy')

        # Frequencies
        x = np.linspace(0, 2, size)
        w = np.pi * x
        z_values = np.exp(1j * w)
        H_abs = np.abs(H_func(z_values)) 
        
        return x, H_abs, zeros, poles


    app = App(function, parameters)
    app.run()