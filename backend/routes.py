#Imports
from flask import request, render_template, redirect, url_for, session
import os, database

#global variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, f'{"practice"}.db')

#Create a function that will initialize all routes upon running flask.
def initialize_routes(app):
#Recreate the whole CRUD process but using the database now.
    @app.route("/")
    def home():
        print("Current Session ID: ", session.get('id'))
        if "id" in session:
            return redirect(url_for("dashboard"))
        return render_template("home.html")

    #Disabling this due to privacy concerns.
    #@app.route("/view")
    #def check():
    #    users = database.get_users()    
    #    return render_template("view-users.html", users=users)

    @app.route("/edit", methods=["GET"])
    def edit():
        return render_template("edit.html")
    
    @app.route("/edit/search", methods=["POST"])
    def search_user():
        #Query the user to be editted first
        user_id = request.form.get("id")
        user = database.get_user_by_id(user_id)
        if not user:
            return{
                "message":"invalid operation, user does not exist.",
                "status":"error"
            }
        return render_template("edit-form.html",user=user,user_id =user_id)
    
    @app.route("/edit/<user_id>", methods=["POST"])
    def edit_user(user_id):    
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        new_age = request.form.get("age")
        
        if not new_username or not new_password or not new_age:
            return {
                "status": "error",
                "message": "invalid operation, missing input field/s"
            }
        previous_user = database.get_user_by_id(user_id)
        existing_username = database.get_user_by_username(new_username)
        
        if existing_username and new_username.lower() != previous_user['username'].lower():
            return {
                "status": "error",
                "message": "invalid operation, username already in exists"
            }
        database.update_user(new_username, new_password, new_age, user_id)
        return redirect("/view")

    @app.route("/delete", methods=["POST"])
    def delete_user():
        user_id = request.form.get("id")
        user = database.get_user_by_id(user_id)
        if not user: 
            return {
                "message":"user not found",
                "status":"error"
            }
        database.delete_user(user_id)
        return redirect("/view")
    
    @app.route("/register", methods=["GET"])
    def register_form():
        print("Rendering register-form.html...")
        return render_template("register-form.html")
    
    @app.route("/register", methods=["POST"])
    def register_user():
        username = request.form.get("username")
        password = request.form.get("password")
        age = request.form.get("age")
        #Empty input fields
        if not username or not password or not age: 
            return {
                "message":"invalid operation, found missing input fields",
                "status":"error"
            }
        #Check for Duplicate entry
        user = database.get_user_by_username(username)
        if user is not None: 
            return {
                "username":user['username'],
                "message":"invalid operation, found existing username",
                "status":"error"
            }
        database.create_user(username, password, age)
        registered_user = {
            "status":"success",
            "message":"user registered successfully",
            "user":{
                "username":username,
                "age":age,            
            }
        }        
        print(registered_user)
        new_user = database.get_user_by_username(username)
        #Save session as "logged in"
        session['id'] = new_user['id']
        current_user = database.get_user_by_id(session['id'])
        conversations = database.get_user_conversations(session['id'])
        return render_template("dashboard.html", current_user=current_user, conversations=conversations)
    
    @app.route("/login", methods=["GET"])
    def login_form():
        return render_template("login-form.html")
    
    @app.route("/login", methods=["POST"])
    def login_user():
        username = request.form.get("username")
        password = request.form.get("password")
        user = database.get_user_by_username(username)
        if not username or not password:
            return{
                "status":"error",
                "message":"missing input field/s"
            }
        if not user:
            return {
                "status": "error",
                "message": "username does not exist"
        }
        if database.verify_password(username, password):
            session['id'] = user['id']
            return """
            Login Success! Redirecting to dashboard...
            <br>
                <script>
                window.onload = function() {
                    setTimeout(function (){
                        window.location.href="/";
                    }, 1500);
                }
                </script>
            </br 
            """
    @app.route("/logout")
    def logout_user():
        session.clear()
        return """
        User Logged Out Successfully! Redirecting to home page...
        <br>
            <script>
            window.onload = function() {
                setTimeout(function (){
                    window.location.href="/";
                }, 1500);
            }
            </script>
        </br
        """
    @app.route("/dashboard", methods=['GET','POST'])
    def dashboard():
        if "id" not in session:
            return redirect("/login")
        if request.method == "POST":
            pass
        #Query the user dictionary from the database and send it to the rendered template
        current_user = database.get_user_by_id(session['id'])
        conversations = database.get_user_conversations(session['id'])
        messages = ""
        print("DASHBOARD GET REQUEST! SESSION: ",session['id'])
        return render_template("dashboard.html", current_user=current_user, conversations=conversations, messages=messages,current_conversation=None)
       
    @app.route("/dashboard/<int:conversation_id>",methods=['GET','POST'])
    def conversation(conversation_id):
        #This is run when user sends a message.
        if request.method == "POST":
            print("DASHBOARD POST REQUEST! SESSION: ",session['id'])
            current_user = database.get_user_by_id(session['id'])
            other_user = database.get_other_conversation_participant_by_id(conversation_id, current_user['id'])
            current_conversation = database.get_conversation_by_id(conversation_id)
            conversations = database.get_user_conversations(session['id'])
            message_content = request.form.get('input-box')
            database.send_conversation_message(session['id'],conversation_id,message_content)
            messages = database.get_conversation_chat_log(conversation_id)
            return render_template("dashboard.html", current_user=current_user, other_user=other_user,conversations=conversations, messages=messages, current_conversation=current_conversation)

        print("DASHBOARD GET REQUEST! SESSION: ",session['id'])
        current_user = database.get_user_by_id(session['id'])
        other_user = database.get_other_conversation_participant_by_id(conversation_id, current_user['id'])
        conversations = database.get_user_conversations(session['id'])
        messages = database.get_conversation_chat_log(conversation_id)
        return render_template("dashboard.html", current_user=current_user, other_user=other_user, conversations=conversations, messages=messages, current_conversation=None)
        
    @app.route("/dashboard/add-conversation", methods=['POST'])
    def add_conversation():
        queried_user = request.form.get('username')
        queried_user = database.get_user_by_username(queried_user.lower())
        
        current_user = database.get_user_by_id(session['id'])
        print("Session Right now: ", session['id'])
        if queried_user is None:
            return "User does not exist."
        if queried_user["id"] == current_user["id"]:
            return "You can't start a conversation with yourself."
        conversation_id = database.create_conversation(queried_user['username'])
        print("CONVERSATION ID PRINT: ", conversation_id)
        database.add_conversation_participant(queried_user['id'], conversation_id)
        database.add_conversation_participant(current_user['id'], conversation_id)
        return redirect(url_for("dashboard")) 

