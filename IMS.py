# Written by Kenn
from tkinter import *
from tkinter.ttk import Combobox
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkcalendar import *
import numpy as np
import matplotlib.figure as mfig

root = Tk()
#SHARED FUNCTIONS
varTimeSpan = StringVar()



#MENU FUNCTIONS



#EXPENSE FUNCTIONS
#def pieChart():
    #body


#INCOME FUNCTIONS
#def barGraph():
    #body


#COMPARISON(LINE-CHART) FUNCTIONS
#def lineGraph():
    #body

#mAINWINDOW Details
root.geometry("1080x720")
root.minsize(800,600)
ic0n = PhotoImage(file='coin.png')
root.iconphoto(True, ic0n)
root.title("Income Management System")

#Main Menu VVV
Menubar = Menu(root, relief=RAISED, borderwidth=1)
root.config(menu=Menubar)
fileMenu = Menu(Menubar, tearoff=0)
Menubar.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="Open", command='doNothing')
fileMenu.add_command(label="Save", command='doNothing')
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=root.quit)

#Title-Bar Frame
Titlebar = Frame(root)
Titlebar.place(x=0,y=0,relwidth=1,h=35)
SysTitle = Label(Titlebar,
               text="Income Management System",
               font=("Calibri", 25, "bold"),
               fg="black",
               padx=5,pady=5,
               compound='bottom').pack(side=TOP,fill=X)
#MAIN FRAME
mainFrame = Frame(root, bg='blue')
mainFrame.place(x=0,y=35,relwidth=1,relh=1,anchor=NW)
mainFrame.grid_columnconfigure((0, 1, 2), weight=1)
mainFrame.grid_rowconfigure(0, weight=1)
    #3 Sub-Frames + next&prev buttons frame
ExpFrame = Frame(mainFrame,bg="lightblue")
IncFrame = Frame(mainFrame,bg="lightgreen")
LineFrame = Frame(mainFrame,bg="lightcoral")
NextPrev = Frame(IncFrame,bg="green")
ExpFrame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
IncFrame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
LineFrame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
NextPrev.grid(row=7,column=0,columnspan=2,padx=10,pady=10,sticky=S)

#Expense Frame Widgets
CanvChartExp = Canvas(ExpFrame,bg='pink')
LabelEx1 = Label(ExpFrame,text='Expenses:',font=("Calibri", 12))
calExp  = DateEntry(ExpFrame, selectmode="date",year=2025,month=11,day=22)
ExpList = Frame(ExpFrame,
                bg="yellow",width=200,height=200)
addExp = Button(ExpFrame,text='Add-Expense',font=("Calibri", 14))
chartE = Button(ExpFrame,text='Generate Chart',font=("Calibri", 14))
CanvChartExp.grid(row=0,column=0,columnspan=3,padx=10,pady=10,sticky=NSEW)
LabelEx1.grid(row=1,column=0,sticky=N)
ExpList.grid(row=2,column=0,columnspan=3,padx=5,pady=5,sticky=NSEW)
addExp.grid(row=3,column=0,sticky=NSEW)
chartE.grid(row=4,column=0,sticky=NSEW)

#Income Frame Widgets
CanvChartInc = Canvas(IncFrame,bg='pink')
LabelIn1 = Label(IncFrame,text='Income Source(s):',font=("Calibri", 12))
calInc = DateEntry(IncFrame, selectmode="date",year=2025,month=11,day=22)
IncList = Frame(IncFrame,
                bg="yellow",width=200,height=200)
addInc = Button(IncFrame,text='Add Income',font=("Calibri", 14))
chartI = Button(IncFrame,text='Generate Graph',font=("Calibri", 14))
CanvChartInc.grid(row=0,column=0,columnspan=3,padx=10,pady=10,sticky=NSEW)
LabelIn1.grid(row=1,column=0,sticky=N)
IncList.grid(row=2,column=0,columnspan=3,padx=5,pady=5,sticky=NSEW)
addInc.grid(row=3,column=0,sticky=NSEW)
chartI.grid(row=4,column=0,sticky=NSEW)

#NextPrev-Button Frame
NextTP = Button(NextPrev,text='  Next Timespan  ',font=("Calibri", 14))
PrevTp = Button(NextPrev,text='Previous Timespan',font=("Calibri", 14))
TimeSpanSel = Combobox(NextPrev,
                      textvariable=varTimeSpan,
                      values=['Weeks','Months','Years'],
                      state='readonly')
varTimeSpan.set("Weeks")
TimeSpanSel.bind("<<ComboboxSelected>>")
NextTP.pack(side=LEFT)
PrevTp.pack(side=LEFT)
TimeSpanSel.pack(side=LEFT)

#Line-Graph Frame Widgets
CanvChartLine = Canvas(LineFrame,bg='pink')
LabelLin1 = Label(LineFrame,text='Expense vs Income over a period of time:',font=("Calibri", 12))
chartL = Button(LineFrame,text='Generate Graph',font=("Calibri", 14))
grossTotal = Frame(LineFrame,bg="yellow",width=200,height=100,relief=SUNKEN,borderwidth=2)
expTotal = Frame(LineFrame,bg="yellow",width=200,height=100,relief=SUNKEN,borderwidth=2)
netTotal = Frame(LineFrame,bg="yellow",width=200,height=100,relief=SUNKEN,borderwidth=2)
CanvChartLine.grid(row=0,column=0,columnspan=3,padx=10,pady=10,sticky=NSEW)
LabelLin1.grid(row=1,column=0,columnspan=2,sticky=N)
chartL.grid(row=2,column=0,columnspan=2,sticky=N)
grossTotal.grid(row=3,column=0,columnspan=2,sticky=N)
expTotal.grid(row=4,column=0,columnspan=2,sticky=N)
netTotal.grid(row=5,column=0,columnspan=2,sticky=N)




root.mainloop()