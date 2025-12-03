from customUI import *
from tkinter import *
from tkinter.ttk import Combobox
from tkcalendar import DateEntry
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

root = Tk()
root.geometry("1080x720")
root.minsize(1080, 720)
try:
    ic0n = PhotoImage(file='coin.png')
    root.iconphoto(True, ic0n)
except Exception:
    pass
root.title("Income Management System")

class EntryRow:
    def __init__(self, category_entry, amount_entry, date_value=None):
        self.category = category_entry
        self.amount = amount_entry
        self.date = date_value

    def get_category(self):
        try:
            return self.category.get().strip()
        except Exception:
            return ""

    def get_amount(self):
        try:
            raw = (self.amount.get() or "").strip()
            return float(raw) if raw != "" else None
        except Exception:
            try:
                return float(self.amount.get())
            except Exception:
                return None

    def clear(self):
        try:
            self.amount.delete(0, "end")
        except Exception:
            pass

    def destroy(self):
        try:
            self.category.destroy()
        except Exception:
            try:
                self.category.grid_forget()
            except:
                pass
        try:
            self.amount.destroy()
        except Exception:
            try:
                self.amount.grid_forget()
            except:
                pass

class IncomeRow(EntryRow):
    pass

class ExpenseRow(EntryRow):
    pass

class TimespanStore:
    def __init__(self):
        self.totals_by_span = {'Weeks': [], 'Months': [], 'Years': []}
        self.start_date_global = None
        self.date_jump = timedelta(weeks=1)

    def set_mode(self, span_mode):
        if span_mode == "Weeks":
            self.date_jump = timedelta(weeks=1)
        elif span_mode == "Months":
            self.date_jump = relativedelta(months=1)
        elif span_mode == "Years":
            self.date_jump = relativedelta(years=1)
        else:
            self.date_jump = timedelta(weeks=1)

    def compute_span_date(self, span_type, idx):
        if self.start_date_global is None:
            self.start_date_global = date.today()
        base = self.start_date_global
        if idx == 1:
            return base
        if span_type == "Weeks":
            return base + timedelta(weeks=idx - 1)
        elif span_type == "Months":
            return base + relativedelta(months=idx - 1)
        elif span_type == "Years":
            return base + relativedelta(years=idx - 1)
        else:
            return base + timedelta(weeks=idx - 1)

    def save_record(self, span_type, record_date, incomes, expenses):
        if isinstance(record_date, str):
            try:
                record_date = datetime.strptime(record_date, "%Y-%m-%d").date()
            except Exception:
                record_date = date.today()
        if self.start_date_global is None:
            self.start_date_global = record_date

        income_categories = {}
        for e in incomes:
            cat = e["category"]
            income_categories.setdefault(cat, 0)
            income_categories[cat] += e["amount"]

        expense_categories = {}
        for e in expenses:
            cat = e["category"]
            expense_categories.setdefault(cat, 0)
            expense_categories[cat] += e["amount"]

        gross_total = sum(income_categories.values())
        expense_total = sum(expense_categories.values())
        net_total = gross_total - expense_total

        span_list = self.totals_by_span.setdefault(span_type, [])
        idx = len(span_list) + 1

        rec = {
            "index": idx,
            "start_date": record_date.isoformat(),
            "span_type": span_type,
            "income_list": incomes,
            "expense_list": expenses,
            "income_totals": income_categories,
            "expense_totals": expense_categories,
            "gross_total": gross_total,
            "expense_total": expense_total,
            "net_total": net_total
        }
        span_list.append(rec)
        return rec

    def save_to_file(self, filepath):
        if not any(self.totals_by_span.values()):
            raise RuntimeError("No data to save")

        base_date = self.start_date_global or date.today()

        def compute(span_type, idx):
            if span_type == "Weeks":
                return base_date + timedelta(weeks=idx - 1)
            elif span_type == "Months":
                return base_date + relativedelta(months=idx - 1)
            elif span_type == "Years":
                return base_date + relativedelta(years=idx - 1)
            else:
                return base_date + timedelta(weeks=idx - 1)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("INCOME MANAGEMENT SYSTEM REPORT\n")
            f.write("=" * 40 + "\n\n")
            for span_type in ["Weeks", "Months", "Years"]:
                records = self.totals_by_span.get(span_type, [])
                if not records:
                    continue
                f.write(f"=== {span_type.upper()} ===\n\n")
                for idx, rec in enumerate(records, start=1):
                    actual_date = compute(span_type, idx)
                    date_str = actual_date.isoformat()

                    gross = rec.get("gross_total") or 0.0
                    expense = rec.get("expense_total") or 0.0
                    net = rec.get("net_total")
                    if net is None:
                        net = gross - expense

                    f.write(f"{span_type[:-1]} {idx} - Date: {date_str}\n")
                    f.write(f"Gross Income: {float(gross):.2f}\n")
                    f.write(f"Expense Total: {float(expense):.2f}\n")
                    f.write(f"Net Total: {float(net):.2f}\n\n")

                    f.write("  Income by Category:\n")
                    if rec.get("income_totals"):
                        for cat, amt in rec["income_totals"].items():
                            try:
                                f.write(f"    {cat}: {float(amt):.2f}\n")
                            except Exception:
                                f.write(f"    {cat}: {amt}\n")
                    else:
                        il = rec.get("income_list") or []
                        if il:
                            for it in il:
                                f.write(f"    {it.get('category','Unknown')}: {it.get('amount',0)}\n")
                        else:
                            f.write("    (no income categories recorded)\n")

                    f.write("\n  Expense by Category:\n")
                    if rec.get("expense_totals"):
                        for cat, amt in rec["expense_totals"].items():
                            try:
                                f.write(f"    {cat}: {float(amt):.2f}\n")
                            except Exception:
                                f.write(f"    {cat}: {amt}\n")
                    else:
                        el = rec.get("expense_list") or []
                        if el:
                            for it in el:
                                f.write(f"    {it.get('category','Unknown')}: {it.get('amount',0)}\n")
                        else:
                            f.write("    (no expense categories recorded)\n")

                    f.write("\n" + "-" * 40 + "\n\n")

    def reset(self):
        self.totals_by_span = {'Weeks': [], 'Months': [], 'Years': []}
        self.start_date_global = None


store = TimespanStore()
expense_data = []
income_data = []
lineChart = None
DateSelct = None

varTimeSpan = StringVar()
startDate = StringVar()
netInc_data = []

TimespanList = ["Weeks", "Months", "Years"]
current_span_index = 0
IncomeValues = []
ExpenseValues = []

ExpenseCanvas = Frame()
IncomeCanvas = Frame()

def validate_amount(text):
    if text == "":
        return True
    return text.replace(".", "", 1).isdigit()
vcmd = (root.register(validate_amount), "%P")

def add_months(orig_date, months):
    month = orig_date.month - 1 + months
    year = orig_date.year + month // 12
    month = month % 12 + 1
    day = min(orig_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def calculate_next_date(current_date, span_type, step=1):
    if span_type == "Weeks":
        return current_date + timedelta(weeks=step)
    elif span_type == "Months":
        month = current_date.month - 1 + step
        year = current_date.year + month // 12
        month = month % 12 + 1
        day = min(current_date.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    elif span_type == "Years":
        try:
            return date(current_date.year + step, current_date.month, current_date.day)
        except ValueError:
            return date(current_date.year + step, 2, 28)
    return current_date

def prefill_timespan(span, target_date):
    record = next((r for r in store.totals_by_span.get(span, []) if r['start_date'] == target_date.isoformat()), None)
    clear_all_income_fields()
    clear_all_expense_fields()

    if record:
        for rec in income_data:
            cat = rec.get_category()
            amt = record.get('income_totals', {}).get(cat, "")
            if amt != "":
                rec.amount.insert(0, str(amt))

        for rec in expense_data:
            cat = rec.get_category()
            amt = record.get('expense_totals', {}).get(cat, "")
            if amt != "":
                rec.amount.insert(0, str(amt))

def compute_overall_net(all_entries):
    return sum(r.get('income', 0) - r.get('expense', 0) for r in all_entries)

# DATE RELATED
current_timespan = StringVar(value="Week")
current_mode = StringVar(value="Week")

def update_mode(event=None):
    mode = TimeSpanSel.get()
    store.set_mode(mode)
    current_mode.set(mode)

def set_default_date():
    try:
        DateSelct.set_date(date.today())
    except Exception:
        try:
            DateSelct.delete(0, "end")
            DateSelct.insert(0, date.today().isoformat())
        except Exception:
            pass

def unlock_date():
    DateSelct.config(state="normal")

def dateSelect(event):
    DateSelct.config(state="normal")

# MENU FUNCTIONS
def save_as_textFile():
    if not any(store.totals_by_span.values()):
        messagebox.showwarning("No Data", "There is no data to save.")
        return

    from tkinter.filedialog import asksaveasfilename
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Save Income Data"
    )
    if not filepath:
        return

    try:
        store.save_to_file(filepath)
    except Exception as ex:
        messagebox.showerror("Save Error", f"Failed saving file: {ex}")
        return

    messagebox.showinfo("Saved", f"File saved to:\n{filepath}")

def reset_all():
    global lineChart, current_span_index

    store.reset()

    for row in list(income_data):
        try:
            row.destroy()
        except Exception:
            pass
    income_data.clear()

    for row in list(expense_data):
        try:
            row.destroy()
        except Exception:
            pass
    expense_data.clear()

    set_default_date()
    try:
        totExp.config(text="Total Expenses: ")
    except:
        pass
    try:
        netInc.config(text="Net Income: ")
    except:
        pass
    try:
        grossTotal.config(text="Total Gross Income: 0.00")
        expTotal.config(text="Total Expense: 0.00")
        netTotal.config(text="Total Net Income: 0.00")
    except:
        pass

    try:
        for w in ChartExp.winfo_children():
            w.destroy()
    except:
        pass
    try:
        for w in ChartInc.winfo_children():
            w.destroy()
    except:
        pass

    try:
        for w in grosTotSF.scrollable_frame.winfo_children():
            w.destroy()
    except:
        pass
    try:
        for w in expTotSF.scrollable_frame.winfo_children():
            w.destroy()
    except:
        pass
    try:
        for w in netTotSF.scrollable_frame.winfo_children():
            w.destroy()
    except:
        pass

    try:
        if lineChart is not None:
            cw = getattr(lineChart, "canvas_widget", None)
            if cw:
                try:
                    cw.get_tk_widget().destroy()
                except:
                    pass
                try:
                    lineChart.canvas_widget = None
                except:
                    pass
            tb = getattr(lineChart, "toolbar", None)
            if tb:
                try:
                    tb.destroy()
                except:
                    pass
    except:
        pass

    try:
        for w in ChartLine.winfo_children():
            w.destroy()
    except:
        pass

    try:
        lineChart = LineChart(ChartLine, store.totals_by_span)
    except:
        lineChart = None

    messagebox.showinfo("Reset Complete", "All data and charts have been reset.")
    try:
        DateSelct.config(state="readonly")
    except:
        pass
    try:
        TimeSpanSel.config(state="readonly")
    except:
        pass

# EXPENSE & INCOME helpers that use a EntryRow subclass
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
    row = ExpenseRow(catExp, amtExp)
    expense_data.append(row)
    catExp.bind("<Button-3>", lambda event, rec=row: expEnt_menu(event, rec))
    catExp.focus_set()
    try:
        DateSelct.config(state="disabled")
    except Exception:
        pass
    if DateSelct:
        DateSelct.config(state="disabled")
    TimeSpanSel.config(state="disabled")

def expEnt_menu(event, record):
    menu_expEnt.entryconfigure(0, command=lambda: deleteExp_row(record))
    menu_expEnt.tk_popup(event.x_root, event.y_root)

def deleteExp_row(record):
    try:
        record.destroy()
        expense_data.remove(record)
        # regrid remaining rows
        for i, rec in enumerate(expense_data):
            try:
                rec.category.grid(row=i, column=0, sticky=NSEW)
                rec.amount.grid(row=i, column=1, sticky=NSEW)
            except:
                pass
    except Exception:
        pass

def clear_all_expense_fields():
    for rec in expense_data:
        rec.clear()

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
    row = IncomeRow(catInc, amtInc)
    income_data.append(row)
    catInc.bind("<Button-3>", lambda event, rec=row: incEnt_menu(event, rec))
    catInc.focus_set()
    try:
        DateSelct.config(state="disabled")
    except Exception:
        pass
    if DateSelct:
        DateSelct.config(state="disabled")
    TimeSpanSel.config(state="disabled")

def incEnt_menu(event, record):
    menu_incEnt.entryconfigure(0, command=lambda: deleteInc_row(record))
    menu_incEnt.tk_popup(event.x_root, event.y_root)

def deleteInc_row(record):
    try:
        record.destroy()
        income_data.remove(record)
        for i, rec in enumerate(income_data):
            try:
                rec.category.grid(row=i, column=0, sticky=NSEW)
                rec.amount.grid(row=i, column=1, sticky=NSEW)
            except:
                pass
    except Exception:
        pass

def clear_all_income_fields():
    for rec in income_data:
        rec.clear()

# COMPARISON SECTION
def update_totals_tables(span, data_list):
    total_income = sum(entry.get("income", 0.0) for entry in data_list)
    total_expense = sum(entry.get("expense", 0.0) for entry in data_list)
    net_total = total_income - total_expense

    grossTotal.config(text=f"Total Gross Income: {total_income:.2f}")
    expTotal.config(text=f"Total Expense: {total_expense:.2f}")
    netTotal.config(text=f"Total Net Income: {net_total:.2f}")

def parse_amount(s):
    s = (s or "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None

def collect_current_entries():
    incomes = []
    expenses = []
    for rec in income_data:
        cat = rec.get_category()
        amt = rec.get_amount()
        if cat and amt is not None:
            incomes.append({"category": cat, "amount": amt})
    for rec in expense_data:
        cat = rec.get_category()
        amt = rec.get_amount()
        if cat and amt is not None:
            expenses.append({"category": cat, "amount": amt})
    return incomes, expenses

def save_current_timespan():
    global current_span_index
    try:
        current_date = DateSelct.get_date()
    except Exception:
        current_date = date.today()
    if isinstance(current_date, str):
        try:
            current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        except Exception:
            current_date = date.today()

    span_type = varTimeSpan.get() or "Weeks"
    incomes, expenses = collect_current_entries()
    rec = store.save_record(span_type, current_date, incomes, expenses)
    current_span_index = rec["index"]
    clear_all_income_fields()
    clear_all_expense_fields()
    return rec

def GenResult():
    for w in grosTotSF.scrollable_frame.winfo_children():
        w.destroy()
    for w in expTotSF.scrollable_frame.winfo_children():
        w.destroy()
    for w in netTotSF.scrollable_frame.winfo_children():
        w.destroy()

    merged = []
    for span, records in store.totals_by_span.items():
        for rec in records:
            merged.append(rec)

    if not merged:
        messagebox.showinfo("No Data", "No timespan data was found.")
        return

    income_categories = {}
    expense_categories = {}
    net_rows = []

    for rec in merged:
        for item in rec.get("income_list", []):
            cat = item["category"]
            income_categories[cat] = income_categories.get(cat, 0) + item["amount"]
        for item in rec.get("expense_list", []):
            cat = item["category"]
            expense_categories[cat] = expense_categories.get(cat, 0) + item["amount"]
        net_rows.append((rec["span_type"], rec["net_total"]))

    total_gross = sum(income_categories.values())
    total_expense = sum(expense_categories.values())
    total_net = total_gross - total_expense

    grossTotal.config(text=f"Total Gross Income: {total_gross:.2f}")
    expTotal.config(text=f"Total Expense: {total_expense:.2f}")
    netTotal.config(text=f"Total Net Income: {total_net:.2f}")

    for cat, val in income_categories.items():
        Label(grosTotSF.scrollable_frame,
              text=f"{cat}: {val:.2f}",
              bg="lightgrey").pack(anchor="w")

    for cat, val in expense_categories.items():
        Label(expTotSF.scrollable_frame,
              text=f"{cat}: {val:.2f}",
              bg="lightgrey").pack(anchor="w")

    for span, val in net_rows:
        Label(netTotSF.scrollable_frame,
              text=f"{span}: {val:.2f}",
              bg="lightgrey").pack(anchor="w")

    try:
        lineChart.render()
    except Exception:
        pass

def go_next_timespan():
    record = save_current_timespan()
    span_type = record["span_type"]
    entries_for_span = store.totals_by_span.get(span_type, [])
    try:
        new_date = calculate_next_date(
            DateSelct.get_date(),
            span_type,
            1
        )
        DateSelct.set_date(new_date)
    except Exception:
        pass

#-v-v-v-v-v-v-v-v-v-v-v-v-v-v-v-v-
#-v-v-GRACHIC USER INTERFACE -v-v-
#-v-v-v-v-v-v-v-v-v-v-v-v-v-v-v-v-
# Main Menu
Menubar = Menu(root, relief=RAISED, borderwidth=1)
root.config(menu=Menubar)
fileMenu = Menu(Menubar, tearoff=0)
Menubar.add_cascade(label="Menu", menu=fileMenu)
fileMenu.add_command(label="Save", command= save_as_textFile)
fileMenu.add_separator()
fileMenu.add_command(label="Reset", command= reset_all)

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
NextTSFrame = Frame(IncFrame, bg="lightgrey")
ExpFrame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
ExpFrame.grid_columnconfigure((0, 1), weight=1)
IncFrame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
IncFrame.grid_columnconfigure((0, 1), weight=1)
LineFrame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
LineFrame.grid_columnconfigure((0, 1), weight=1)
DateRel.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky=S)
NextTSFrame.grid(row=2, column=0, columnspan=2, sticky=S)

# EXPENSE FRAME WIDGETS
LabelEx1 = Label(ExpFrame, text='Expenses:', font=("Calibri", 14), bg="white")
ChartExp = Frame(ExpFrame, bg='lightgrey', width=300, height=300)
ChartExp.pack_propagate(False)
ExpListCont = Frame(ExpFrame, bg="lightgrey", width=200, height=150, relief=SUNKEN, borderwidth=2)
ExpListCont.grid_propagate(False)
ExpCatAmt = Frame(ExpListCont,relief=RAISED, borderwidth=1)
ExpCatAmt.columnconfigure((0,1), weight=1)
expCatLab = Label(ExpCatAmt, text="Category:",font=("Calibri", 12))
expAmtLab = Label(ExpCatAmt, text="Amount:",font=("Calibri", 12))
ExpScrollFrame = ScrollFrame(ExpListCont, height=150)
ExpScrollFrame.scrollable_frame.config(bg="lightgrey")
totExp = Label(ExpListCont, text='Total Expenses: ', font=("Calibri", 14), bg="lightgrey")
addExp = Button(ExpFrame, text='Add Expense', font=("Calibri", 14), command=addExpense)
chartE = Button(ExpFrame, text='Generate Chart', font=("Calibri", 14))
pieChart = PieChart(ChartExp, expense_data, total_label=totExp)
LabelEx1.grid(row=0, column=0, sticky=N)
ChartExp.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
ExpListCont.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
ExpCatAmt.pack(side=TOP, fill="both", expand=True)
expCatLab.grid(row=0,column=0,sticky=NW)
expAmtLab.grid(row=0,column=1,sticky=NW)
ExpScrollFrame.pack(fill="both", expand=True)
totExp.pack(fill="both", expand=True)
addExp.grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
chartE.grid(row=4, column=1, padx=5, pady=5, sticky=NSEW)
chartE.config(command=pieChart.render)

# Date Related Elements
DateSelct = DateEntry(DateRel, font=('Arial', 12), selectmode='date')
TimeSpanSel = Combobox(DateRel, font=('Arial', 12),
                       textvariable=varTimeSpan,
                       values=['Weeks', 'Months', 'Years'],
                       state='readonly')
varTimeSpan.set("Weeks")
TimeSpanSel.bind("<<ComboboxSelected>>", update_mode)
update_mode()
DateSelct.bind("<<DateEntrySelected>>", dateSelect)
set_default_date()
DateSelct.pack(side=LEFT)
TimeSpanSel.pack(side=LEFT)

# INCOME FRAME WIDGETS
LabelIn1 = Label(IncFrame, text='Income Source(s):', font=("Calibri", 14), bg="white")
ChartInc = Frame(IncFrame, bg='lightgrey', width=300, height=300)
ChartInc.pack_propagate(False)
IncListCont = Frame(IncFrame, bg="lightgrey", width=200, height=150, relief=SUNKEN, borderwidth=2)
IncListCont.grid_propagate(False)
IncCatAmt = Frame(IncListCont,relief=RAISED, borderwidth=1)
IncCatAmt.columnconfigure((0,1), weight=1)
incCatLab = Label(IncCatAmt, text="Category:",font=("Calibri", 12))
incAmtLab = Label(IncCatAmt, text="Amount:",font=("Calibri", 12))
IncScrollFrame = ScrollFrame(IncListCont, height=150)
IncScrollFrame.scrollable_frame.config(bg="lightgrey")
netInc = Label(IncListCont, text='Net Income: ', font=("Calibri", 14), bg="lightgrey")
addInc = Button(IncFrame, text='Add Income', font=("Calibri", 14), command=addIncome)
chartI = Button(IncFrame, text='Generate Graph', font=("Calibri", 14))
barChart = BarChart(ChartInc, income_data, expense_data, net_label=netInc)
LabelIn1.grid(row=0, column=0, sticky=N)
ChartInc.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
IncListCont.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
IncCatAmt.pack(side=TOP, fill="both", expand=True)
incCatLab.grid(row=0,column=0,sticky=NW)
incAmtLab.grid(row=0,column=1,sticky=NW)
IncScrollFrame.pack(fill="both", expand=True)
netInc.pack(fill="both", expand=True)
addInc.grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
chartI.grid(row=4, column=1, padx=5, pady=5, sticky=NSEW)
chartI.config(command=barChart.render)

# NEXT BUTTON FRAME
NextTP = Button(NextTSFrame, text='  Next Timespan  ', font=("Calibri", 12), command=go_next_timespan)
NextTP.pack(side=LEFT)

# LINE CHART FRAME WIDGETS
LabelLin1 = Label(LineFrame, text='Expense vs Income over a period of time:', font=("Calibri", 14), bg="white")
ChartLine = Frame(LineFrame, bg='lightgrey', width=300, height=300)
ChartLine.pack_propagate(False)
genbutt_Frame = Frame(LineFrame, bg="white")
lineChart = LineChart(ChartLine, store.totals_by_span)
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

