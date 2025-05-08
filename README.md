# Darkweb Monitor

Darkweb Monitor is an open-source, web-based Python application for monitoring .onion sites on the Tor network. It features user authentication with bcrypt, a PostgreSQL database, REST API, real-time WebSocket updates, and Tor health checks. The app is containerized with Docker, installable via pip, and includes CI/CD via GitHub Actions.

## Features
- Secure authentication with Flask-Login and bcrypt
- PostgreSQL database for storing results
- REST API for programmatic access
- Real-time result updates via WebSockets
- Tor health check for connectivity
- Background task scheduling for continuous monitoring
- Monitors .onion URLs for keywords
- Telegram notifications for matches
- Dockerized deployment
- Installable Python package
- Unit tests and GitHub Actions CI

## Prerequisites
- Docker (for containerized deployment)
- Python 3.6+ (for local development)
- Tor service (local or proxy)
- PostgreSQL server
- Telegram bot token and chat ID
- GitHub account (for repository hosting)

## Installation

### Option 1: Docker
1. **Clone the Repository**
   ```bash
   git clone https://github.com/3tternp/Darkweb-monitor.git
   cd Darkweb-monitor

   Configure Environment VariablesCopy .env.example to .env and update:

cp .env.example .env

Edit .env:

FLASK_SECRET_KEY=your_secret_key
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TOR_PROXY=socks5h://127.0.0.1:9050
CHECK_INTERVAL=900
MAX_THREADS=5
DATABASE_URL=postgresql://user:password@localhost:5432/darkweb_monitor


Set Up PostgreSQL


Install and run PostgreSQL locally or use a cloud provider.


Create a database:

psql -U postgres -c "CREATE DATABASE darkweb_monitor;"


Build and Run

docker build -t darkweb-monitor .
docker run -d -p 5000:5000 --name darkweb-monitor darkweb-monitor


Access the Web InterfaceOpen http://localhost:5000. Register a new user or log in.

Option 2: Local Installation

Clone the Repository

git clone https://github.com/3tternp/Darkweb-monitor.git
cd Darkweb-monitor


Install Dependencies

pip install .



Configure Environment VariablesCopy .env.example to .env and update.


Set Up PostgreSQL


Install PostgreSQL and create a database as above.


Update DATABASE_URL in .env.


Initialize Database

python -c "from darkweb_monitor.app import db; db.create_all()"


Run the Application

darkweb-monitor

Or:

python -m darkweb_monitor.app

Access the Web InterfaceOpen http://localhost:5000. Register a new user or log in.

Deployment

Local Deployment

Follow the Docker or local installation steps above. Ensure Tor and PostgreSQL are running.

Cloud Deployment (Heroku)


Install Heroku CLIDownload from Heroku CLI.

Create a Heroku App

heroku create your-app-name


Add Heroku Buildpacks

heroku buildpacks:set heroku/python
heroku buildpacks:add heroku/postgresql

Configure Environment Variables

heroku config:set FLASK_SECRET_KEY=your_secret_key
heroku config:set TELEGRAM_TOKEN=your_telegram_bot_token
heroku config:set TELEGRAM_CHAT_ID=your_telegram_chat_id
heroku config:set TOR_PROXY=socks5h://your-vps-ip:9050
heroku config:set CHECK_INTERVAL=900
heroku config:set MAX_THREADS=5

Heroku automatically sets DATABASE_URL for PostgreSQL.

Deploy to Heroku

git push heroku main

Open the App

heroku open

Note: Configure an external Tor proxy for Heroku.

Tor Proxy Setup


Local Tor Proxy


Install Tor:

sudo apt-get install tor


Start Tor:

sudo service tor start


Verify: TOR_PROXY=socks5h://127.0.0.1:9050.


VPS Tor Proxy



Rent a VPS (e.g., AWS, DigitalOcean).


Install Tor:

sudo apt-get update
sudo apt-get install tor


Configure /etc/tor/torrc:

SocksPort 0.0.0.0:9050


Restart Tor:

sudo service tor restart


Update .env:

TOR_PROXY=socks5h://<vps-ip>:9050

Usage


Register/Login:



Go to /register to create an account.


Log in at /login.


Configure Monitoring:

Go to /.



Enter .onion URLs and a query.



Click "Update Configuration".



Start/Stop Monitoring:



Click "Start Monitoring" (runs every 15 minutes).


Click "Stop Monitoring" to pause.


View Results:


Go to /results to see scraped data (updates in real-time).



API Access:



GET /api/config: Retrieve configuration.


POST /api/config: Update configuration (JSON: {"urls": [], "query": ""}).



GET /api/results: Retrieve results.



GET /api/tor_health: Check Tor connectivity.

Testing

Run unit tests:

python -m unittest discover -s tests -v
