from flask import Flask
from dotenv import load_dotenv
import os
import routes

load_dotenv()

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Register routes for both Render and local execution
routes.initialize_routes(app)

if __name__ == "__main__":
    app.run(debug=True)