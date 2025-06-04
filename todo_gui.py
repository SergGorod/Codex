import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List
import datetime
import calendar

@dataclass
class Task:
    task_id: int
    description: str
    due_date: str
    status: str

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TODO List")

        self.tasks: List[Task] = []
        self.next_id = 1

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        # Tab for creating a task
        self.create_frame = ttk.Frame(notebook)
        notebook.add(self.create_frame, text="Создать задачу")
        self._build_create_tab()

        # Tab for active tasks
        self.active_frame = ttk.Frame(notebook)
        notebook.add(self.active_frame, text="Активные задачи")
        self.active_tree = self._build_tasks_tab(self.active_frame)

        # Tab for completed tasks
        self.done_frame = ttk.Frame(notebook)
        notebook.add(self.done_frame, text="Завершенные задачи")
        self.done_tree = self._build_tasks_tab(self.done_frame)

        self.refresh_task_views()

    def _build_create_tab(self):
        lbl_desc = ttk.Label(self.create_frame, text="Описание:")
        lbl_desc.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_desc = ttk.Entry(self.create_frame, width=40)
        self.entry_desc.grid(row=0, column=1, padx=5, pady=5)

        lbl_due = ttk.Label(self.create_frame, text="Дата завершения:")
        lbl_due.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_due = ttk.Entry(self.create_frame, width=20)
        self.entry_due.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        btn_cal = ttk.Button(self.create_frame, text="\uD83D\uDCC5", width=3,
                              command=self.open_calendar)
        btn_cal.grid(row=1, column=2, padx=5, pady=5)

        lbl_status = ttk.Label(self.create_frame, text="Статус:")
        lbl_status.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_var = tk.StringVar(value="Open")
        cmb_status = ttk.Combobox(self.create_frame, textvariable=self.status_var,
                                  values=["Open", "In Progress", "Done"], state='readonly')
        cmb_status.grid(row=2, column=1, padx=5, pady=5)

        btn_add = ttk.Button(self.create_frame, text="Добавить", command=self.add_task)
        btn_add.grid(row=3, column=0, columnspan=2, pady=10)

    def open_calendar(self):
        CalendarPopup(self.root, self.entry_due)

    def _build_tasks_tab(self, frame):
        columns = ('ID', 'Описание', 'Дата завершения', 'Статус')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, stretch=True)
        tree.pack(fill='both', expand=True)
        return tree

    def add_task(self):
        desc = self.entry_desc.get().strip()
        due = self.entry_due.get().strip()
        status = self.status_var.get()
        if not desc:
            messagebox.showwarning("Ошибка", "Описание не может быть пустым")
            return
        try:
            datetime.datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД"
            )
            return
        task = Task(self.next_id, desc, due, status)
        self.tasks.append(task)
        self.next_id += 1

        self.entry_desc.delete(0, tk.END)
        self.entry_due.delete(0, tk.END)
        self.status_var.set("Open")
        self.refresh_task_views()

    def refresh_task_views(self):
        for tree in (self.active_tree, self.done_tree):
            for row in tree.get_children():
                tree.delete(row)

        for task in self.tasks:
            if task.status in ("Open", "In Progress"):
                self._insert_task(self.active_tree, task)
            elif task.status == "Done":
                self._insert_task(self.done_tree, task)

    def _insert_task(self, tree, task: Task):
        tree.insert('', 'end', values=(task.task_id, task.description, task.due_date, task.status))


class CalendarPopup:
    def __init__(self, master, entry):
        self.entry = entry
        self.cal = calendar.Calendar()
        today = datetime.date.today()
        self.year = today.year
        self.month = today.month
        self.top = tk.Toplevel(master)
        self.top.title("Выберите дату")
        self._build()

    def _build(self):
        for widget in self.top.winfo_children():
            widget.destroy()

        header = ttk.Frame(self.top)
        header.pack(pady=5)
        ttk.Button(header, text="<", command=self._prev_month).pack(side=tk.LEFT)
        ttk.Label(header, text=f"{self.month:02d}-{self.year}").pack(side=tk.LEFT, padx=10)
        ttk.Button(header, text=">", command=self._next_month).pack(side=tk.LEFT)

        days = ttk.Frame(self.top)
        days.pack()
        for i, name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ttk.Label(days, text=name).grid(row=0, column=i, padx=2, pady=2)

        row = 1
        for week in self.cal.monthdayscalendar(self.year, self.month):
            for col, day in enumerate(week):
                if day == 0:
                    ttk.Label(days, text="").grid(row=row, column=col, padx=2, pady=2)
                else:
                    btn = ttk.Button(days, text=str(day),
                                     command=lambda d=day: self._set_date(d))
                    btn.grid(row=row, column=col, padx=2, pady=2)
            row += 1

    def _prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self._build()

    def _next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self._build()

    def _set_date(self, day: int):
        dt = datetime.date(self.year, self.month, day)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, dt.strftime("%Y-%m-%d"))
        self.top.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
