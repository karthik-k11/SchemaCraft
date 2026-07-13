from flask import Flask, render_template, request
import os

from database_reader import analyze_database

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"db", "sqlite", "sqlite3"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    analysis = {

        "database_name": "No database loaded",
        "database_size": "--",
        "total_tables": "--",
        "total_views": "--",
        "total_columns": "--",
        "total_rows": "--",
        "tables": []

    }

    if request.method == "POST":

        if "database" not in request.files:

            message = "No file selected."

        else:

            file = request.files["database"]

            if file.filename == "":

                message = "Please choose a database."

            elif allowed_file(file.filename):

                save_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    file.filename
                )

                file.save(save_path)

                analysis = analyze_database(save_path)

                message = "Database analyzed successfully."

            else:

                message = "Only SQLite databases are allowed."

    return render_template(

        "index.html",

        message=message,

        analysis=analysis

    )


if __name__ == "__main__":
    app.run(debug=True)