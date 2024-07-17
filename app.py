from flask import Flask, request, jsonify
from pymongo import MongoClient


import tkinter as tk
from tkinter import messagebox
import pickle

app = Flask(__name__)

try:
    client = MongoClient('localhost', 27017)
    db = client.todo_db
    todos = db.todos
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = list(todos.find({}))
    for task in tasks:
        task['_id'] = str(task['_id'])
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    task = request.json
    todos.insert_one(task)
    task['_id'] = str(task['_id'])
    return jsonify(task), 201

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")

        self.tasks = []

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.listbox = tk.Listbox(
            self.frame, height=15, width=50, selectmode=tk.SINGLE
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.add_button = tk.Button(
            self.button_frame, text="Add Task", command=self.add_task
        )
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.update_button = tk.Button(
            self.button_frame, text="Update Task", command=self.update_task
        )
        self.update_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(
            self.button_frame, text="Delete Task", command=self.delete_task
        )
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.status_button = tk.Button(
            self.button_frame, text="Toggle Status", command=self.toggle_status
        )
        self.status_button.pack(side=tk.LEFT, padx=10)

        self.load_tasks()

    def add_task(self):
        task = self.entry.get()
        if task != "":
            self.tasks.append({"task": task, "status": "Incomplete"})
            self.listbox.insert(tk.END, f"{task} - Incomplete")
            self.entry.delete(0, tk.END)
            self.save_tasks()
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def update_task(self):
        try:
            selected_task_index = self.listbox.curselection()[0]
            new_task = self.entry.get()
            if new_task != "":
                status = self.tasks[selected_task_index]["status"]
                self.tasks[selected_task_index] = {"task": new_task, "status": status}
                self.listbox.delete(selected_task_index)
                self.listbox.insert(
                    selected_task_index, f"{new_task} - {status}"
                )
                self.entry.delete(0, tk.END)
                self.save_tasks()
            else:
                messagebox.showwarning("Warning", "You must enter a task.")
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task.")

    def delete_task(self):
        try:
            selected_task_index = self.listbox.curselection()[0]
            self.listbox.delete(selected_task_index)
            del self.tasks[selected_task_index]
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task.")

    def toggle_status(self):
        try:
            selected_task_index = self.listbox.curselection()[0]
            task = self.tasks[selected_task_index]["task"]
            current_status = self.tasks[selected_task_index]["status"]
            new_status = "Complete" if current_status == "Incomplete" else "Incomplete"
            self.tasks[selected_task_index]["status"] = new_status
            self.listbox.delete(selected_task_index)
            self.listbox.insert(
                selected_task_index, f"{task} - {new_status}"
            )
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task.")

    def save_tasks(self):
        with open("tasks.pkl", "wb") as f:
            pickle.dump(self.tasks, f)

    def load_tasks(self):
        try:
            with open("tasks.pkl", "rb") as f:
                self.tasks = pickle.load(f)
                for task in self.tasks:
                    if isinstance(task, dict) and "task" in task and "status" in task:
                        self.listbox.insert(tk.END, f"{task['task']} - {task['status']}")
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showwarning("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
