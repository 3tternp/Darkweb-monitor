from setuptools import setup, find_packages

setup(
    name="darkweb-monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests==2.28.1',
        'beautifulsoup4==4.11.1',
        'pyTelegramBotAPI==4.7.0',
        'python-dotenv==0.21.0',
        'flask==2.2.2',
        'flask-login==0.6.2',
        'flask-sqlalchemy==3.0.2',
        'flask-socketio==5.3.2',
        'flask-bcrypt==1.0.1',
        'psycopg2-binary==2.9.5',
    ],
    include_package_data=True,
    package_data={
        'darkweb_monitor': ['templates/*.html', 'static/css/*.css', 'static/js/*.js', 'config.json'],
    },
    author="3tternp",
    author_email="your.email@example.com",
    description="A web-based dark web monitoring tool with authentication, PostgreSQL, and real-time updates",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/3tternp/Darkweb-monitor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'darkweb-monitor=darkweb_monitor.app:main',
        ],
    },
)
