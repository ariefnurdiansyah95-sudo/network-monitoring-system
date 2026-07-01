# Network Monitoring System 🌐

A comprehensive Python-based network monitoring system with real-time Telegram notifications, a responsive web dashboard, device status monitoring, and network performance visualization.

## ✨ Features

- **Real-time Monitoring**: Continuously monitor network devices and services
- **Telegram Notifications**: Instant alerts via Telegram for critical events
- **Web Dashboard**: Responsive and interactive web interface for visualization
- **Device Status Tracking**: Real-time status of network devices
- **Performance Metrics**: Detailed network performance analytics and visualization
- **Multi-Device Support**: Monitor multiple devices across your network
- **Historical Data**: Track network metrics over time
- **Customizable Alerts**: Configure alert thresholds and notification rules

## 🎯 Use Cases

- Network infrastructure monitoring
- Server health tracking
- Performance analysis and optimization
- Proactive issue detection and alerts
- Network administration and management

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip (Python package manager)
- Telegram Bot Token
- Basic networking knowledge

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ariefnurdiansyah95-sudo/network-monitoring-system.git
cd network-monitoring-system
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Update `.env` with your settings:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
# Add other configuration as needed
```

5. Run the application:
```bash
python main.py
```

6. Access the web dashboard:
```
http://localhost:5000
```

## 📁 Project Structure

```
network-monitoring-system/
├── src/
│   ├── monitoring/          # Core monitoring logic
│   ├── notifications/       # Telegram notification handler
│   ├── dashboard/           # Web dashboard
│   └── utils/               # Utility functions
├── static/                  # Frontend assets (CSS, JS)
├── templates/               # HTML templates
├── config/                  # Configuration files
├── requirements.txt         # Python dependencies
├── main.py                  # Application entry point
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
FLASK_ENV=production
DEBUG=False
MONITOR_INTERVAL=60
ALERT_THRESHOLD=80
```

### Device Configuration

Add your devices to monitor in `config/devices.json`:

```json
{
  "devices": [
    {
      "name": "Router",
      "ip": "192.168.1.1",
      "type": "router",
      "alert_enabled": true
    },
    {
      "name": "Server",
      "ip": "192.168.1.10",
      "type": "server",
      "alert_enabled": true
    }
  ]
}
```

## 🌐 Web Dashboard

The dashboard provides:

- **Live Status**: Real-time device status indicators
- **Performance Charts**: Network metrics visualization
- **Alert Logs**: Historical alert records
- **Device Details**: Detailed information about monitored devices
- **Configuration Panel**: Manage monitoring settings

Access at: `http://localhost:5000`

## 🔔 Telegram Notifications

Receive instant notifications for:

- Device connectivity status changes
- Performance threshold breaches
- Network anomalies
- System errors and warnings

Setup Telegram bot: [BotFather Guide](https://core.telegram.org/bots#3-how-do-i-create-a-bot)

## 📊 Monitoring Metrics

The system tracks:

- **Latency**: Response time to devices (in ms)
- **Packet Loss**: Percentage of lost packets
- **Bandwidth**: Current network bandwidth usage
- **CPU Usage**: CPU utilization on monitored devices
- **Memory Usage**: RAM utilization metrics
- **Uptime**: Device availability percentage

## 🛠️ API Endpoints

### Get Device Status
```
GET /api/devices
```

### Get Performance Metrics
```
GET /api/metrics?device_id=<id>&period=24h
```

### Get Alert History
```
GET /api/alerts?limit=50
```

### Trigger Manual Check
```
POST /api/check/<device_id>
```

## 🐛 Troubleshooting

### No Telegram notifications
- Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
- Check internet connectivity
- Ensure Telegram bot is active

### Dashboard not loading
- Check if Flask server is running
- Verify port 5000 is not in use
- Check browser console for errors

### Devices not being monitored
- Verify device IPs are correct
- Check network connectivity to devices
- Ensure firewall allows ICMP packets

## 📝 Logs

View application logs:
```bash
tail -f logs/app.log
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For issues, questions, or suggestions:

1. Check existing [Issues](https://github.com/ariefnurdiansyah95-sudo/network-monitoring-system/issues)
2. Create a new issue with detailed information
3. Include error messages and system configuration details

## 🙏 Acknowledgments

- Built with Python and Flask
- Telegram Bot API for notifications
- Chart.js for data visualization
- Bootstrap for responsive design

## 📚 Additional Resources

- [Python Documentation](https://docs.python.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Network Monitoring Best Practices](https://en.wikipedia.org/wiki/Network_monitoring)

---

**Last Updated**: July 2026

**Repository**: [network-monitoring-system](https://github.com/ariefnurdiansyah95-sudo/network-monitoring-system)

**Author**: [ariefnurdiansyah95-sudo](https://github.com/ariefnurdiansyah95-sudo)