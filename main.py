# main.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from typing import List, Dict

TASKS_FILE = "tasks.json"

# --- Temas ---
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "entry_bg": "#ffffff",
        "btn_add": "#4CAF50",
        "btn_done": "#2196F3",
        "btn_del": "#f44336",
        "list_bg": "#ffffff",
        "list_fg": "#000000",
        "list_select": "#bde0fe"
    },
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "entry_bg": "#3c3f41",
        "btn_add": "#66bb6a",
        "btn_done": "#42a5f5",
        "btn_del": "#ef5350",
        "list_bg": "#3c3f41",
        "list_fg": "#ffffff",
        "list_select": "#37474f"
    }
}

# --- Cargar/Guardar ---
def load_tasks() -> List[Dict]:
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks: List[Dict]):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# --- App ---
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do App")
        self.root.geometry("520x680")
        self.root.resizable(False, False)
        self.tasks = load_tasks()
        self.current_theme = "light"
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # === Crear widgets ===
        self.title_lbl = tk.Label(self.root, text="Mis Tareas", font=("Helvetica", 18, "bold"))
        self.title_lbl.pack(pady=12)

        # Entrada + botones
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=8, fill=tk.X, padx=20)
        self.top_frame = top_frame

        self.entry = tk.Entry(top_frame, font=("Helvetica", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.add_task())

        self.add_btn = tk.Button(top_frame, text="Añadir", command=self.add_task, width=10)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.theme_btn = tk.Button(top_frame, text="Dark", command=self.toggle_theme, width=8)
        self.theme_btn.pack(side=tk.RIGHT)

        # Lista
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.list_frame = list_frame

        self.listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 11),
            selectmode=tk.SINGLE,
            activestyle="none",
            height=20
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-1>", self.edit_task)

        # Botones acción
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        self.btn_frame = btn_frame

        self.done_btn = tk.Button(btn_frame, text="Completar", command=self.mark_done, width=12)
        self.done_btn.pack(side=tk.LEFT, padx=8)

        self.del_btn = tk.Button(btn_frame, text="Eliminar", command=self.delete_task, width=12)
        self.del_btn.pack(side=tk.LEFT, padx=8)

        # Footer
        self.footer = tk.Label(self.root, text="Doble clic para editar", font=("Helvetica", 8))
        self.footer.pack(side=tk.BOTTOM, pady=10)

        # Aplicar tema
        self.apply_theme()

    def apply_theme(self):
        theme = THEMES[self.current_theme]
        self.root.configure(bg=theme["bg"])

        # Aplicar a TODOS los contenedores
        for frame in [self.top_frame, self.list_frame, self.btn_frame]:
            frame.configure(bg=theme["bg"])

        for widget in [self.title_lbl, self.footer]:
            widget.configure(bg=theme["bg"], fg=theme["fg"])

        self.entry.configure(
            bg=theme["entry_bg"],
            fg=theme["fg"],
            insertbackground=theme["fg"]
        )

        self.add_btn.configure(bg=theme["btn_add"], fg="white")
        self.done_btn.configure(bg=theme["btn_done"], fg="white")
        self.del_btn.configure(bg=theme["btn_del"], fg="white")

        self.listbox.configure(
            bg=theme["list_bg"],
            fg=theme["list_fg"],
            selectbackground=theme["list_select"]
        )

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.theme_btn.configure(text="Light" if self.current_theme == "dark" else "Dark")
        self.apply_theme()
        self.refresh_list()

    def add_task(self):
        desc = self.entry.get().strip()
        if not desc:
            messagebox.showwarning("Error", "Escribe una tarea.")
            return
        task = {"id": len(self.tasks) + 1, "description": desc, "done": False}
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.entry.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for t in self.tasks:
            status = "Done" if t["done"] else "Pending"
            text = f"{status} {t['id']}. {t['description']}"
            self.listbox.insert(tk.END, text)
            if t["done"]:
                color = "#888888" if self.current_theme == "light" else "#bbbbbb"
                self.listbox.itemconfig(tk.END, fg=color)

    def get_selected_id(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Error", "Selecciona una tarea.")
            return None
        line = self.listbox.get(sel[0])
        try:
            return int(line.split(".")[0].split()[-1])
        except:
            return None

    def mark_done(self):
        task_id = self.get_selected_id()
        if not task_id: return
        for t in self.tasks:
            if t["id"] == task_id:
                t["done"] = True
                break
        save_tasks(self.tasks)
        self.refresh_list()

    def delete_task(self):
        task_id = self.get_selected_id()
        if not task_id: return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta tarea?"):
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            for i, t in enumerate(self.tasks, 1):
                t["id"] = i
            save_tasks(self.tasks)
            self.refresh_list()

    def edit_task(self, event):
        task_id = self.get_selected_id()
        if not task_id: return
        for t in self.tasks:
            if t["id"] == task_id:
                new_desc = simpledialog.askstring("Editar tarea", "Nueva descripción:", initialvalue=t["description"])
                if new_desc and new_desc.strip():
                    t["description"] = new_desc.strip()
                    save_tasks(self.tasks)
                    self.refresh_list()
                break

# --- Ejecutar ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()