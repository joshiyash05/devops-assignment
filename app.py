from flask import Flask, jsonify


app = Flask(__name__)


@app.get("/health")
def health_check():
    return jsonify({"service": "ACEest Fitness API", "status": "ok"})


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Welcome to ACEest Fitness & Gym API",
            "endpoints": ["/health"],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
