from flask import request, render_template

#Dummy Database as Usual. 
users = {
    "enzo":{
        "first name":"enzo",
        "last name":"pogi",
    }
}
def initialize_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")
    @app.route("/view")
    def view_users():
        return render_template("view-users.html", users=users)
#Lets focus on CRUD routes for now.
    @app.route("/create", methods=["POST"])
    def create_user():
        #Retrieving the inputted information from the html file.
        first_name = request.form.get("fname").lower()
        last_name = request.form.get("lname").lower()

        if not first_name or not last_name:
            return {
            "status":"error",
            "message":"missing input details",
            }
        #Create a dict template to store inside the temporary database
        user = {
            "first name":first_name,
            "last name":last_name,
        }
        #Check for duplicate entry, prevent from overwriting existing data
        if first_name in users:
            return {
                "status":"error",
                "message":"user is already existing",    
            }
        #It should look like (Enzo (name) -> First name: Enzo, Last Name: Magnolia)
        users[first_name] = user
        #Print the created user information in JSON format for now.
        return {
            "message":"user creation success",
            first_name:users[first_name]
        }
    @app.route("/create", methods=["GET"])
    def create_form():
        return render_template("create-form.html")
    
    @app.route("/edit", methods=["GET"])
    def edit():
        return render_template("edit.html")
    #This route will be responsible for checking if the submitted username is existing, before proceeding to edit.
    @app.route("/edit/search", methods=["POST"])
    def search_user():
        #ENZO, DAPAT GUMAMET KA NG POST PARA MA RECOGNIZE AND MAKUHA NILA YUNG INPUT DITO SA PART NA REQUEST.FORM.GET("FNAME") POTEK
        username = request.form.get("fname").lower()
        if not username:
            return {
                "status":"error",
                "message":"missing input details",
            }
        if username not in users:
            return {
                "status":"error",
                "message":"user does not exist",
            }
        #user is the user we are sending to the html which is gonna refer to the current user that we are modifying from the temporary database
        return render_template("edit-form.html", user=username)
    @app.route("/edit/<name>", methods=["POST"])
    def edit_user(name):
        new_fname = request.form.get("fname").lower()
        new_lname = request.form.get("lname").lower()
        
        #Prevent the user from inputting empty fields.
        if not new_fname or not new_lname:
            return {
                "status": "error",
                "message": "missing fields"
            }
        updated_user = {
            "first name": new_fname,
            "last name": new_lname,
        }
        users.pop(name)
        users[new_fname] = updated_user
        return{
            "message":"user update success",
            "data":users[new_fname],
        }
    @app.route("/delete")
    def delete():
        return render_template("delete.html")
    @app.route("/delete", methods=["POST"])
    def search_delete_user():
        user = request.form.get("fname").lower()
        if not user:
            return {
                "status":"error",
                "message":"missing input details",
            }
        if user not in users:
            return {
                "status":"error",
                "message":"user does not exist",
            }
        users.pop(user)
        return render_template("delete-form.html")

    @app.route("/home2")
    def home2():
        return render_template("/prototype-home.html")