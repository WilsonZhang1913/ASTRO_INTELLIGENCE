from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/astro_intelligence")
def home():
    return render_template("index.html")

@app.route("/author")
def author():
    return render_template("author.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
