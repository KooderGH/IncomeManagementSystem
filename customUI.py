from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import platform

def parse_amount(s):
    s = (s or "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None

def display_net_totals(merged, netTotSF):
    net_counters = {"Weeks": 0, "Months": 0, "Years": 0}

    net_rows = []

    for rec in merged:
        span_type = rec["span_type"]
        net_counters[span_type] += 1
        label = f"{span_type[:-1]} {net_counters[span_type]}"
        net_total = rec.get("net_total", 0.0)
        net_rows.append((label, net_total))

    for widget in netTotSF.scrollable_frame.winfo_children():
        widget.destroy()

    for label, val in net_rows:
        Label(netTotSF.scrollable_frame,
            text=f"{label}: {val:.2f}",
            bg="lightgrey").pack(anchor="w")

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
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_x11_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_x11_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        if platform.system() == "Linux":
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_x11_up)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_x11_down)
        else:
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
        if self.canvas_widget:
            try: self.canvas_widget.get_tk_widget().destroy()
            except: pass
            self.canvas_widget = None

        if self.toolbar:
            try: self.toolbar.destroy()
            except: pass
            self.toolbar = None

        plt.close("all")

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        labels = []
        amounts = []
        total_expense = 0.0

        for record in self.expense_data:
            cat = (record.category.get() or "").strip()
            amt = parse_amount(record.amount.get())
            d = record.date

            if cat and amt is not None:
                labels.append(cat)
                amounts.append(amt)
                total_expense += amt

        if self.total_label:
            self.total_label.config(text=f"Total Expenses: {total_expense:.2f}")

        if not amounts:
            ax.text(0.5, 0.5, "No data to display", ha="center", va="center")
        else:
            ax.pie(amounts, labels=labels, autopct="%1.1f%%")
            ax.set_title("Expense Distribution")

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
        if self.canvas_widget:
            try: self.canvas_widget.get_tk_widget().destroy()
            except: pass
            self.canvas_widget = None

        if self.toolbar:
            try: self.toolbar.destroy()
            except: pass
            self.toolbar = None

        plt.close("all")

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        labels = []
        amounts = []
        total_income = 0.0

        for record in self.income_data:
            cat = (record.category.get() or "").strip()
            amt = parse_amount(record.amount.get())
            d = record.date

            if cat and amt is not None:
                labels.append(cat)
                amounts.append(amt)
                total_income += amt

        total_expense = sum(parse_amount(r.amount.get()) or 0 for r in self.expense_data)

        if self.net_label:
            self.net_label.config(text=f"Net Income: {total_income - total_expense:.2f}")

        if labels:
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

        combined = []
        span_counters = {"Weeks": 0, "Months": 0, "Years": 0}
        
        for span_type, records in self.totals_by_span.items():
            for rec in records: 
                span_counters[span_type] += 1 
                combined.append({ "label": f"{span_type[:-1]} {span_counters[span_type]}",
                                  "gross": rec.get("gross_total", 0.0),
                                  "expense": rec.get("expense_total", 0.0), 
                                  "net": rec.get("net_total", 0.0) 
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
