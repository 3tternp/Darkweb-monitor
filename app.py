from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from flask_bcrypt import Bcrypt
from darkweb_monitor.monitor import DarkWebMonitor
from darkweb_monitor.scheduler import Scheduler
from darkweb_monitor.models import db, User, Result
import json
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('darkweb_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/darkweb_monitor')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load configuration
try:
    with open('darkweb_monitor/config.json', 'r') as f:
        config = json.load(f)
except Exception as e:
    logger.error("Failed to load config: %s", e)
    config = {"urls": [], "query": ""}

monitor = DarkWebMonitor(config.get('urls', []), config.get('query', ''), socketio)
scheduler = Scheduler(monitor)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html', config=config, is_monitoring=scheduler.is_running(), tor_healthy=monitor.check_tor_health())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/update_config', methods=['POST'])
@login_required
def update_config():
    try:
        urls = request.form.get('urls').split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        query = request.form.get('query').strip()
        
        if not urls or not query:
            flash('URLs and query cannot be empty.', 'error')
            return redirect(url_for('index'))
        
        # Update config.json
        new_config = {'urls': urls, 'query': query}
        with open('darkweb_monitor/config.json', 'w') as f:
            json.dump(new_config, f, indent=2)
        
        # Update monitor
        monitor.urls = urls
        monitor.query = query
        
        flash('Configuration updated successfully!', 'success')
    except Exception as e:
        logger.error("Failed to update config: %s", e)
        flash(f'Failed to update configuration: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/results')
@login_required
def results():
    results = Result.query.all()
    return render_template('results.html', results=results)

@app.route('/start_monitoring')
@login_required
def start_monitoring():
    try:
        if not scheduler.is_running():
            scheduler.start()
            flash('Monitoring started successfully!', 'success')
        else:
            flash('Monitoring is already running.', 'info')
    except Exception as e:
        logger.error("Failed to start monitoring: %s", e)
        flash(f'Failed to start monitoring: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/stop_monitoring')
@login_required
def stop_monitoring():
    try:
        if scheduler.is_running():
            scheduler.stop()
            flash('Monitoring stopped successfully!', 'success')
        else:
            flash('Monitoring is not running.', 'info')
    except Exception as e:
        logger.error("Failed to stop monitoring: %s", e)
        flash(f'Failed to stop monitoring: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    if request.method == 'GET':
        return jsonify(config)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            urls = data.get('urls', [])
            query = data.get('query', '')
            if not urls or not query:
                return jsonify({'error': 'URLs and query cannot be empty'}), 400
            new_config = {'urls': urls, 'query': query}
            with open('darkweb_monitor/config.json', 'w') as f:
                json.dump(new_config, f, indent=2)
            monitor.urls = urls
            monitor.query = query
            return jsonify({'message': 'Configuration updated successfully'})
        except Exception as e:
            logger.error("Failed to update config via API: %s", e)
            return jsonify({'error': str(e)}), 500

@app.route('/api/results', methods=['GET'])
@login_required
def api_results():
    results = Result.query.all()
    return jsonify([{'url': r.url, 'content': r.content, 'timestamp': r.timestamp} for r in results])

@app.route('/api/tor_health', methods=['GET'])
@login_required
def tor_health():
    healthy = monitor.check_tor_health()
    return jsonify({'healthy': healthy, 'message': 'Tor is running' if healthy else 'Tor is not responding'})

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        logger.info("WebSocket connected for user %s", current_user.username)
        emit('status', {'is_monitoring': scheduler.is_running()})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000)
