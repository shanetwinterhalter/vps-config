from flask import Flask

app = Flask(__name__)


@app.route('/github', methods=["POST"])
def gh_webhook_listener():
    pass


if __name__ == '__main__':
    app.run(debug=True, port=5009)
