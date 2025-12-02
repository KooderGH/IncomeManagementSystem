from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkcalendar import DateEntry
from datetime import datetime, date, timedelta
import calendar
import numpy as np
import platform

root = Tk()
# MAINWINDOW Details
root.geometry("1080x720")
root.minsize(1080, 720)
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

def parse_amount(s):
    """Return float or None if invalid/blank."""
    s = (s or "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None

def add_months(orig_date, months):
    """Add (or subtract) months to a date safely."""
    # orig_date: datetime.date
    month = orig_date.month - 1 + months
    year = orig_date.year + month // 12
    month = month % 12 + 1
    day = min(orig_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def calculate_next_date(current_date, span, step=1):
    """Return the next or previous date given a timespan and step (+1 or -1)."""
    if span == "Weeks":
        return current_date + timedelta(weeks=step)
    elif span == "Months":
        return add_months(current_date, step)
    else:  # Years
        try:
            return date(current_date.year + step, current_date.month, current_date.day)
        except Exception:
            # fallback for invalid day in month
            year = current_date.year + step
            month = current_date.month
            day = min(current_date.day, calendar.monthrange(year, month)[1])
            return date(year, month, day)


def prefill_timespan(span, target_date):
    """Prefill the current income/expense entries if data exists for this timespan."""
    record = next((r for r in totals_by_span.get(span, []) if r['start_date'] == target_date.isoformat()), None)
    clear_all_income_fields()
    clear_all_expense_fields()

    if record:
        # Prefill Income
        for rec in income_data:
            amt = record.get('income_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))
        # Prefill Expenses
        for rec in expense_data:
            amt = record.get('expense_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))


def compute_overall_net(all_entries):
    """Return the total net income across all saved records."""
    return sum(r.get('income', 0) - r.get('expense', 0) for r in all_entries)

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

        # Better cross-platform wheel support:
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _on_mousewheel_windows(self, event):
        # Windows and many X11 bindings emit event.delta multiples of 120
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_x11_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_x11_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        # Use platform detection for safer binding
        if platform.system() == "Linux":
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_x11_up)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_x11_down)
        else:
            # Windows & macOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)

    def _unbind_mousewheel(self):
        if platform.system() == "Linux":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

class PieChart:
    def __init__(self, parent_frame, expense_data, total_label=None):
        self.parent_frame = parent_frame
        self.expense_data = expense_data
        self.total_label = total_label
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
        total_expense = 0.0
        for record in self.expense_data:
            cat = record["category"].get().strip()
            amt = parse_amount(record["amount"].get())
            if cat != "" and amt is not None:
                labels.append(cat)
                amounts.append(amt)
                total_expense += amt

        if self.total_label:
            self.total_label.config(text=f"Total Expenses: {total_expense:.2f}")

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
    def __init__(self, parent_frame, income_data, expense_data, net_label=None):
        self.parent_frame = parent_frame
        self.income_data = income_data
        self.expense_data = expense_data
        self.net_label = net_label
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
        total_income = 0.0
        for record in self.income_data:
            cat = record["category"].get().strip()
            amt = parse_amount(record["amount"].get())
            if cat != "" and amt is not None:
                labels.append(cat)
                amounts.append(amt)
                total_income += amt

        total_expense = 0.0
        for rec in self.expense_data:
            amt = parse_amount(rec["amount"].get())
            if amt is not None:
                total_expense += amt

        if self.net_label:
            self.net_label.config(text=f"Net Income: {total_income - total_expense:.2f}")

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

    def render(self):
        # Destroy existing
        if self.canvas_widget:
            try:
                self.canvas_widget.get_tk_widget().destroy()
            except:
                pass
            self.canvas_widget = None

        if self.toolbar:
            try:
                self.toolbar.destroy()
            except:
                pass
            self.toolbar = None

        plt.close('all')

        # Build the combined chronological dataset
        combined = []

        for span_type, records in self.totals_by_span.items():
            for i, rec in enumerate(records, start=1):
                combined.append({
                    "label": f"{span_type[:-1]} {i}",   # Week 1, Month 1, Year 1
                    "gross": rec["gross_total"],
                    "expense": rec["expense_total"],
                    "net": rec["net_total"]
                })

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        if not combined:
            ax.text(0.5, 0.5, "No data to display", ha="center", va="center")
        else:
            x = np.arange(len(combined))

            gross_values   = [c["gross"] for c in combined]
            expense_values = [c["expense"] for c in combined]
            net_values     = [c["net"] for c in combined]
            x_labels       = [c["label"] for c in combined]

            ax.plot(x, gross_values, marker="o", label="Gross Income")
            ax.plot(x, expense_values, marker="o", label="Expenses")
            ax.plot(x, net_values, marker="o", label="Net Income")

            ax.set_xticks(x)
            ax.set_xticklabels(x_labels, rotation=45, ha="right")
            ax.set_ylabel("Amount")
            ax.set_title("Income vs Expenses Over Time")
            ax.grid(True)
            ax.legend()
            ax.margins(x=0.05)

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.parent_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, self.parent_frame)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, fill=X)




# DATE RELATED
current_timespan = StringVar(value="Week")
def set_default_date():
    # set DateSelct to today's date (DateEntry expects date or datetime)
    try:
        DateSelct.set_date(date.today())
    except Exception:
        # fallback to string insert (rare)
        try:
            DateSelct.delete(0, "end")
            DateSelct.insert(0, date.today().isoformat())
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
    try:
        DateSelct.config(state="disabled")
    except Exception:
        pass

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
    try:
        DateSelct.config(state="disabled")
    except Exception:
        pass

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
def update_totals_tables(span, data_list):
    total_income = sum(entry.get("income", 0.0) for entry in data_list)
    total_expense = sum(entry.get("expense", 0.0) for entry in data_list)
    net_total = total_income - total_expense

    grossTotal.config(text=f"Total Gross Income: {total_income:.2f}")
    expTotal.config(text=f"Total Expense: {total_expense:.2f}")
    netTotal.config(text=f"Total Net Income: {net_total:.2f}")


def collect_current_entries():
    """
    Read the current GUI income_data and expense_data Entry widgets and
    return two lists of dicts: incomes, expenses.
    Format: [{"category": "Salary", "amount": 123.45}, ...]
    """
    incomes = []
    expenses = []

    # income_data and expense_data are lists of {"category": Entry, "amount": Entry}
    for rec in income_data:
        cat = rec["category"].get().strip()
        amt = parse_amount(rec["amount"].get())
        if cat and amt is not None:
            incomes.append({"category": cat, "amount": amt})

    for rec in expense_data:
        cat = rec["category"].get().strip()
        amt = parse_amount(rec["amount"].get())
        if cat and amt is not None:
            expenses.append({"category": cat, "amount": amt})

    return incomes, expenses


def save_current_timespan():
    """
    Build a consistent record from the current entries and append to totals_by_span.
    Includes:
    - per-category lists
    - per-category summed totals
    - per-span totals
    - span index for charts
    """
    global totals_by_span, TimespanList, current_span_index

    try:
        current_date = DateSelct.get_date()
        date_str = current_date.isoformat()
    except Exception:
        date_str = date.today().isoformat()

    span_type = varTimeSpan.get() or "Weeks"

    incomes, expenses = collect_current_entries()

    # -----------------------------------------
    # 1. PER-CATEGORY SUMMATION
    # -----------------------------------------
    income_categories = {}
    for entry in incomes:
        cat = entry["category"]
        income_categories.setdefault(cat, 0)
        income_categories[cat] += entry["amount"]

    expense_categories = {}
    for entry in expenses:
        cat = entry["category"]
        expense_categories.setdefault(cat, 0)
        expense_categories[cat] += entry["amount"]

    # -----------------------------------------
    # 2. TOTALS
    # -----------------------------------------
    gross_total = sum(income_categories.values())
    expense_total = sum(expense_categories.values())
    net_total = gross_total - expense_total

    # -----------------------------------------
    # 3. Create final record structure
    # -----------------------------------------
    record = {
        "start_date": date_str,
        "span_type": span_type,
        "span_index": current_span_index,   # <-- NECESSARY FOR CHARTS

        "income_list": incomes,
        "expense_list": expenses,

        "income_totals": income_categories,     # <-- FIXED
        "expense_totals": expense_categories,   # <-- FIXED

        "gross_total": gross_total,
        "expense_total": expense_total,
        "net_total": net_total,
    }

    # -----------------------------------------
    # 4. Append record to the correct span bucket
    # -----------------------------------------
    totals_by_span.setdefault(span_type, []).append(record)

    # -----------------------------------------
    # 5. Clear UI fields
    # -----------------------------------------
    clear_all_income_fields()
    clear_all_expense_fields()

    return record



print("\n=== DEBUG: totals_by_span ===")
for span_type, records in totals_by_span.items():
    print(f"Span: {span_type}")
    for r in records:
        print("  ", r)

print("\n=== DEBUG: income_categories ===", income_categories if 'income_categories' in globals() else "NOT DEFINED")
print("\n=== DEBUG: expense_categories ===", expense_categories if 'expense_categories' in globals() else "NOT DEFINED")
print("\n=== DEBUG: net_rows ===", net_rows if 'net_rows' in globals() else "NOT DEFINED")

def GenResult():
    global totals_by_span

    # -----------------------
    # Clear old UI rows
    # -----------------------
    for w in grosTotSF.scrollable_frame.winfo_children():
        w.destroy()
    for w in expTotSF.scrollable_frame.winfo_children():
        w.destroy()
    for w in netTotSF.scrollable_frame.winfo_children():
        w.destroy()

    # -----------------------
    # Merge all records
    # -----------------------
    merged = []
    for span, records in totals_by_span.items():
        for rec in records:
            merged.append(rec)

    if not merged:
        messagebox.showinfo("No Data", "No timespan data was found.")
        return

    # -----------------------
    # Build category totals
    # -----------------------
    income_categories = {}
    expense_categories = {}
    net_rows = []

    for rec in merged:
        # income categories
        for item in rec["income_list"]:
            cat = item["category"]
            income_categories[cat] = income_categories.get(cat, 0) + item["amount"]

        # expense categories
        for item in rec["expense_list"]:
            cat = item["category"]
            expense_categories[cat] = expense_categories.get(cat, 0) + item["amount"]

        # net per timespan
        net_rows.append((rec["span_type"], rec["net_total"]))

    # -----------------------
    # Totals across categories
    # -----------------------
    total_gross = sum(income_categories.values())
    total_expense = sum(expense_categories.values())
    total_net = total_gross - total_expense

    grossTotal.config(text=f"Total Gross Income: {total_gross:.2f}")
    expTotal.config(text=f"Total Expense: {total_expense:.2f}")
    netTotal.config(text=f"Total Net Income: {total_net:.2f}")

    # -----------------------
    # Fill scroll frames
    # -----------------------
    # Gross income categories table
    for cat, val in income_categories.items():
        Label(grosTotSF.scrollable_frame,
              text=f"{cat}: {val:.2f}",
              bg="lightgrey").pack(anchor="w")

    # Expense categories table
    for cat, val in expense_categories.items():
        Label(expTotSF.scrollable_frame,
              text=f"{cat}: {val:.2f}",
              bg="lightgrey").pack(anchor="w")

    # Net per timespan table
    for span, val in net_rows:
        Label(netTotSF.scrollable_frame,
              text=f"{span}: {val:.2f}",
              bg="lightgrey").pack(anchor="w")

    # -----------------------
    # Final step: Render line chart
    # -----------------------
    lineChart.render()   # ← NO MORE PARAMETERS





# NEXT & PREV BUTTONS FUNCTIONS
def go_next_timespan():
    """
    Save the current timespan dataset and advance the index *for that span type*.
    This allows multiple weeks, multiple months, etc., each with their own index.
    """
    global totals_by_span, current_span_index

    # Save the record first
    record = save_current_timespan()

    span_type = record["span_type"]

    # Count how many records exist for THIS span type
    entries_for_span = totals_by_span.get(span_type, [])

    # The next index is simply the length of the list
    # (0-based indexing -> if 1 entry exists, next index is 1)
    current_span_index = len(entries_for_span)

    # --- OPTIONAL: move calendar date forward automatically ---
    try:
        new_date = calculate_next_date(
            DateSelct.get_date(),
            span_type,
            1
        )
        DateSelct.set_date(new_date)
    except Exception:
        pass


def go_prev_timespan():
    span = varTimeSpan.get()
    try:
        current_date = DateSelct.get_date()
    except Exception:
        messagebox.showerror("Invalid date", "Please select a valid date.")
        return

    if span == "Weeks":
        prev_date = current_date - timedelta(weeks=1)
    elif span == "Months":
        prev_date = add_months(current_date, -1)
    else:
        prev_date = date(current_date.year - 1, current_date.month, min(current_date.day, calendar.monthrange(current_date.year - 1, current_date.month)[1]))

    DateSelct.set_date(prev_date)
    clear_all_income_fields()
    clear_all_expense_fields()

    # Prefill if record exists
    data_list = totals_by_span.get(span, [])
    record = next((r for r in data_list if r['start_date'] == prev_date.isoformat()), None)
    if record:
        for rec in income_data:
            amt = record.get('income_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))
        for rec in expense_data:
            amt = record.get('expense_by_cat', {}).get(rec["category"].get().strip(), "")
            if amt != "":
                rec["amount"].insert(0, str(amt))



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

ExpListCont = Frame(ExpFrame, bg="lightgrey", width=200, height=150, relief=SUNKEN, borderwidth=2)
ExpListCont.grid_propagate(False)
ExpScrollFrame = ScrollFrame(ExpListCont, height=150)
ExpScrollFrame.scrollable_frame.config(bg="lightgrey")

totExp = Label(ExpListCont, text='Total Expenses: ', font=("Calibri", 14), bg="lightgrey")
addExp = Button(ExpFrame, text='Add Expense', font=("Calibri", 14), command=addExpense)
chartE = Button(ExpFrame, text='Generate Chart', font=("Calibri", 14))

# Now create pieChart passing totExp so it doesn't use a global
pieChart = PieChart(ChartExp, expense_data, total_label=totExp)

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

IncListCont = Frame(IncFrame, bg="lightgrey", width=200, height=150, relief=SUNKEN, borderwidth=2)
IncListCont.grid_propagate(False)
IncScrollFrame = ScrollFrame(IncListCont, height=150)
IncScrollFrame.scrollable_frame.config(bg="lightgrey")

netInc = Label(IncListCont, text='Net Income: ', font=("Calibri", 14), bg="lightgrey")
addInc = Button(IncFrame, text='Add Income', font=("Calibri", 14), command=addIncome)
chartI = Button(IncFrame, text='Generate Graph', font=("Calibri", 14))

# Create barChart after netInc exists
barChart = BarChart(ChartInc, income_data, expense_data, net_label=netInc)

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
