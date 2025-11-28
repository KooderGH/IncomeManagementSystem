#Written By: cedrick
from tkinter import *
from customtkinter import *
from tkinter.ttk import Combobox
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkcalendar import DateEntry
import numpy as np
import matplotlib.figure as mfig

root = Tk()
#MAINWINDOW Details
    #root.grid_propagate(False)
root.geometry("1080x720")
root.minsize(800,600)
ic0n = PhotoImage(file='coin.png')
root.iconphoto(True, ic0n)
root.title("Income Management System")

#SHARED FUNCTIONS
varTimeSpan = StringVar()
def validate_amount(text):
    if text == "":
        return True
    # Accept numbers or decimal numbers
    return text.replace(".", "", 1).isdigit()
vcmd = (root.register(validate_amount), "%P")



#MENU FUNCTIONS



#EXPENSE FUNCTIONS
expense_data = []
expEnt_menu = Menu(root, tearoff=0)
expEnt_menu.add_command(label="Delete Entry")
def addExpense():
    catExp = Entry(ExpList,font=("Calibri", 12),relief=SUNKEN,borderwidth=1)
    amtExp = Entry(ExpList,font=("Calibri", 12),relief=SUNKEN,borderwidth=1,
                   validate='key',validatecommand=vcmd)
    rowexp = len(expense_data)
    catExp.grid(row=rowexp,column=0,sticky=NSEW)
    amtExp.grid(row=rowexp,column=1,sticky=NSEW)
    expEnt_record = {"category": catExp,"amount": amtExp}
    expense_data.append(expEnt_record)
    catExp.bind("<Button-3>", lambda event, rec=expEnt_record: open_expEnt_menu(event, rec))
#amount = float(amount_str) if amount_str else 0 (converting amount_str to float)
def open_expEnt_menu(event, record):
    expEnt_menu.entryconfigure(0, command=lambda: delete_exp_row(record))
    expEnt_menu.tk_popup(event.x_root, event.y_root)
def delete_exp_row(record):
    record["category"].grid_forget()
    record["amount"].grid_forget()
    expense_data.remove(record)
    for i, rec in enumerate(expense_data):
        rec["category"].grid(row=i, column=0, sticky=NSEW)
        rec["amount"].grid(row=i, column=1, sticky=NSEW)


#INCOME FUNCTIONS
income_data = []
incEnt_menu = Menu(root, tearoff=0)
incEnt_menu.add_command(label="Delete Entry")
def addIncome():
    catInc = Entry(IncList,font=("Calibri", 12),relief=SUNKEN,borderwidth=1)
    amtInc = Entry(IncList,font=("Calibri", 12),relief=SUNKEN,borderwidth=1,
                   validate='key',validatecommand=vcmd)
    rowinc = len(income_data)
    catInc.grid(row=rowinc,column=0,sticky=NSEW)
    amtInc.grid(row=rowinc,column=1,sticky=NSEW)
    incEnt_record = {"category": catInc,"amount": amtInc}
    income_data.append(incEnt_record)
    catInc.bind("<Button-3>", lambda event, rec=incEnt_record: open_incEnt_menu(event, rec))
#amount = float(amount_str) if amount_str else 0 (converting amount_str to float)
def open_incEnt_menu(event, record):
    incEnt_menu.entryconfigure(0, command=lambda: delete_inc_row(record))
    incEnt_menu.tk_popup(event.x_root, event.y_root)
def delete_inc_row(record):
    record["category"].grid_forget()
    record["amount"].grid_forget()
    income_data.remove(record)
    for i, rec in enumerate(income_data):
        rec["category"].grid(row=i, column=0, sticky=NSEW)
        rec["amount"].grid(row=i, column=1, sticky=NSEW)



#COMPARISON(LINE-CHART) FUNCTIONS
#def lineGraph():
    #body

#Main Menu
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
DateRel = Frame(ExpFrame,bg="gray")
NextPrev = Frame(IncFrame,bg="green")
ExpFrame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
ExpFrame.grid_columnconfigure((0, 1), weight=1)
IncFrame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
IncFrame.grid_columnconfigure((0, 1), weight=1)
LineFrame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
LineFrame.grid_columnconfigure((0, 1), weight=1)
DateRel.grid(row=2,column=0,columnspan=2,padx=4,pady=4,sticky=S)
DateRel.grid_rowconfigure(0,weight=1)
NextPrev.grid(row=2,column=0,columnspan=2,sticky=S)
NextPrev.grid_rowconfigure(0,weight=1)

#Expense Frame Widgets
LabelEx1 = Label(ExpFrame,text='Expenses:',font=("Calibri", 14))
CanvChartExp = Canvas(ExpFrame,bg='pink')
ExpList = Frame(ExpFrame,bg="yellow",height=200,relief=SUNKEN,borderwidth=2)
addExp = Button(ExpFrame,text='Add Expense',font=("Calibri", 14), command=addExpense)
chartE = Button(ExpFrame,text='Generate Chart',font=("Calibri", 14))
LabelEx1.grid(row=0,column=0,sticky=NSEW)
CanvChartExp.grid(row=1,column=0,columnspan=2,padx=10,pady=10,sticky=NSEW)
ExpList.grid(row=3,column=0,columnspan=2,padx=10,pady=10,sticky=NSEW)
addExp.grid(row=4,column=0,padx=5,pady=5,sticky=NSEW)
chartE.grid(row=4,column=1,padx=5,pady=5,sticky=NSEW)

#Date Related Elements
DateSelct  = DateEntry(DateRel,font=('Arial',12),selectmode='date',year=2025,month=11,day=22)
TimeSpanSel = Combobox(DateRel,font=('Arial',12),
                      textvariable=varTimeSpan,
                      values=['Weeks','Months','Years'],
                      state='readonly')
varTimeSpan.set("Weeks")
TimeSpanSel.bind("<<ComboboxSelected>>")
DateSelct.bind("<<DateEntryClicked>>", lambda e: position_cal_up(DateSelct))
DateSelct.pack(side=LEFT)
TimeSpanSel.pack(side=LEFT)

#Income Frame Widgets
LabelIn1 = Label(IncFrame,text='Income Source(s):',font=("Calibri", 14))
CanvChartInc = Canvas(IncFrame,bg='pink')
calInc = DateEntry(IncFrame, selectmode="date",year=2025,month=11,day=22)
IncList = Frame(IncFrame,bg="yellow",width=200,height=200,relief=SUNKEN,borderwidth=2)
    #NetLabel= Label(IncList, text='Net Income:{}',relief=RAISED,font=("Calibri", 12))
addInc = Button(IncFrame,text='Add Income',font=("Calibri", 14),command=addIncome)
chartI = Button(IncFrame,text='Generate Graph',font=("Calibri", 14))
LabelIn1.grid(row=0,column=0,sticky=N)
CanvChartInc.grid(row=1,column=0,columnspan=2,padx=10,pady=10,sticky=NSEW)
IncList.grid(row=3,column=0,columnspan=2,padx=10,pady=10,sticky=NSEW)
addInc.grid(row=4,column=0,padx=5,pady=5,sticky=NSEW)
chartI.grid(row=4,column=1,padx=5,pady=5,sticky=NSEW)

#NextPrev-Button Frame
NextTP = Button(NextPrev,text='  Next Timespan  ',font=("Calibri", 12))
PrevTp = Button(NextPrev,text='Previous Timespan',font=("Calibri", 12))
NextTP.pack(side=LEFT)
PrevTp.pack(side=LEFT)

#LineGraph Frame Widgets
LabelLin1 = Label(LineFrame,text='Expense vs Income over a period of time:',font=("Calibri", 14))
CanvChartLine = Canvas(LineFrame,bg='pink')
chartL = Button(LineFrame,text='Generate Graph',font=("Calibri", 14))
grossTotal = Frame(LineFrame,bg="yellow",width=200,height=100,relief=SUNKEN,borderwidth=2)
expTotal = Frame(LineFrame,bg="yellow",width=200,height=100,relief=SUNKEN,borderwidth=2)
netTotal = Frame(LineFrame,bg="yellow",width=200,height=100,relief=SUNKEN,borderwidth=2)
LabelLin1.grid(row=0,column=0,columnspan=2,sticky=N)
CanvChartLine.grid(row=1,column=0,columnspan=2,padx=10,pady=10,sticky=NSEW)
chartL.grid(row=2,column=0,columnspan=2,sticky=N)
grossTotal.grid(row=3,column=0,columnspan=2,sticky=N)
expTotal.grid(row=4,column=0,columnspan=2,sticky=N)
netTotal.grid(row=5,column=0,columnspan=2,sticky=N)




root.mainloop()