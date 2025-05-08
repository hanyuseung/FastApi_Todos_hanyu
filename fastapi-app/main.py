import os, json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

TODO_FILE = "todo.json"

class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    priority: int
    todayFlag: bool = False    # 새로 추가된 필드, 기본값 False

class TodoStatusUpdate(BaseModel):
    completed: bool

def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "r") as f:
                todos = json.load(f)
        except json.JSONDecodeError:
            todos = []
    else:
        todos = []
    # 기존 항목에 todayFlag 누락 시 기본값 설정
    for todo in todos:
        if "todayFlag" not in todo:
            todo["todayFlag"] = False
    return todos

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=4)

@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated: TodoItem):
    todos = load_todos()
    for i, td in enumerate(todos):
        if td["id"] == todo_id:
            todos[i] = updated.dict()
            save_todos(todos)
            return updated
    raise HTTPException(404, "To-Do item not found")

@app.patch("/todos/{todo_id}/completed", response_model=TodoItem)
def update_todo_completed(todo_id: int, status: TodoStatusUpdate):
    todos = load_todos()
    for td in todos:
        if td["id"] == todo_id:
            td["completed"] = status.completed
            save_todos(todos)
            return td
    raise HTTPException(404, "To-Do item not found")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = [td for td in load_todos() if td["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
