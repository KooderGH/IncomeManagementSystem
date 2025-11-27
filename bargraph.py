#CODE BY KIAN 
import matplotlib, numpy
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as w

Windows = w.Tk()
Windows.geometry('600x500')
Windows.title('Income')

f, ax = plt.subplots()

data = (21, 41, 35, 67)
bar_colors = ['skyblue', 'skyblue', 'red', 'red']
ind = numpy.arange(4)
width = .4

bar1 = ax.bar(ind, data, width, color=bar_colors)

ax.set_ylabel('Amount')
ax.set_title('Income Data')
ax.set_xticks(ind + width / 20)
ax.set_xticklabels(('Gross\nIncome', 'Net\nIncome', 'Gross\nIncome', 'Net\nIncome'))

canvas = FigureCanvasTkAgg(f, master=Windows)
canvas.draw()
canvas.get_tk_widget().pack(side=w.TOP, fill=w.BOTH, expand=1)

w.mainloop()
