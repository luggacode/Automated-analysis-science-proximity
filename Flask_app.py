from flask import Flask, render_template, request
from bokeh.embed import components
import API_call
import useful_methods
from find_similar_authors import generate_similar_authors_map

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    script, div = None, None

    if request.method == "POST":
        author_name = request.form["author"]
        fig = generate_similar_authors_map(author_name)
        script, div = components(fig)

    return render_template(
        "index.html",
        script=script,
        div=div
    )

if __name__ == "__main__":
    app.run(debug=True)
