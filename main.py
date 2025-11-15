import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from typing import List, Dict

TASKS_FILE = "tasks.json"

# --- Persistencia ---
def load_tasks() -> List[Dict]:
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks: List[Dict]):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# --- App GUI ---
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do App")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")

        self.tasks = load_tasks()
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # Título
        title = tk.Label(self.root, text="Mis Tareas", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
        title.pack(pady=10)

        # Frame entrada
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(pady=5, fill=tk.X, padx=20)

        self.entry = tk.Entry(input_frame, font=("Helvetica", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda e: self.add_task())

        add_btn = tk.Button(input_frame, text="Añadir", command=self.add_task, bg="#4CAF50", fg="white")
        add_btn.pack(side=tk.RIGHT)

        # Lista de tareas
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.listbox = tk.Listbox(list_frame, font=("Helvetica", 11), selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Botones
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=5)

        done_btn = tk.Button(btn_frame, text="✓ Completar", command=self.mark_done, bg="#2196F3", fg="white")
        done_btn.pack(side=tk.LEFT, padx=5)

        del_btn = tk.Button(btn_frame, text="Eliminar", command=self.delete_task, bg="#f44336", fg="white")
        del_btn.pack(side=tk.LEFT, padx=5)

    def add_task(self):
        desc = self.entry.get().strip()
        if not desc:
            messagebox.showwarning("Error", "Escribe una tarea.")
            return
        task = {
            "id": len(self.tasks) + 1,
            "description": desc,
            "done": False
        }
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.entry.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for t in self.tasks:
            status = "✓" if t["done"] else "○"
            text = f"{status} {t['id']}. {t['description']}"
            self.listbox.insert(tk.END, text)
            if t["done"]:
                self.listbox.itemconfig(tk.END, {'fg': 'gray'})

    def get_selected_id(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Error", "Selecciona una tarea.")
            return None
        line = self.listbox.get(selection[0])
        task_id = int(line.split(".")[0].split()[-1])
        return task_id

    def mark_done(self):
        task_id = self.get_selected_id()
        if task_id is None:
            return
        for t in self.tasks:
            if t["id"] == task_id:
                t["done"] = True
                break
        save_tasks(self.tasks)
        self.refresh_list()

    def delete_task(self):
        task_id = self.get_selected_id()
        if task_id is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta tarea?"):
            return
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        # Reasignar IDs
        for i, t in enumerate(self.tasks, 1):
            t["id"] = i
        save_tasks(self.tasks)
        self.refresh_list()

# --- Ejecutar ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()