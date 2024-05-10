from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from .BaseClassPage import *
from .widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu, NumberInput

from .widgets.DynamicSettingsWidget import DynamicSettingsWidget

import pyqtgraph as pg
import numpy as np

class PlotterPage(BaseClassPage):
    
    title = "Plotter Page"

    def initUI(self, layout):

        self.dynamicSettings = DynamicSettingsWidget(
            paramList=self.model.parameters, 
            title="Plot Settings",
            on_edit=self.compute)
        
        
        # Set waveform plotter
        self.plotLayout = pg.GraphicsLayoutWidget(show=True)
        self.wavePlot = []
        self.wavePlot.append(self.plotLayout.addPlot(row=0, col=0))
        self.wavePlot.append(self.plotLayout.addPlot(row=0, col=1))


        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dynamicSettings)
        topHLayout.addWidget(self.plotLayout)

        self.compute()

        # Add widgets to page layout
        layout.addLayout(topHLayout)


    # Synthesize a sound using the selected instrument and effect
    def compute(self):

        for i in range(len(self.wavePlot)):
            self.wavePlot[i].clear()

            # set grid
            self.wavePlot[i].showGrid(x=True, y=True)

        x, y, z, p = self.model.function(self.model.parameters)

        self.wavePlot[0].plot(x, y)

        # fix aspect ratio of plot 1
        self.wavePlot[1].setAspectLocked(True)

        # Plot poles and zeros
        self.wavePlot[1].plot(np.real(z), np.imag(z), pen=None, symbol='o', symbolPen='cyan', symbolBrush='cyan', symbolSize=10, zorder=1)
        self.wavePlot[1].plot(np.real(p), np.imag(p), pen=None, symbol='x', symbolPen='r', symbolBrush='r', symbolSize=15, zorder=1)

        # Plot unit circle
        w = np.linspace(0, np.pi*2, 300)
        self.wavePlot[1].plot(np.cos(w), np.sin(w), pen='w')

        # plot pole circle dashed
        ro = self.model.parameters["ro"]
        pen = pg.mkPen(color='g', width=0.5, style=Qt.DashLine)
        self.wavePlot[1].plot(ro * np.cos(w), ro * np.sin(w), pen=pen)
        
