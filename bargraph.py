# Written by Kian
import matplotlib.pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from tkinter import *

window = Tk()
window.geometry('500x500')

values = ([50, 100, 150])
categories = ['Source of Income', 'Gross Income', 'Net Income']

def chart():
	fig = Figure(figsize = (5,5), dpi = 100)
	y = [i**2 for i in range(101)]
	chart1 = fig.add_subplot(111)
	chart1.chart(y)

	xpos = np.arange(len(categories))

	matplotlib.pyplot.bar(xpos, values, color=['Gold', 'Gold', 'Gold'])
	matplotlib.pyplot.xlabel('Categories')
	matplotlib.pyplot.ylabel('Values')
	matplotlib.pyplot.title('Income Graph')
	matplotlib.pyplot.xticks(xpos, categories)

	canvas = FigureCanvasTkAgg(fig, master = window)
	canvas.draw()
	canvas.get_tk_widget().pack()
	toolbar = NavigationToolbar2Tk(canvas, window)
	toolbar.update()
	canvas.get_tk_widget().pack()

button = Button(master = window, command = chart,
                height = 2, width = 10, text ='Bar Graph')

button.pack()