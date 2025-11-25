import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import date

from helpers import (
    format_currency,
    parse_number,
    compute_percentage,
    format_percentage_display,
)
from storage import load_accounts, save_accounts

ENTRYBOX_WIDTH = 12
TREEVIEW_COLUMN_WIDTH = 100


def resource_path(relative_path):
    """
    Get absolute path to resource.
    Works for dev mode and for PyInstaller EXE.
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller temporary folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class CreditTracker(tk.Tk):
    def __init__(self):
        super().__init__()

        # Default utilization threshold for "high utilization" coloring
        self.util_threshold = 50.0  # percent

        # Window setup
        self.iconbitmap(resource_path("credit.ico"))
        self.title("Credit Tracker")
        self.geometry("1100x600")
        self.configure(bg="#F1F3E0")  # main bg color

        self._configure_style()
        self._build_layout()

    # ----------------- Styling -----------------

    def _configure_style(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Palette
        BG_MAIN = "#F1F3E0"   # window background
        BG_PANEL = "#D2DCB6"  # panels
        BTN_BG = "#A1BC98"    # buttons
        BTN_ACTIVE = "#778873"
        TEXT_MAIN = "#333333"
        TEXT_LIGHT = "#556055"
        BORDER = "#778873"

        # App background
        self.configure(bg=BG_MAIN)

        # Frames
        style.configure("TFrame", background=BG_PANEL)
        style.configure("Left.TFrame", background=BG_PANEL)
        style.configure("Right.TFrame", background=BG_PANEL)

        # Header Label
        style.configure(
            "Header.TLabel",
            background=BG_PANEL,
            foreground=TEXT_MAIN,
            font=("Segoe UI", 12, "bold"),
        )

        # Field labels
        style.configure(
            "FieldLabel.TLabel",
            background=BG_PANEL,
            foreground=TEXT_LIGHT,
            font=("Segoe UI", 10),
        )

        # Buttons
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 5),
            foreground=TEXT_MAIN,
            background=BTN_BG,
            bordercolor=BORDER,
            borderwidth=1,
        )
        style.map(
            "TButton",
            background=[("active", BTN_ACTIVE), ("pressed", BORDER)],
            foreground=[("pressed", "white")],
        )

        # Treeview
        style.configure(
            "Treeview",
            background=BG_MAIN,
            foreground=TEXT_MAIN,
            rowheight=24,
            fieldbackground=BG_MAIN,
            font=("Segoe UI", 10),
            bordercolor=BORDER,
            borderwidth=1,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_PANEL,
            foreground=TEXT_MAIN,
            font=("Segoe UI", 10, "bold"),
            bordercolor=BORDER,
            borderwidth=1,
        )
        style.map(
            "Treeview",
            background=[("selected", BTN_BG)],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Summary.TFrame",
            background="#F0F0F0",
        )

    # ----------------- Layout -----------------

    def _build_layout(self):
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Left frame (full height)
        left_frame = ttk.Frame(paned, style="Left.TFrame", padding=(15, 15))
        paned.add(left_frame, weight=1)

        # Right frame (we'll split it into top + bottom inside)
        right_frame = ttk.Frame(paned, style="Right.TFrame", padding=(10, 10))
        paned.add(right_frame, weight=5)

        # --- Left panel ---
        header = ttk.Label(left_frame, text="Data Entry", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Settings button (gear icon style)
        settings_btn = ttk.Button(
            left_frame,
            text="⚙",
            width=3,
            command=self.open_settings,
        )
        settings_btn.grid(row=0, column=2, sticky="e", pady=(0, 10), padx=(5, 0))

        ttk.Label(left_frame, text="Select Account:", style="FieldLabel.TLabel").grid(
            row=1, column=0, sticky="w", pady=2, padx=10
        )
        self.select_account_var = tk.StringVar()
        self.select_account = ttk.Combobox(
            left_frame,
            width=ENTRYBOX_WIDTH,
            textvariable=self.select_account_var,
            state="readonly",
        )
        self.select_account.grid(row=1, column=1, sticky="ew", pady=5, padx=10)

        ttk.Label(left_frame, text="New Balance:", style="FieldLabel.TLabel").grid(
            row=2, column=0, sticky="w", pady=5, padx=10
        )
        self.entry_new_balance = ttk.Entry(left_frame, width=ENTRYBOX_WIDTH)
        self.entry_new_balance.grid(row=2, column=1, sticky="ew", pady=5, padx=10)

        separator = ttk.Separator(left_frame, orient="horizontal")
        separator.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10, padx=10)

        ttk.Label(left_frame, text="Add Account:", style="FieldLabel.TLabel").grid(
            row=4, column=0, sticky="w", pady=5, padx=10
        )
        self.entry_new_account = ttk.Entry(left_frame, width=ENTRYBOX_WIDTH)
        self.entry_new_account.grid(row=4, column=1, sticky="ew", pady=5, padx=10)

        ttk.Label(left_frame, text="Line of Credit:", style="FieldLabel.TLabel").grid(
            row=5, column=0, sticky="w", pady=5, padx=10
        )
        self.entry_line = ttk.Entry(left_frame, width=ENTRYBOX_WIDTH)
        self.entry_line.grid(row=5, column=1, sticky="ew", pady=5, padx=10)

        ttk.Label(left_frame, text="Balance:", style="FieldLabel.TLabel").grid(
            row=6, column=0, sticky="w", pady=5, padx=10
        )
        self.entry_balance = ttk.Entry(left_frame, width=ENTRYBOX_WIDTH)
        self.entry_balance.grid(row=6, column=1, sticky="ew", pady=5, padx=10)

        ttk.Label(left_frame, text="Minimum Payment:", style="FieldLabel.TLabel").grid(
            row=7, column=0, sticky="w", pady=5, padx=10
        )
        self.entry_min_pay = ttk.Entry(left_frame, width=ENTRYBOX_WIDTH)
        self.entry_min_pay.grid(row=7, column=1, sticky="ew", pady=5, padx=10)

        ttk.Label(left_frame, text="Due Date:", style="FieldLabel.TLabel").grid(
            row=8, column=0, sticky="w", pady=5, padx=10
        )
        self.entry_paydate = ttk.Entry(left_frame, width=ENTRYBOX_WIDTH)
        self.entry_paydate.grid(row=8, column=1, sticky="ew", pady=5, padx=10)

        left_frame.columnconfigure(1, weight=1)

        buttons_frame = ttk.Frame(left_frame, style="Left.TFrame")
        buttons_frame.grid(row=9, column=0, columnspan=3, pady=(15, 0), sticky="ew")
        buttons_frame.columnconfigure((0, 1, 2), weight=1)

        btn_add = ttk.Button(buttons_frame, text="Add", command=self.add_item)
        btn_add.grid(row=0, column=0, padx=3, sticky="ew")

        btn_edit = ttk.Button(buttons_frame, text="Edit", command=self.update_item)
        btn_edit.grid(row=0, column=1, padx=3, sticky="ew")

        btn_delete = ttk.Button(buttons_frame, text="Delete", command=self.delete_item)
        btn_delete.grid(row=0, column=2, padx=3, sticky="ew")

        btn_clear = ttk.Button(
            left_frame, text="Clear Fields", command=self.clear_fields
        )
        btn_clear.grid(row=10, column=0, columnspan=3, pady=(10, 0), sticky="ew")

        # --- Right panel: top (Records) + bottom (Summary) ---

        tv_label = ttk.Label(right_frame, text="Records", style="Header.TLabel")
        tv_label.pack(anchor="w", pady=(0, 8))

        # TOP: table area
        right_top_frame = ttk.Frame(right_frame, style="Right.TFrame")
        right_top_frame.pack(fill="both", expand=True)

        columns = ("account", "line", "balance", "percentage", "min_pay", "paydate")
        self.tree = ttk.Treeview(
            right_top_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree["height"] = 11

        self.tree.heading("account", text="Account")
        self.tree.heading("line", text="Line of Credit")
        self.tree.heading("balance", text="Balance")
        self.tree.heading("percentage", text="Percentage")
        self.tree.heading("min_pay", text="Min Payment")
        self.tree.heading("paydate", text="Due Date")

        self.tree.column("account", width=TREEVIEW_COLUMN_WIDTH, anchor="w")
        self.tree.column("line", width=TREEVIEW_COLUMN_WIDTH, anchor="e")
        self.tree.column("balance", width=TREEVIEW_COLUMN_WIDTH, anchor="e")
        self.tree.column("percentage", width=TREEVIEW_COLUMN_WIDTH, anchor="e")
        self.tree.column("min_pay", width=TREEVIEW_COLUMN_WIDTH, anchor="e")
        self.tree.column("paydate", width=TREEVIEW_COLUMN_WIDTH, anchor="center")

        tv_scroll = ttk.Scrollbar(
            right_top_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tv_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tv_scroll.pack(side="right", fill="y")

        # Tag for high utilization only
        self.tree.tag_configure("high_util", background="#E08F79", foreground="#452829")

        # BOTTOM: summary / chart area
        right_bottom_frame = ttk.Frame(
            right_frame, style="Right.TFrame", padding=(0, 10, 0, 0)
        )
        right_bottom_frame.pack(fill="x", side="bottom")

        summary_title = ttk.Label(
            right_bottom_frame,
            text="Total Credit Utilization",
            style="Header.TLabel",
        )
        summary_title.pack(anchor="w", pady=(0, 5))

        # Canvas for donut chart
        self.chart_canvas = tk.Canvas(
            right_bottom_frame,
            height=160,
            bg="#D2DCB6",      # match panel bg
            highlightthickness=0,
            bd=0,
        )
        self.chart_canvas.pack(fill="x")

        # Label for totals
        self.summary_label = ttk.Label(
            right_bottom_frame,
            text="",
            style="FieldLabel.TLabel",
        )
        self.summary_label.pack(anchor="w", pady=(5, 0))

        # Bindings
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Escape>", lambda e: self.clear_tree_selection())
        self.tree.bind("<Button-1>", self.on_tree_click)

        # Load data from 'database'
        self.load_from_db()

    # ----------------- Summary chart -----------------

    def update_summary_chart(self):
        """Recalculate totals and redraw the donut-style utilization chart."""
        if not hasattr(self, "chart_canvas"):
            return

        total_line = 0.0
        total_balance = 0.0

        for item in self.tree.get_children():
            _, line, balance, *_ = self.tree.item(item, "values")
            total_line += parse_number(line)
            total_balance += parse_number(balance)

        # Clear previous drawing
        self.chart_canvas.delete("all")

        # Ensure geometry is up-to-date
        self.chart_canvas.update_idletasks()

        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()

        # Fallback sensible sizes if still too small
        if width < 150:
            width = 260
        if height < 100:
            height = 140

        size = min(width, height) - 20
        cx = width / 2
        cy = height / 2
        r = size / 2

        # Background ring (4 coordinates)
        self.chart_canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            outline="#73AF6F",
            width=20,
        )

        # Utilization ratio
        if total_line > 0:
            util_ratio = total_balance / total_line
        else:
            util_ratio = 0.0

        extent = util_ratio * 359.9  # max arc

        # Utilization arc (4 coordinates)
        if util_ratio > 0:
            self.chart_canvas.create_arc(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                start=90,         # start at top
                extent=-extent,   # clockwise
                style="arc",
                outline="#D34E4E",
                width=20,
            )

        # Center text (overall utilization %)
        percent_text = f"{util_ratio * 100:.1f}%" if total_line > 0 else "0%"
        self.chart_canvas.create_text(
            cx,
            cy,
            text=percent_text,
            font=("Segoe UI", 14, "bold"),
            fill="#333333",
        )

        # Bottom summary text
        self.summary_label.config(
            text=(
                f"Total Line: {format_currency(total_line)}   |   "
                f"Total Balance: {format_currency(total_balance)}"
            )
        )

    # ----------------- Settings (threshold) -----------------

    def get_percentage_tag(self, percentage):
        """
        Return 'high_util' if percentage meets the current threshold,
        else '' (no tag). Uses self.util_threshold.
        """
        try:
            p = float(percentage)
        except (ValueError, TypeError):
            return ""
        return "high_util" if p >= self.util_threshold else ""

    def open_settings(self):
        """Open a small window to adjust the high-utilization threshold."""
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.transient(self)
        settings_win.grab_set()
        settings_win.resizable(False, False)

        ttk.Label(
            settings_win,
            text="High utilization threshold (%):",
            style="FieldLabel.TLabel",
            background="#F0F0F0",
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        threshold_var = tk.StringVar(value=str(self.util_threshold))
        entry = ttk.Entry(settings_win, textvariable=threshold_var, width=10)
        entry.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")
        entry.focus()

        def save_threshold():
            try:
                val = float(threshold_var.get())
                if val < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid value",
                    "Please enter a valid number greater than or equal to 0.",
                    parent=settings_win,
                )
                return

            self.util_threshold = val
            # Re-apply tags/colors to all rows based on new threshold
            self.reapply_utilization_tags()
            settings_win.destroy()

        btn_frame = ttk.Frame(settings_win, style="Summary.TFrame")
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 10))

        ttk.Button(btn_frame, text="Save", command=save_threshold).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=settings_win.destroy).grid(
            row=0, column=1, padx=5
        )

    def reapply_utilization_tags(self):
        """Recalculate percentage & tags for all rows using the current threshold."""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            if not values or len(values) < 6:
                continue

            # values = [account, line, balance, percentage, min_pay, paydate]
            line_num = parse_number(values[1])
            bal_num = parse_number(values[2])

            percentage_num = compute_percentage(line_num, bal_num)
            percentage_disp = format_percentage_display(percentage_num)
            values[3] = percentage_disp  # update display

            current_tags = set(self.tree.item(item, "tags"))
            # remove any old high_util
            current_tags.discard("high_util")

            tag = self.get_percentage_tag(percentage_num)
            if tag:
                current_tags.add(tag)

            self.tree.item(item, values=values, tags=tuple(current_tags))

    # ----------------- Due date alerts (popup only) -----------------

    def parse_due_day(self, paydate_str):
        """
        Extract the day number from the paydate text.
        Examples:
          '15th' -> 15
          '20'   -> 20
          ' 3rd' -> 3
        Returns an int or None if no digits found.
        """
        s = str(paydate_str).strip()
        if not s:
            return None

        digits = "".join(ch for ch in s if ch.isdigit())
        if not digits:
            return None

        try:
            return int(digits)
        except ValueError:
            return None

    def check_due_alerts(self, show_popup=True):
        """
        Check which accounts have a due date of tomorrow.
        If show_popup is True, show a message listing them.
        (No Treeview color changes here.)
        """
        today_day = date.today().day
        due_tomorrow_accounts = []

        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if not values or len(values) < 6:
                continue

            account = values[0]
            paydate = values[5]

            day = self.parse_due_day(paydate)
            if day is not None and day == today_day + 1:
                due_tomorrow_accounts.append(account)

        if show_popup and due_tomorrow_accounts:
            msg = "Payment due tomorrow for:\n\n" + "\n".join(due_tomorrow_accounts)
            messagebox.showinfo("Upcoming payments", msg, parent=self)

    # ----------------- Treeview selection helpers -----------------

    def clear_tree_selection(self):
        self.tree.selection_remove(self.tree.selection())

    def on_tree_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            self.clear_tree_selection()

    # ----------------- Database I/O -----------------

    def load_from_db(self):
        """Load rows from JSON (via storage.load_accounts)."""
        data = load_accounts()

        for row in data:
            account = row.get("account", "")
            line_val = row.get("line", 0)
            bal_val = row.get("balance", 0)

            line = format_currency(line_val)
            balance = format_currency(bal_val)
            percentage_num = compute_percentage(line_val, bal_val)
            percentage_disp = format_percentage_display(percentage_num)
            tag = self.get_percentage_tag(percentage_num)

            min_pay = format_currency(row.get("min_pay", 0))
            paydate = row.get("paydate", "")

            tags = []
            if tag:
                tags.append(tag)

            self.tree.insert(
                "",
                "end",
                values=(account, line, balance, percentage_disp, min_pay, paydate),
                tags=tuple(tags) if tags else (),
            )

        self.refresh_account_combobox()
        self.update_summary_chart()
        # Popup once on startup if there are accounts due tomorrow
        self.check_due_alerts(show_popup=True)

    def save_to_db(self):
        """Collect Treeview rows and save to JSON (via storage.save_accounts)."""
        data = []
        for item in self.tree.get_children():
            acc, line, bal, perc, min_pay, paydate = self.tree.item(item, "values")
            line_num = parse_number(line)
            bal_num = parse_number(bal)
            min_num = parse_number(min_pay)

            perc_num = compute_percentage(line_num, bal_num)

            data.append(
                {
                    "account": acc,
                    "line": line_num,
                    "balance": bal_num,
                    "percentage": perc_num,
                    "min_pay": min_num,
                    "paydate": paydate,
                }
            )

        save_accounts(data)

    # ----------------- UI helpers -----------------

    def refresh_account_combobox(self):
        accounts = []
        for item in self.tree.get_children():
            acc_name = self.tree.item(item, "values")[0]
            accounts.append(acc_name)
        self.select_account["values"] = sorted(set(accounts))

    def get_entry_data(self):
        """Read fields for adding a new row."""
        account = self.entry_new_account.get().strip()
        if not account:
            account = self.select_account_var.get().strip()

        line_str = self.entry_line.get().strip()
        bal_str = self.entry_balance.get().strip()
        min_pay_str = self.entry_min_pay.get().strip()
        paydate = self.entry_paydate.get().strip()

        line_val = parse_number(line_str)
        bal_val = parse_number(bal_str)
        min_val = parse_number(min_pay_str)

        percentage_num = compute_percentage(line_val, bal_val)
        percentage_disp = format_percentage_display(percentage_num)

        line_fmt = format_currency(line_val) if line_str else ""
        bal_fmt = format_currency(bal_val) if bal_str else ""
        min_fmt = format_currency(min_val) if min_pay_str else ""

        return account, line_fmt, bal_fmt, percentage_disp, min_fmt, paydate, percentage_num

    def clear_fields(self):
        self.select_account_var.set("")
        self.entry_new_balance.delete(0, tk.END)
        self.entry_new_account.delete(0, tk.END)
        self.entry_line.delete(0, tk.END)
        self.entry_balance.delete(0, tk.END)
        self.entry_min_pay.delete(0, tk.END)
        self.entry_paydate.delete(0, tk.END)

    # ----------------- CRUD actions -----------------

    def add_item(self):
        # Max 20 rows
        if len(self.tree.get_children()) >= 20:
            messagebox.showinfo("Limit reached", "You can only store up to 20 rows.")
            return

        (
            account,
            line,
            balance,
            percentage_disp,
            min_pay,
            paydate,
            percentage_num,
        ) = self.get_entry_data()

        if not account:
            return

        tag = self.get_percentage_tag(percentage_num)

        tags = []
        if tag:
            tags.append(tag)

        self.tree.insert(
            "",
            "end",
            values=(account, line, balance, percentage_disp, min_pay, paydate),
            tags=tuple(tags) if tags else (),
        )

        self.refresh_account_combobox()
        self.save_to_db()
        self.update_summary_chart()
        self.clear_fields()
        # No popup here, just on startup; if you want, change to show_popup=True
        self.check_due_alerts(show_popup=False)

    def update_item(self):
        """
        Edit the balance of the account selected in the combobox,
        using the 'New Balance' field.
        """
        account_to_update = self.select_account_var.get().strip()
        if not account_to_update:
            messagebox.showinfo("Select account", "Please choose an account to edit.")
            return

        new_balance_str = self.entry_new_balance.get().strip()
        if not new_balance_str:
            messagebox.showinfo("New balance", "Please enter a new balance.")
            return

        # Validate numeric balance
        try:
            bal_num = float(new_balance_str)
        except ValueError:
            messagebox.showerror("Invalid value", "Please enter a numeric balance.")
            return

        # Find the row in the Treeview with this account
        target_item = None
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if vals and vals[0] == account_to_update:
                target_item = item
                break

        if target_item is None:
            messagebox.showerror(
                "Not found",
                f"Account '{account_to_update}' was not found in the table.",
            )
            return

        # Get current row values and recalculate percentage
        values = list(self.tree.item(target_item, "values"))
        # values = [account, line, balance, percentage, min_pay, paydate]

        line_num = parse_number(values[1])
        percentage_num = compute_percentage(line_num, bal_num)
        percentage_disp = format_percentage_display(percentage_num)

        # Update balance + percentage
        values[2] = format_currency(bal_num)
        values[3] = percentage_disp

        # Rebuild tags for utilization only
        current_tags = set(self.tree.item(target_item, "tags"))
        current_tags.discard("high_util")
        tag = self.get_percentage_tag(percentage_num)
        if tag:
            current_tags.add(tag)

        # Push back to Treeview
        self.tree.item(target_item, values=values, tags=tuple(current_tags))

        # Visually select and scroll to the updated row
        self.tree.selection_set(target_item)
        self.tree.see(target_item)

        # Clear only the New Balance box
        self.entry_new_balance.delete(0, tk.END)

        # Persist changes + update chart + (silent) alert check
        self.save_to_db()
        self.update_summary_chart()
        self.check_due_alerts(show_popup=False)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        self.tree.delete(selected[0])
        self.refresh_account_combobox()
        self.save_to_db()
        self.update_summary_chart()
        self.clear_fields()
        self.check_due_alerts(show_popup=False)

    # ----------------- Treeview double-click -----------------

    def on_tree_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if not values:
            return

        account, line, balance, percentage, min_pay, paydate = values

        self.entry_new_account.delete(0, tk.END)
        self.entry_new_account.insert(0, account)

        self.entry_line.delete(0, tk.END)
        self.entry_line.insert(0, parse_number(line))

        self.entry_balance.delete(0, tk.END)
        self.entry_balance.insert(0, parse_number(balance))

        self.entry_min_pay.delete(0, tk.END)
        self.entry_min_pay.insert(0, parse_number(min_pay))

        self.entry_paydate.delete(0, tk.END)
        self.entry_paydate.insert(0, paydate)

        self.select_account_var.set(account)
