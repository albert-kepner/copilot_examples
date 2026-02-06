from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("home.html", title="Home", active_page="home")


@app.get("/about")
def about():
    return render_template("about.html", title="About", active_page="about")


@app.get("/contact")
def contact():
    return render_template("contact.html", title="Contact", active_page="contact")


if __name__ == "__main__":
    app.run(debug=True)
