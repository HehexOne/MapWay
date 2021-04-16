from flask import Flask, request, render_template, url_for
import json


app = Flask(__name__)

data = json.load(open("cities.json", "r", encoding="UTF-8"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predictor")
def api_predictor():
    query = request.args.get("query", None)
    result = {"response": []}
    if query:
        query = query.lower()
        result_objects = [obj for obj in data["data"] if obj["name"].lower().startswith(query)]
        result["response"] = result_objects
        return json.dumps(result)
    else:
        return "{\"response\":[{\"name\":\"Начните вводить запрос\"}]}"


if __name__ == '__main__':
    app.run("0.0.0.0", 3000)
