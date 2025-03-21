from flask import Flask, render_template, request, send_from_directory
from api import api_blueprint
from flask_cors import CORS
import os

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

CORS(app)
app.debug = True

app.register_blueprint(api_blueprint, url_prefix='/api')

@app.before_request
def log_routes():
    print(f"Requested URL: {request.url}")
    print(f"Request Method: {request.method}")

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/search.html')
def search():
    return render_template('search.html')

@app.route('/restaurant.html')
def restaurant():
    return render_template('restaurant.html')

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory(os.path.join(app.static_folder, 'images'), filename)
    except:
        return send_from_directory(app.static_folder, 'placeholder.jpg')

if __name__ == '__main__':  # Fixed to use correct double underscores
    print("Starting Flask server...")
    host = '127.0.0.1'
    port = 5000
    print(f"\n{'='*50}")
    print(f"Server is running at: http://{host}:{port}")
    print(f"Open this URL in your web browser")
    print(f"{'='*50}\n")
    try:
        app.run(host=host, port=port, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")