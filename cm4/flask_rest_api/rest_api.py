from cm4.flask_rest_api.app import app

if __name__ == "__main__":
    app.start(debug=True, threaded=True, host='127.0.0.1')
