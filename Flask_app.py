from flask import Flask, render_template, request
from bokeh.embed import components
import API_call
import useful_methods
import os
from find_similar_authors import generate_similar_authors_map, create_empty_map

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    fig = create_empty_map()
    script, div = components(fig)

    if request.method == "POST":
        author_name = request.form["author"]
        fig = generate_similar_authors_map(author_name)
        script, div = components(fig)
        print("Returning template with script length:", len(script))

    return render_template(
        "index.html",
        script=script,
        div=div
    )

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)