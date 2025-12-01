# Written By: cedrick (debugged)
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkcalendar import DateEntry
from datetime import *
import calendar
import numpy as np

root = Tk()
# MAINWINDOW Details`
root.geometry("1080x720")
root.minsize(1080,720)
try:
    ic0n = PhotoImage(file='coin.png')
    root.iconphoto(True, ic0n)
except Exception:
    pass
root.title("Income Management System")

# SHARED FUNCTIONS, CLASSES, & VARIABLES
totals_by_span = {
    'Weeks': [],
    'Months': [],
    'Years': []
}
expense_data = []
income_data = []
lineChart = None
DateSelct = None

varTimeSpan = StringVar()
startDate = StringVar()
netInc_data = []

def validate_amount(text):
    if text == "":
        return True
    return text.replace(".", "", 1).isdigit()   
vcmd = (root.register(validate_amount), "%P")

class ScrollFrame(Frame):
    def __init__(self, container, height=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        if height is not None:
            self.configure(height=height)
            self.pack_propagate(False)
        self.canvas = Canvas(self, highlightthickness=0)
        self.vscroll = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.scrollable_frame = Frame(self.canvas)
        self._window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            canvas_width = event.width
            self.canvas.itemconfig(self._window_id, width=canvas_width)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

class PieChart:
    def __init__(self, parent_frame, expense_data):
        self.parent_frame = parent_frame
        self.expense_data = expense_data
        self.canvas_widget = None
        self.toolbar = None

    def render(self):
        # destroy existing
        if self.canvas_widget:
            try:
                self.canvas_widget.get_tk_widget().destroy()
            except Exception:
                pass
            self.canvas_widget = None
        if self.toolbar:
            try:
                self.toolbar.destroy()
            except Exception:
                pass
            self.toolbar = None
        plt.close('all')

        self.parent_frame.update_idletasks()
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        labels = []
        amounts = []
        total_expense = 0
        for record in self.expense_data:
            cat = record["category"].get().strip()
            amt_str = record["amount"].get().strip()
            if cat != "" and amt_str.replace(".", "", 1).isdigit():
                amt = float(amt_str)
                labels.append(cat)
                amounts.append(amt)
                total_expense += amt

        totExp.config(text=f"Total Expenses: {total_expense:.2f}")

        if not amounts:
            ax.text(0.5, 0.5, 'No data to display', ha='center', va='center')
        else:
            ax.pie(amounts, labels=labels, autopct='%1.1f%%')
            ax.set_title("Expense Distribution")

        # pack the canvas and toolbar (stable placement)
        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.parent_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, self.parent_frame)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, fill=X)

class BarChart:
    def __init__(self, parent_frame, income_data, expense_data):
        self.parent_frame = parent_frame
        self.income_data = income_data
        self.expense_data = expense_data
        self.canvas_widget = None
        self.toolbar = None

    def render(self):
        # destroy existing
        if self.canvas_widget:
            try:
                self.canvas_widget.get_tk_widget().destroy()
            except Exception:
                pass
            self.canvas_widget = None
        if self.toolbar:
            try:
                self.toolbar.destroy()
            except Exception:
                pass
            self.toolbar = None
        plt.close('all')

        self.parent_frame.update_idletasks()
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        labels = []
        amounts = []
        total_income = 0
        for record in self.income_data:
            cat = record["category"].get().strip()
            amt_str = record["amount"].get().strip()
            if cat != "":
                try:
                    amt = float(amt_str)
                    labels.append(cat)
                    amounts.append(amt)
                    total_income += amt
                except ValueError:
                    pass

        total_expense = sum(float(rec["amount"].get() or 0) for rec in self.expense_data if rec["amount"].get().replace(".", "", 1).isdigit())
        netInc.config(text=f"Net Income: {total_income - total_expense:.2f}")

        if labels and amounts:
            ind = np.arange(len(amounts))
            ax.bar(ind, amounts, width=0.5)
            ax.set_ylabel("Amount")
            ax.set_title("Income Overview")
            ax.set_xticks(ind)
            ax.set_xticklabels(labels, rotation=45, ha="right")
        else:
            ax.text(0.5, 0.5, "No data to display", ha="center", va="center")

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.parent_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, self.parent_frame)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, fill=X)

class LineChart:
    def __init__(self, parent_frame, totals_by_span):
        self.parent_frame = parent_frame
        self.totals_by_span = totals_by_span
        self.canvas_widget = None
        self.toolbar = None

    def render(self, data_list=None):
        """Render the line chart with all saved timespans, labeled Week/Month/Year."""
        # Destroy existing canvas/toolbar
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        plt.close('all')

        if not data_list:
            fig = Figure(figsize=(4,3), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data to display", ha='center', va='center')
        else:
            fig = Figure(figsize=(4,3), dpi=100)
            ax = fig.add_subplot(111)

            # Prepare X-axis labels
            span_counters = {"Weeks":0, "Months":0, "Years":0}
            x_labels, gross_values, expense_values, net_values = [], [], [], []

            for entry in data_list:
                span_type = entry.get("span_type", "Unknown")
                span_counters[span_type] += 1
                label = f"{span_type[:-1]} {span_counters[span_type]}"  # Week 1, Month 1, Year 1
                x_labels.append(label)
                gross_values.append(entry["income"])
                expense_values.append(entry["expense"])
                net_values.append(entry["net"])

            ind = np.arange(len(data_list))
            ax.plot(ind, gross_values, marker='o', label='Gross Income', color='green')
            ax.plot(ind, expense_values, marker='o', label='Expenses', color='red')
            ax.plot(ind, net_values, marker='o', label='Net Income', color='blue')

            ax.set_xticks(ind)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
            ax.set_xlabel("Timespan")
            ax.set_ylabel("Amount")
            ax.set_title("Income vs Expenses Over Time")
            ax.grid(True)
            ax.legend()
            ax.margins(x=0.05)

        # Pack canvas and toolbar
        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.parent_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, self.parent_frame)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, fill=X)







# DATE RELATED 
current_timespan = StringVar(value="Week")
def set_default_date():
    today = datetime.today().strftime("%Y-%m-%d")
    try:
        DateSelct.delete(0, "end")
        DateSelct.insert(0, today)
    except Exception:
        try:
            DateSelct.set_date(datetime.today())
        except Exception:
            pass

def unlock_date():
    DateSelct.config(state="normal")

def dateSelect(event):
    DateSelct.config(state="normal")

# MENU FUNCTIONS (left as placeholder)
# EXPENSE FUNCTIONS
menu_expEnt = Menu(root, tearoff=0)
menu_expEnt.add_command(label="Delete Entry")

def addExpense():
    parent = ExpScrollFrame.scrollable_frame
    parent.grid_columnconfigure((0,1), weight=1)
    catExp = Entry(parent, font=("Calibri", 12), relief=SUNKEN, borderwidth=1)
    amtExp = Entry(parent, font=("Calibri", 12), relief=SUNKEN, borderwidth=1,
                   validate='key', validatecommand=vcmd)
    rowexp = len(expense_data)
    catExp.grid(row=rowexp, column=0, sticky="nsew", padx=2, pady=2)
    amtExp.grid(row=rowexp, column=1, sticky="nsew", padx=2, pady=2)
    expEnt_record = {"category": catExp, "amount": amtExp}
    expense_data.append(expEnt_record)
    catExp.bind("<Button-3>", lambda event, rec=expEnt_record: expEnt_menu(event, rec))
    catExp.focus_set()
    DateSelct.config(state="disabled")

def expEnt_menu(event, record):
    menu_expEnt.entryconfigure(0, command=lambda: deleteExp_row(record))
    menu_expEnt.tk_popup(event.x_root, event.y_root)

def deleteExp_row(record):
    try:
        record["category"].grid_forget()
        record["amount"].grid_forget()
        expense_data.remove(record)
        for i, rec in enumerate(expense_data):
            rec["category"].grid(row=i, column=0, sticky=NSEW)
            rec["amount"].grid(row=i, column=1, sticky=NSEW)
    except Exception:
        pass

def clear_all_expense_fields():
    for rec in expense_data:
        rec["amount"].delete(0, "end")

# INCOME FUNCTIONS
menu_incEnt = Menu(root, tearoff=0)
menu_incEnt.add_command(label="Delete Entry")

def addIncome():
    parent = IncScrollFrame.scrollable_frame
    parent.grid_columnconfigure((0,1), weight=1)
    catInc = Entry(parent, font=("Calibri", 12), relief=SUNKEN, borderwidth=1)
    amtInc = Entry(parent, font=("Calibri", 12), relief=SUNKEN, borderwidth=1,
                   validate='key', validatecommand=vcmd)
    rowinc = len(income_data)
    catInc.grid(row=rowinc, column=0, sticky="nsew", padx=2, pady=2)
    amtInc.grid(row=rowinc, column=1, sticky="nsew", padx=2, pady=2)
    incEnt_record = {"category": catInc, "amount": amtInc}
    income_data.append(incEnt_record)
    catInc.bind("<Button-3>", lambda event, rec=incEnt_record: incEnt_menu(event, rec))
    catInc.focus_set()
    DateSelct.config(state="disabled")

def incEnt_menu(event, record):
    menu_incEnt.entryconfigure(0, command=lambda: deleteInc_row(record))
    menu_incEnt.tk_popup(event.x_root, event.y_root)

def deleteInc_row(record):
    try:
        record["category"].grid_forget()
        record["amount"].grid_forget()
        income_data.remove(record)
        for i, rec in enumerate(income_data):
            rec["category"].grid(row=i, column=0, sticky=NSEW)
            rec["amount"].grid(row=i, column=1, sticky=NSEW)
    except Exception:
        pass

def clear_all_income_fields():
    for rec in income_data:
        rec["amount"].delete(0, "end")

# COMPARISON(LINE-CHART)
def update_totals_tables(span, data_list=None):
    if data_list is None:
        data_list = totals_by_span.get(span, [])
    data_list = sorted(data_list, key=lambda x: x['start_date'])

    # clear the scrollable frames
    for sf in (grosTotSF, expTotSF, netTotSF):
        for widget in sf.scrollable_frame.winfo_children():
            widget.destroy()

    # TOTAL GROSS INCOME per category aggregated across stored timespans
    income_totals = {}
    for rec in data_list:
        for cat, amt in rec.get("income_by_cat", {}).items():
            income_totals[cat] = income_totals.get(cat, 0) + amt

    if income_totals:
        for cat, total_amt in sorted(income_totals.items()):
            Label(
                grosTotSF.scrollable_frame,
                text=f"{cat} | {total_amt:.2f}",
                anchor="w",
                bg="lightgrey"
            ).pack(fill="x")
    else:
        Label(
            grosTotSF.scrollable_frame,
            text="No income categories yet",
            anchor="w",
            bg="lightgrey"
        ).pack(fill="x")

    # TOTAL EXPENSES per category aggregated across stored timespans
    expense_totals = {}
    for rec in data_list:
        for cat, amt in rec.get("expense_by_cat", {}).items():
            expense_totals[cat] = expense_totals.get(cat, 0) + amt

    if expense_totals:
        for cat, total_amt in sorted(expense_totals.items()):
            Label(
                expTotSF.scrollable_frame,
                text=f"{cat} | {total_amt:.2f}",
                anchor="w",
                bg="lightgrey"
            ).pack(fill="x")
    else:
        Label(
            expTotSF.scrollable_frame,
            text="No expense categories yet",
            anchor="w",
            bg="lightgrey"
        ).pack(fill="x")

    # NET INCOME PER STORED TIMESPAN
    overall_net = 0.0
    if data_list:
        for i, rec in enumerate(data_list):
            span_label = f"{span[:-1]} {i+1}"
            net_val = rec.get("net", 0.0)
            overall_net += net_val
            Label(
                netTotSF.scrollable_frame,
                text=f"{span_label} | {net_val:.2f}",
                anchor="w",
                bg="lightgrey"
            ).pack(fill="x")

        Label(
            netTotSF.scrollable_frame,
            text=f"Overall Net | {overall_net:.2f}",
            anchor="w",
            bg="lightgrey",
            font=("Calibri", 10, "bold")
        ).pack(fill="x", pady=(6,0))
    else:
        Label(
            netTotSF.scrollable_frame,
            text="No stored timespans yet",
            anchor="w",
            bg="lightgrey"
        ).pack(fill="x")

def GenResult():
    """Save current timespan data and update line chart & totals across all saved timespans."""
    span = varTimeSpan.get()
    date_str = DateSelct.get()

    # Build income_by_cat and expense_by_cat
    income_by_cat = {}
    for rec in income_data:
        cat = rec["category"].get().strip()
        amt_str = rec["amount"].get().strip()
        if cat and amt_str.replace(".", "", 1).isdigit():
            income_by_cat[cat] = income_by_cat.get(cat, 0) + float(amt_str)

    expense_by_cat = {}
    for rec in expense_data:
        cat = rec["category"].get().strip()
        amt_str = rec["amount"].get().strip()
        if cat and amt_str.replace(".", "", 1).isdigit():
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + float(amt_str)

    total_income = sum(income_by_cat.values())
    total_expense = sum(expense_by_cat.values())
    net_total = total_income - total_expense

    if not income_by_cat and not expense_by_cat:
        messagebox.showinfo("No Data", "No valid entries for this timespan.")
        return

    # Save/update record in totals_by_span
    record = next((r for r in totals_by_span[span] if r["start_date"] == date_str), None)
    record_data = {
        "start_date": date_str,
        "income": total_income,
        "expense": total_expense,
        "net": net_total,
        "income_by_cat": income_by_cat,
        "expense_by_cat": expense_by_cat,
        "span_type": span
    }
    if record:
        record.update(record_data)
    else:
        totals_by_span[span].append(record_data)

    # Clear input fields
    clear_all_income_fields()
    clear_all_expense_fields()
    root.update()

    # Gather all entries across all timespans
    all_entries = []
    for s in ["Weeks", "Months", "Years"]:
        all_entries.extend(totals_by_span[s])
    all_entries.sort(key=lambda x: datetime.strptime(x['start_date'], "%Y-%m-%d"))

    # Update summary tables using all entries
    update_totals_tables(span, data_list=all_entries)

    # Render line chart using all entries
    lineChart.render(data_list=all_entries)






# NEXT & PREV BUTTONS FUNCTIONS
def go_next_timespan():
    GenResult()
    span = varTimeSpan.get()
    current_date = datetime.strptime(DateSelct.get(), "%Y-%m-%d")

    if span == "Weeks":
        next_date = current_date + timedelta(weeks=1)
    elif span == "Months":
        month = current_date.month + 1
        year = current_date.year
        if month > 12:
            month = 1
            year += 1
        last_day = calendar.monthrange(year, month)[1]
        next_date = current_date.replace(day=min(current_date.day, last_day), month=month, year=year)
    else:  # Years
        next_date = current_date.replace(year=current_date.year + 1)

    try:
        DateSelct.set_date(next_date)
    except Exception:
        DateSelct.delete(0, "end")
        DateSelct.insert(0, next_date.strftime("%Y-%m-%d"))

    # Clear fields before prefill
    clear_all_income_fields()
    clear_all_expense_fields()

    # Prefill if record exists
    data_list = totals_by_span.get(span, [])
    record = next((r for r in data_list if r['start_date'] == next_date.strftime("%Y-%m-%d")), None)
    if record:
        for rec in income_data:
            amt = record.get('income_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))
        for rec in expense_data:
            amt = record.get('expense_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))

    # Update chart & totals with all entries
    all_entries = []
    for s in ["Weeks", "Months", "Years"]:
        all_entries.extend(totals_by_span[s])
    all_entries.sort(key=lambda x: datetime.strptime(x['start_date'], "%Y-%m-%d"))
    update_totals_tables(span, data_list=all_entries)
    lineChart.render(data_list=all_entries)


def go_prev_timespan():
    GenResult()
    span = varTimeSpan.get()
    current_date = datetime.strptime(DateSelct.get(), "%Y-%m-%d")

    if span == "Weeks":
        prev_date = current_date - timedelta(weeks=1)
    elif span == "Months":
        month = current_date.month - 1
        year = current_date.year
        if month < 1:
            month = 12
            year -= 1
        last_day = calendar.monthrange(year, month)[1]
        prev_date = current_date.replace(day=min(current_date.day, last_day), month=month, year=year)
    else:  # Years
        prev_date = current_date.replace(year=current_date.year - 1)

    try:
        DateSelct.set_date(prev_date)
    except Exception:
        DateSelct.delete(0, "end")
        DateSelct.insert(0, prev_date.strftime("%Y-%m-%d"))

    # Clear fields before prefill
    clear_all_income_fields()
    clear_all_expense_fields()

    # Prefill if record exists
    data_list = totals_by_span.get(span, [])
    record = next((r for r in data_list if r['start_date'] == prev_date.strftime("%Y-%m-%d")), None)
    if record:
        for rec in income_data:
            amt = record.get('income_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))
        for rec in expense_data:
            amt = record.get('expense_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))

    # Update chart & totals with all entries
    all_entries = []
    for s in ["Weeks", "Months", "Years"]:
        all_entries.extend(totals_by_span[s])
    all_entries.sort(key=lambda x: datetime.strptime(x['start_date'], "%Y-%m-%d"))
    update_totals_tables(span, data_list=all_entries)
    lineChart.render(data_list=all_entries)



# -v-v-v-v- GUI -v-v-v-
# Main Menu
Menubar = Menu(root, relief=RAISED, borderwidth=1)
root.config(menu=Menubar)
fileMenu = Menu(Menubar, tearoff=0)
Menubar.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="Open", command=lambda: None)
fileMenu.add_command(label="Save", command=lambda: None)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=root.quit)

# TITLE-BAR FRAME
Titlebar = Frame(root, bg="white")
Titlebar.place(x=0, y=0, relwidth=1, height=35)
SysTitle = Label(
    Titlebar,
    text="Income Management System",
    font=("Calibri", 25, "bold"),
    fg="black",
    bg="white",
    padx=5, pady=5
)
SysTitle.pack(side=TOP, fill=X)

# MAIN FRAME
mainFrame = Frame(root, bg="white")
mainFrame.place(x=0, y=35, relwidth=1, relheight=1, anchor=NW)
mainFrame.grid_columnconfigure((0, 1, 2), weight=1)
mainFrame.grid_rowconfigure(0, weight=1)

# Sub-Frames
ExpFrame = Frame(mainFrame, bg="white")
IncFrame = Frame(mainFrame, bg="white")
LineFrame = Frame(mainFrame, bg="white")
DateRel = Frame(ExpFrame, bg="lightgrey")
NextPrev = Frame(IncFrame, bg="lightgrey")
ExpFrame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
ExpFrame.grid_columnconfigure((0, 1), weight=1)
IncFrame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
IncFrame.grid_columnconfigure((0, 1), weight=1)
LineFrame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
LineFrame.grid_columnconfigure((0, 1), weight=1)
DateRel.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky=S)
NextPrev.grid(row=2, column=0, columnspan=2, sticky=S)

# EXPENSE FRAME WIDGETS
LabelEx1 = Label(ExpFrame, text='Expenses:', font=("Calibri", 14), bg="white")
ChartExp = Frame(ExpFrame, bg='lightgrey', width=300, height=300)
ChartExp.pack_propagate(False)
pieChart = PieChart(ChartExp, expense_data)
ExpListCont = Frame(ExpFrame, bg="lightgrey", width=200, height=150, relief=SUNKEN, borderwidth=2)
ExpListCont.grid_propagate(False)
ExpScrollFrame = ScrollFrame(ExpListCont, height=150)
ExpScrollFrame.scrollable_frame.config(bg="lightgrey")
totExp = Label(ExpListCont, text='Total Expenses: ', font=("Calibri", 14), bg="lightgrey")
addExp = Button(ExpFrame, text='Add Expense', font=("Calibri", 14), command=addExpense)
chartE = Button(ExpFrame, text='Generate Chart', font=("Calibri", 14))
LabelEx1.grid(row=0, column=0, sticky=N)
ChartExp.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
ExpListCont.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
ExpScrollFrame.pack(fill="both", expand=True)
totExp.pack(fill="both", expand=True)
addExp.grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
chartE.grid(row=4, column=1, padx=5, pady=5, sticky=NSEW)
chartE.config(command=pieChart.render)

# Date Related Elements
DateSelct = DateEntry(DateRel, font=('Arial', 12), selectmode='day', year=2025, month=11, day=22)
TimeSpanSel = Combobox(DateRel, font=('Arial', 12),
                       textvariable=varTimeSpan,
                       values=['Weeks', 'Months', 'Years'],
                       state='readonly')
varTimeSpan.set("Weeks")
TimeSpanSel.bind("<<ComboboxSelected>>", lambda e: GenResult())
DateSelct.bind("<<DateEntrySelected>>", dateSelect)
set_default_date()
DateSelct.pack(side=LEFT)
TimeSpanSel.pack(side=LEFT)

# INCOME FRAME WIDGETS
LabelIn1 = Label(IncFrame, text='Income Source(s):', font=("Calibri", 14), bg="white")
ChartInc = Frame(IncFrame, bg='lightgrey', width=300, height=300)
ChartInc.pack_propagate(False)
barChart = BarChart(ChartInc, income_data, expense_data)
IncListCont = Frame(IncFrame, bg="lightgrey", width=200, height=150, relief=SUNKEN, borderwidth=2)
IncListCont.grid_propagate(False)
IncScrollFrame = ScrollFrame(IncListCont, height=150)
IncScrollFrame.scrollable_frame.config(bg="lightgrey")
netInc = Label(IncListCont, text='Net Income: ', font=("Calibri", 14), bg="lightgrey")
addInc = Button(IncFrame, text='Add Income', font=("Calibri", 14), command=addIncome)
chartI = Button(IncFrame, text='Generate Graph', font=("Calibri", 14))
LabelIn1.grid(row=0, column=0, sticky=N)
ChartInc.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
IncListCont.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
IncScrollFrame.pack(fill="both", expand=True)
netInc.pack(fill="both", expand=True)
addInc.grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
chartI.grid(row=4, column=1, padx=5, pady=5, sticky=NSEW)
chartI.config(command=barChart.render)

# NEXT & PREV BUTTONS
NextTP = Button(NextPrev, text='  Next Timespan  ', font=("Calibri", 12), command=go_next_timespan)
PrevTp = Button(NextPrev, text='Previous Timespan', font=("Calibri", 12), command=go_prev_timespan)
NextTP.pack(side=LEFT)
PrevTp.pack(side=LEFT)

# LINE CHART FRAME WIDGETS
LabelLin1 = Label(LineFrame, text='Expense vs Income over a period of time:', font=("Calibri", 14), bg="white")
ChartLine = Frame(LineFrame, bg='lightgrey', width=300, height=300)
ChartLine.pack_propagate(False)
genbutt_Frame = Frame(LineFrame, bg="white")
lineChart = LineChart(ChartLine, totals_by_span)
genResult = Button(genbutt_Frame, text='Compare', font=("Calibri", 14))
genResult.config(command=GenResult)
grosTotCont = Frame(LineFrame, bg="lightgrey", width=250, height=60, relief=SUNKEN, borderwidth=2)
grosTotCont.grid_propagate(False)
grosTotSF = ScrollFrame(grosTotCont, height=60)
grosTotSF.scrollable_frame.config(bg="lightgrey")
grossTotal = Label(grosTotCont, text='Total Gross Income: ', font=("Calibri", 12), bg="lightgrey")
expTotCont = Frame(LineFrame, bg="lightgrey", width=250, height=60, relief=SUNKEN, borderwidth=2)
expTotCont.grid_propagate(False)
expTotSF = ScrollFrame(expTotCont, height=60)
expTotSF.scrollable_frame.config(bg="lightgrey")
expTotal = Label(expTotCont, text='Total Expense: ', font=("Calibri", 12), bg="lightgrey")
netTotCont = Frame(LineFrame, bg="lightgrey", width=250, height=60, relief=SUNKEN, borderwidth=2)
netTotCont.grid_propagate(False)
netTotSF = ScrollFrame(netTotCont, height=60)
netTotSF.scrollable_frame.config(bg="lightgrey")
netTotal = Label(netTotCont, text='Total Net Income: ', font=("Calibri", 12), bg="lightgrey")
LabelLin1.grid(row=0, column=0, columnspan=2, sticky=N)
ChartLine.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
genbutt_Frame.grid(row=2, column=0, columnspan=2, padx=5, pady=2.5, sticky=NSEW)
genResult.pack(side=TOP)
grosTotCont.grid(row=3, column=0, columnspan=2, padx=10, sticky=NSEW)
grosTotSF.pack(fill="both", expand=True)
grossTotal.pack(fill="both", expand=True)
expTotCont.grid(row=4, column=0, columnspan=2, padx=10, sticky=NSEW)
expTotSF.pack(fill="both", expand=True)
expTotal.pack(fill="both", expand=True)
netTotCont.grid(row=5, column=0, columnspan=2, padx=10, sticky=NSEW)
netTotSF.pack(fill="both", expand=True)
netTotal.pack(fill="both", expand=True)

root.mainloop()
