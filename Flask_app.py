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
    author_info = {
        'display_name': '',
        'works_count': '',
        'cited_by_count': '',
        'topics': ''

    } 

    if request.method == "POST":
        author_name = request.form["author"]
        fig = generate_similar_authors_map(author_name)
        script, div = components(fig)
        author_info = API_call.get_author_info(author_name)

    return render_template(
        "index.html",
        script=script,
        div=div,
        author_info = author_info
    )

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)