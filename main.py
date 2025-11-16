# main.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from typing import List, Dict
import sys
import tempfile
import csv
from datetime import datetime

# --- DPI Awareness ---
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

TASKS_FILE = "tasks.json"

# --- Temas ---
THEMES = {
    "light": {
        "bg": "#f0f0f0", "fg": "#000000", "entry_bg": "#ffffff",
        "btn_add": "#4CAF50", "btn_done": "#2196F3", "btn_del": "#f44336",
        "text_bg": "#ffffff", "text_fg": "#000000", "text_select": "#bde0fe"
    },
    "dark": {
        "bg": "#2b2b2b", "fg": "#ffffff", "entry_bg": "#3c3f41",
        "btn_add": "#66bb6a", "btn_done": "#42a5f5", "btn_del": "#ef5350",
        "text_bg": "#3c3f41", "text_fg": "#ffffff", "text_select": "#37474f"
    }
}

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

        # Icono (ruta absoluta + fallback)
        icon_path = resource_path("app.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
                self.root.update_idletasks()  # Forzar actualización
            except Exception as e:
                print(f"Error cargando icono: {e}")
        else:
            print("app.ico no encontrado en:", icon_path)

        # Ventana
        width, height = 600, 700
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)

        self.tasks = load_tasks()
        self.current_theme = "light"
        self.setup_ui()
        self.apply_theme()  # ← Después de crear todos los widgets
        self.refresh_list()

    def setup_ui(self):
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Título
        self.title_lbl = tk.Label(self.root, text="Mis Tareas", font=("Helvetica", 18, "bold"))
        self.title_lbl.grid(row=0, column=0, pady=12, sticky="ew")

        # Entrada
        self.top_frame = tk.Frame(self.root)  # ← CREAR ANTES
        self.top_frame.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.entry = tk.Entry(self.top_frame, font=("Helvetica", 12))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.add_task())

        self.add_btn = tk.Button(self.top_frame, text="Añadir", command=self.add_task, width=10)
        self.add_btn.grid(row=0, column=1, padx=(0, 8))

        self.theme_btn = tk.Button(self.top_frame, text="Dark", command=self.toggle_theme, width=8)
        self.theme_btn.grid(row=0, column=2)

        # Text + Scroll
        text_frame = tk.Frame(self.root)
        text_frame.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="nsew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(
            text_frame,
            font=("Consolas", 11),
            wrap="none",
            state="normal",  # ← PERMITE SELECCIÓN
            spacing1=2,
            spacing3=2
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        # BLOQUEAR EDICIÓN (solo lectura)
        self.text.bind("<Key>", lambda e: "break")  # Bloquea teclado
        self.text.bind("<Button-1>", self.on_text_click)  # Detecta clic
        self.text.bind("<Double-1>", self.edit_task)

        v_scroll = tk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=v_scroll.set)

        h_scroll = tk.Scrollbar(self.root, orient="horizontal", command=self.text.xview)
        h_scroll.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 5))
        self.text.configure(xscrollcommand=h_scroll.set)

        # Botones
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.grid(row=5, column=0, pady=5, sticky="ew")
        self.btn_frame.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(1, weight=1)

        self.done_btn = tk.Button(self.btn_frame, text="Completar", command=self.mark_done, width=12)
        self.done_btn.grid(row=0, column=0, padx=8, sticky="e")

        self.del_btn = tk.Button(self.btn_frame, text="Eliminar", command=self.delete_task, width=12)
        self.del_btn.grid(row=0, column=1, padx=8, sticky="w")

        # Botón Exportar
        self.export_btn = tk.Button(self.btn_frame, text="Exportar CSV", command=self.export_to_csv, width=14)
        self.export_btn.grid(row=0, column=2, padx=8, sticky="w")

        # Footer
        self.footer = tk.Label(self.root, text="Doble clic para editar", font=("Helvetica", 8))
        self.footer.grid(row=6, column=0, pady=10, sticky="ew")

    def apply_theme(self):
        theme = THEMES[self.current_theme]
        self.root.configure(bg=theme["bg"])

        # Aplicar fondo a frames
        for widget in [self.top_frame, self.text.master, self.btn_frame]:
            widget.configure(bg=theme["bg"])

        # Título y footer: fondo + texto
        self.title_lbl.configure(bg=theme["bg"], fg=theme["fg"])
        self.footer.configure(bg=theme["bg"], fg=theme["fg"])

        # Entrada
        self.entry.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])

        # Botones
        self.add_btn.configure(bg=theme["btn_add"], fg="white", activebackground=theme["btn_add"])
        self.done_btn.configure(bg=theme["btn_done"], fg="white", activebackground=theme["btn_done"])
        self.del_btn.configure(bg=theme["btn_del"], fg="white", activebackground=theme["btn_del"])
        self.theme_btn.configure(bg="#555555" if self.current_theme == "dark" else "#333333", fg="white")
        self.export_btn.configure(bg="#FF9800", fg="white", activebackground="#e68900")

        # Text
        self.text.configure(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            selectbackground=theme["text_select"],
            insertbackground=theme["text_fg"]
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
        self.tasks.append({"id": len(self.tasks) + 1, "description": desc, "done": False})
        save_tasks(self.tasks)
        self.entry.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self):
        self.text.configure(state="normal")  # ← Siempre normal, permite selección
        self.text.delete("1.0", tk.END)
        for t in self.tasks:
            status = "✓" if t["done"] else "○"
            line = f"{status} {t['id']}. {t['description']}\n"
            start = self.text.index(tk.END)
            self.text.insert(tk.END, line)
            if t["done"]:
                self.text.tag_add("done", start, self.text.index(tk.END))
        self.text.tag_config("done", foreground="#888888" if self.current_theme == "light" else "#bbbbbb")
        self.text.see("end")

    def get_selected_task_id(self):
        try:
            if self.text.tag_ranges("sel"):
                line = self.text.get("sel.first linestart", "sel.first lineend")
            else:
                # Fallback: línea bajo el cursor
                line = self.text.get("insert linestart", "insert lineend")
            return int(line.split(".")[0].split()[-1])
        except Exception as e:
            messagebox.showwarning("Error", "Selecciona una tarea.")
            return None

    def mark_done(self):
        if (tid := self.get_selected_task_id()):
            for t in self.tasks:
                if t["id"] == tid:
                    t["done"] = True
                    break
            save_tasks(self.tasks)
            self.refresh_list()

    def delete_task(self):
        if (tid := self.get_selected_task_id()) and messagebox.askyesno("Confirmar", "¿Eliminar?"):
            self.tasks = [t for t in self.tasks if t["id"] != tid]
            for i, t in enumerate(self.tasks, 1):
                t["id"] = i
            save_tasks(self.tasks)
            self.refresh_list()

    def edit_task(self, event):
        if (tid := self.get_selected_task_id()):
            for t in self.tasks:
                if t["id"] == tid:
                    if (new := simpledialog.askstring("Editar", "Nueva descripción:", initialvalue=t["description"])) and new.strip():
                        t["description"] = new.strip()
                        save_tasks(self.tasks)
                        self.refresh_list()
                    break
    
    def on_text_click(self, event):
        self.text.focus_set()
        # Forzar selección de línea completa
        line_start = self.text.index(f"@{event.x},{event.y} linestart")
        line_end = self.text.index(f"@{event.x},{event.y} lineend")
        self.text.tag_remove("sel", "1.0", "end")
        self.text.tag_add("sel", line_start, line_end)
        return "break"
    
    def export_to_csv(self):
        if not self.tasks:
            messagebox.showinfo("Exportar", "No hay tareas para exportar.")
            return

        # Nombre de archivo con fecha/hora
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"tasks_export_{timestamp}.csv"

        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Estado", "Descripción"])  # Cabecera
                for t in self.tasks:
                    status = "Completada" if t["done"] else "Pendiente"
                    writer.writerow([t["id"], status, t["description"]])
            messagebox.showinfo("Exportar CSV", f"Exportado correctamente:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

    # --- ÍCONO EN .EXE (PyInstaller) ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        # PyInstaller crea carpeta temporal y almacena path en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



# --- Ejecutar ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()