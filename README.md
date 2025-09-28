# EcoShakti - Renewable Energy Monitoring System 🌱⚡

A comprehensive web application for monitoring and analyzing renewable energy systems, including solar panels and wind turbines. EcoShakti provides real-time data visualization, AI-powered analytics, fault detection, and energy optimization.

![EcoShakti Dashboard](https://img.shields.io/badge/Status-Active-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### 🔄 Real-time Monitoring
- Live metrics on solar/wind generation, consumption, and battery storage
- WebSocket-powered real-time updates
- Interactive dashboards with Plotly.js visualizations

### 🤖 AI-Powered Analytics
- PyTorch-based machine learning models for forecasting
- Automated fault detection and anomaly analysis
- Predictive maintenance recommendations

### 📊 Advanced Analytics
- Correlation analysis (sun intensity vs. solar output)
- Historical trend analysis and benchmarking
- Energy efficiency optimization insights

### 🚨 Intelligent Alerts
- Automated detection of system faults
- Low battery and energy imbalance warnings
- Customizable alert thresholds

### 💰 Energy Trading Optimization
- Market timing suggestions for energy selling
- Revenue opportunity identification
- Energy surplus/deficit analysis

### 🔐 Secure User Management
- Simple username/password authentication
- Personalized dashboards
- User profile management

### 💬 AI Chatbot Assistant
- Natural language queries about energy data
- Real-time insights and recommendations
- Support for complex energy-related questions

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Iam-Prakash-10/EcoShakti.git
   cd EcoShakti
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   # Create .env file
   echo "FLASK_SECRET_KEY=your_secret_key_here" > .env
   echo "DATABASE_URL=sqlite:///energy_monitor.db" >> .env
   echo "ML_MODEL_PATH=./ml_models" >> .env
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and go to: `http://localhost:5000`

## 🏗️ Architecture

### Technology Stack
- **Backend:** Flask 2.3.3, Flask-SocketIO, Python 3.8+
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Plotly.js
- **Machine Learning:** PyTorch, scikit-learn, pandas, NumPy
- **Database:** JSON files (users.json, alerts.json) + SQLite support
- **Real-time:** WebSocket communication via Flask-SocketIO

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App      │    │   Data Layer    │
│   (Dashboard)   │◄──►│   (API Routes)   │◄──►│   (JSON/SQLite) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼──────┐
                       │   ML Models   │
                       │  (PyTorch)    │
                       └───────────────┘
```

## 📁 Project Structure

```
EcoShakti/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
├── DEPLOYMENT.md        # Deployment guide
├── models/              # Data models
│   ├── user.py         # User management
│   └── ml_models.py    # Machine learning models
├── utils/              # Utility modules
│   ├── data_generator.py   # Simulated data generation
│   └── alert_system.py     # Alert management
├── templates/          # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
├── static/             # Static files (CSS, JS, images)
├── logs/              # Application logs
└── deployment/        # Deployment configurations
    ├── Dockerfile
    ├── docker-compose.yml
    ├── gunicorn.conf.py
    └── nginx.conf
```

## 🌐 Deployment

### Local Production
```bash
# Windows
.\deploy.bat

# Linux/macOS
chmod +x deploy.sh
./deploy.sh
```

### Cloud Platforms

#### Heroku
```bash
heroku create your-ecoshakti-app
git push heroku main
```

#### Docker
```bash
docker-compose up -d
```

### Detailed Deployment Guide
See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:
- Local production setup
- Cloud deployment (Heroku, Railway, Render)
- Docker containerization
- VPS/Server deployment with Nginx
- SSL certificate setup

## 📊 Dashboard Features

### Real-time Metrics
- ☀️ Solar power generation with efficiency tracking
- 💨 Wind power generation with speed monitoring
- 🏠 Energy consumption with load factor analysis
- 🔋 Battery storage status and capacity

### Interactive Charts
- Power overview with multiple time ranges
- Sun intensity correlation analysis
- Storage status trending
- Energy trading recommendations

### Smart Alerts
- System fault detection
- Performance optimization suggestions
- Maintenance reminders
- Energy trading opportunities

## 🤖 AI Chatbot Capabilities

Ask natural language questions like:
- "What's my current energy consumption?"
- "How much solar energy did I generate today?"
- "What's my battery status?"
- "Compare today's performance with yesterday"
- "Are there any system alerts?"

## 🔧 Configuration

### Environment Variables
```env
FLASK_SECRET_KEY=your_secure_secret_key
FLASK_ENV=production
DATABASE_URL=sqlite:///energy_monitor.db
ML_MODEL_PATH=./ml_models
PORT=5000
```

### Customization
- Modify `utils/data_generator.py` for real hardware integration
- Adjust ML models in `models/ml_models.py` for specific use cases
- Customize alert thresholds in `utils/alert_system.py`

## 🧪 Testing

```bash
# Run basic functionality tests
python -m pytest tests/

# Check application health
curl http://localhost:5000/api/health
```

## 📝 API Documentation

### Key Endpoints
- `/api/current-data` - Real-time energy data
- `/api/historical-data` - Historical energy metrics
- `/api/alerts` - System alerts and notifications
- `/api/chatbot/ask` - AI chatbot interactions
- `/api/health` - System health check

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo:** [Coming Soon]
- **Documentation:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues:** [GitHub Issues](https://github.com/Iam-Prakash-10/EcoShakti/issues)

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the deployment guide for common solutions
- Review the application logs for troubleshooting

## 🙏 Acknowledgments

- Built with Flask and modern web technologies
- Powered by PyTorch for machine learning capabilities
- Designed for renewable energy enthusiasts and professionals

---

**EcoShakti** - Empowering sustainable energy monitoring and optimization 🌱⚡