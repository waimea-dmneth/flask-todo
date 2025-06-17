#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db import connect_db
from app.helpers.errors import register_error_handlers, not_found_error


# Create the app
app = Flask(__name__)

# Setup a session for messages, etc.
init_session(app)

# Handle 404 and 500 errors
# register_error_handlers(app)


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        sql = """
            SELECT *
            FROM tasks
            WHERE complete=?
            ORDER BY priority DESC
        """
        values = [0]
        tasks = client.execute(sql, values)
        aTasks = tasks.rows

        sql = """
            SELECT *
            FROM tasks
            WHERE complete!=?
            ORDER BY name ASC
        """
        tasks = client.execute(sql, values)
        inaTasks = tasks.rows
        
        return render_template("pages/home.jinja", aTasks = aTasks, inaTasks = inaTasks)
    
@app.get("/edit/<int:id>")
def editPage(id):
    with connect_db() as client:
        sql = "SELECT id, complete, name, priority FROM tasks WHERE id=?"
        values = [id]
        result = client.execute(sql,values)
        thing = result.rows[0]

        return render_template("pages/edit.jinja",thing = thing)
    
@app.get("/new")
def newTaskPage():
    return render_template("pages/new.jinja")

@app.post("/update/<int:id>")
def updateDB(id):
    with connect_db() as client:
        complete = request.form.get("complete")
        if not complete :
            complete = 0
        else:
            complete = 1
        sql = """
            UPDATE tasks 
            SET name=?, priority=?, complete=?
            WHERE id=?
        """
        values= [request.form.get("name"), request.form.get("priority"),complete , id]
        client.execute(sql,values)
        return redirect("/")

@app.get("/complete/<int:id>")
def completeTask(id):
    with connect_db() as client:
        sql = """
            UPDATE tasks 
            SET complete=?
            WHERE id=?
        """
        values= [1,id]
        client.execute(sql,values)
        return redirect("/")
    
@app.get("/restore/<int:id>")
def restoreTask(id):
    with connect_db() as client:
        sql = """
            UPDATE tasks 
            SET complete=?
            WHERE id=?
        """
        values= [0,id]
        client.execute(sql,values)
        return redirect("/")

@app.get("/delete/<int:id>")
def deleteTask(id):
    with connect_db() as client:
        sql = """
            DELETE FROM tasks 
            WHERE id=?
        """
        values= [id]
        client.execute(sql,values)
        return redirect("/")

#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def addTasks():
    # Get the data from the form
    name  = request.form.get("name")
    priority = request.form.get("priority")

    # Sanitize the inputs
    name = html.escape(name)
    priority = html.escape(priority)

    with connect_db() as client:
        sql = "INSERT INTO tasks (name, priority) VALUES (?, ?)"
        values = [name, priority]
        client.execute(sql, values)

        flash(f"Task '{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        values = [id]
        client.execute(sql, values)

        # Go back to the home page
        flash("Task deleted", "warning")
        return redirect("/")


