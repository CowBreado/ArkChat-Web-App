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

app.secret_key = os.getenv("SECRET_KEY")

if __name__ == "__main__":
    routes.initialize_routes(app)
    app.run(debug=True)