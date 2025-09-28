from datetime import datetime, timedelta
import json
import os
from enum import Enum
from typing import List, Dict, Any

class AlertType(Enum):
    FAULT_DETECTION = "fault_detection"
    LOW_EFFICIENCY = "low_efficiency"
    MAINTENANCE_REQUIRED = "maintenance_required"
    ENERGY_SURPLUS = "energy_surplus"
    ENERGY_DEFICIT = "energy_deficit"
    TRADING_OPPORTUNITY = "trading_opportunity"
    BATTERY_LOW = "battery_low"
    BATTERY_FULL = "battery_full"
    SYSTEM_OFFLINE = "system_offline"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert:
    def __init__(self, alert_type: AlertType, severity: AlertSeverity, title: str, 
                 message: str, data: Dict[str, Any] = None, user_id: str = None):
        self.id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(message) % 10000}"
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.message = message
        self.data = data or {}
        self.user_id = user_id
        self.timestamp = datetime.now().isoformat()
        self.is_read = False
        self.is_acknowledged = False
        self.acknowledged_by = None
        self.acknowledged_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'is_read': self.is_read,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at
        }
    
    @classmethod
    def from_dict(cls, data):
        alert = cls(
            AlertType(data['alert_type']),
            AlertSeverity(data['severity']),
            data['title'],
            data['message'],
            data.get('data', {}),
            data.get('user_id')
        )
        alert.id = data['id']
        alert.timestamp = data['timestamp']
        alert.is_read = data.get('is_read', False)
        alert.is_acknowledged = data.get('is_acknowledged', False)
        alert.acknowledged_by = data.get('acknowledged_by')
        alert.acknowledged_at = data.get('acknowledged_at')
        return alert
    
    def acknowledge(self, user_id: str):
        self.is_acknowledged = True
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.now().isoformat()
    
    def mark_as_read(self):
        self.is_read = True

class AlertManager:
    def __init__(self, alerts_file='alerts.json'):
        self.alerts_file = alerts_file
        self.alerts: List[Alert] = []
        self.load_alerts()
    
    def load_alerts(self):
        """Load alerts from JSON file"""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    alerts_data = json.load(f)
                    for alert_data in alerts_data:
                        alert = Alert.from_dict(alert_data)
                        self.alerts.append(alert)
            except (json.JSONDecodeError, KeyError, ValueError):
                self.alerts = []
    
    def save_alerts(self):
        """Save alerts to JSON file"""
        alerts_data = [alert.to_dict() for alert in self.alerts]
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def create_alert(self, alert_type: AlertType, severity: AlertSeverity, 
                    title: str, message: str, data: Dict[str, Any] = None, 
                    user_id: str = None):
        """Create a new alert"""
        alert = Alert(alert_type, severity, title, message, data, user_id)
        self.alerts.append(alert)
        self.save_alerts()
        return alert
    
    def get_alerts(self, user_id: str = None, unread_only: bool = False, 
                  unacknowledged_only: bool = False, limit: int = None):
        """Get alerts with filtering options"""
        filtered_alerts = self.alerts
        
        if user_id:
            filtered_alerts = [a for a in filtered_alerts if a.user_id == user_id or a.user_id is None]
        
        if unread_only:
            filtered_alerts = [a for a in filtered_alerts if not a.is_read]
        
        if unacknowledged_only:
            filtered_alerts = [a for a in filtered_alerts if not a.is_acknowledged]
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        if limit:
            filtered_alerts = filtered_alerts[:limit]
        
        return filtered_alerts
    
    def get_alert_by_id(self, alert_id: str):
        """Get a specific alert by ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def acknowledge_alert(self, alert_id: str, user_id: str):
        """Acknowledge an alert"""
        alert = self.get_alert_by_id(alert_id)
        if alert:
            alert.acknowledge(user_id)
            self.save_alerts()
            return True
        return False
    
    def mark_alert_as_read(self, alert_id: str):
        """Mark an alert as read"""
        alert = self.get_alert_by_id(alert_id)
        if alert:
            alert.mark_as_read()
            self.save_alerts()
            return True
        return False
    
    def cleanup_old_alerts(self, days_old: int = 30):
        """Remove alerts older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        initial_count = len(self.alerts)
        
        self.alerts = [
            alert for alert in self.alerts 
            if datetime.fromisoformat(alert.timestamp) > cutoff_date
        ]
        
        removed_count = initial_count - len(self.alerts)
        if removed_count > 0:
            self.save_alerts()
        
        return removed_count
    
    def get_alert_summary(self, user_id: str = None):
        """Get summary of alerts by type and severity"""
        alerts = self.get_alerts(user_id=user_id)
        
        summary = {
            'total': len(alerts),
            'unread': len([a for a in alerts if not a.is_read]),
            'unacknowledged': len([a for a in alerts if not a.is_acknowledged]),
            'by_severity': {
                'critical': len([a for a in alerts if a.severity == AlertSeverity.CRITICAL]),
                'high': len([a for a in alerts if a.severity == AlertSeverity.HIGH]),
                'medium': len([a for a in alerts if a.severity == AlertSeverity.MEDIUM]),
                'low': len([a for a in alerts if a.severity == AlertSeverity.LOW])
            },
            'by_type': {}
        }
        
        for alert_type in AlertType:
            summary['by_type'][alert_type.value] = len([
                a for a in alerts if a.alert_type == alert_type
            ])
        
        return summary

class EnergyAlertAnalyzer:
    """Analyze energy data and generate appropriate alerts"""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.thresholds = {
            'solar_efficiency_low': 0.6,      # 60% of expected
            'wind_efficiency_low': 0.5,       # 50% of expected
            'battery_low': 20,                # 20% charge
            'battery_full': 95,               # 95% charge
            'surplus_threshold': 3000,        # 3kW surplus
            'deficit_threshold': -2000,       # 2kW deficit
            'fault_probability': 0.7          # 70% fault probability
        }
    
    def analyze_and_create_alerts(self, current_data: Dict[str, Any], 
                                historical_data: List[Dict[str, Any]] = None,
                                user_id: str = None):
        """Analyze current data and create relevant alerts"""
        alerts_created = []
        
        # Solar panel efficiency check
        if current_data.get('sun_intensity', 0) > 70:
            expected_solar = (current_data['sun_intensity'] / 100) * 10000 * 0.75
            actual_solar = current_data.get('solar_power', 0)
            
            if actual_solar < expected_solar * self.thresholds['solar_efficiency_low']:
                efficiency_loss = ((expected_solar - actual_solar) / expected_solar) * 100
                alert = self.alert_manager.create_alert(
                    AlertType.LOW_EFFICIENCY,
                    AlertSeverity.HIGH if efficiency_loss > 50 else AlertSeverity.MEDIUM,
                    "Solar Panel Low Efficiency",
                    f"Solar panels operating at {efficiency_loss:.1f}% below expected efficiency. "
                    f"Expected: {expected_solar:.0f}W, Actual: {actual_solar:.0f}W. "
                    f"Sun intensity: {current_data['sun_intensity']:.1f}%",
                    {
                        'expected_power': expected_solar,
                        'actual_power': actual_solar,
                        'efficiency_loss': efficiency_loss,
                        'sun_intensity': current_data['sun_intensity']
                    },
                    user_id
                )
                alerts_created.append(alert)
        
        # Wind turbine efficiency check
        wind_speed = current_data.get('wind_speed', 0)
        if wind_speed > 8:  # Above cut-in speed
            if wind_speed > 14:
                expected_wind = 8000  # Rated power
            else:
                expected_wind = 8000 * ((wind_speed - 3) / 11) ** 3
            
            actual_wind = current_data.get('wind_power', 0)
            
            if actual_wind < expected_wind * self.thresholds['wind_efficiency_low']:
                efficiency_loss = ((expected_wind - actual_wind) / expected_wind) * 100
                alert = self.alert_manager.create_alert(
                    AlertType.LOW_EFFICIENCY,
                    AlertSeverity.HIGH if efficiency_loss > 60 else AlertSeverity.MEDIUM,
                    "Wind Turbine Low Efficiency",
                    f"Wind turbine operating at {efficiency_loss:.1f}% below expected efficiency. "
                    f"Expected: {expected_wind:.0f}W, Actual: {actual_wind:.0f}W. "
                    f"Wind speed: {wind_speed:.1f} m/s",
                    {
                        'expected_power': expected_wind,
                        'actual_power': actual_wind,
                        'efficiency_loss': efficiency_loss,
                        'wind_speed': wind_speed
                    },
                    user_id
                )
                alerts_created.append(alert)
        
        # Battery status alerts
        storage_percentage = current_data.get('storage_percentage', 50)
        
        if storage_percentage <= self.thresholds['battery_low']:
            alert = self.alert_manager.create_alert(
                AlertType.BATTERY_LOW,
                AlertSeverity.HIGH if storage_percentage < 10 else AlertSeverity.MEDIUM,
                "Battery Level Low",
                f"Battery charge is at {storage_percentage:.1f}%. Consider reducing consumption "
                f"or increasing generation.",
                {'storage_percentage': storage_percentage},
                user_id
            )
            alerts_created.append(alert)
        
        if storage_percentage >= self.thresholds['battery_full']:
            alert = self.alert_manager.create_alert(
                AlertType.BATTERY_FULL,
                AlertSeverity.LOW,
                "Battery Nearly Full",
                f"Battery is at {storage_percentage:.1f}% capacity. Excess energy "
                f"may be exported to grid.",
                {'storage_percentage': storage_percentage},
                user_id
            )
            alerts_created.append(alert)
        
        # Energy surplus/deficit alerts
        net_power = current_data.get('net_power', 0)
        
        if net_power >= self.thresholds['surplus_threshold']:
            revenue_estimate = net_power * 0.15 / 1000  # $0.15 per kWh
            alert = self.alert_manager.create_alert(
                AlertType.ENERGY_SURPLUS,
                AlertSeverity.LOW,
                "Energy Surplus Available",
                f"Generating {net_power:.0f}W surplus energy. Consider selling to grid. "
                f"Estimated revenue: ${revenue_estimate:.2f}/hour",
                {
                    'surplus_power': net_power,
                    'estimated_revenue': revenue_estimate,
                    'storage_percentage': storage_percentage
                },
                user_id
            )
            alerts_created.append(alert)
        
        if net_power <= self.thresholds['deficit_threshold']:
            cost_estimate = abs(net_power) * 0.12 / 1000  # $0.12 per kWh
            alert = self.alert_manager.create_alert(
                AlertType.ENERGY_DEFICIT,
                AlertSeverity.MEDIUM if abs(net_power) > 4000 else AlertSeverity.LOW,
                "Energy Deficit",
                f"Energy deficit of {abs(net_power):.0f}W. Drawing from battery/grid. "
                f"Estimated cost: ${cost_estimate:.2f}/hour",
                {
                    'deficit_power': abs(net_power),
                    'estimated_cost': cost_estimate,
                    'storage_percentage': storage_percentage
                },
                user_id
            )
            alerts_created.append(alert)
        
        # Trading opportunity alerts
        if (net_power > 2000 and storage_percentage > 80):
            sell_amount = net_power * 0.8
            revenue = sell_amount * 0.15 / 1000
            alert = self.alert_manager.create_alert(
                AlertType.TRADING_OPPORTUNITY,
                AlertSeverity.LOW,
                "Optimal Selling Opportunity",
                f"Ideal conditions for selling energy: {sell_amount:.0f}W available. "
                f"Battery at {storage_percentage:.1f}%. Potential revenue: ${revenue:.2f}/hour",
                {
                    'action': 'sell',
                    'power_amount': sell_amount,
                    'estimated_revenue': revenue,
                    'storage_percentage': storage_percentage
                },
                user_id
            )
            alerts_created.append(alert)
        
        elif (net_power < -1000 and storage_percentage < 30):
            buy_amount = abs(net_power) * 0.5
            cost = buy_amount * 0.12 / 1000
            alert = self.alert_manager.create_alert(
                AlertType.TRADING_OPPORTUNITY,
                AlertSeverity.LOW,
                "Energy Purchase Opportunity",
                f"Consider purchasing {buy_amount:.0f}W from grid. "
                f"Battery low at {storage_percentage:.1f}%. Estimated cost: ${cost:.2f}/hour",
                {
                    'action': 'buy',
                    'power_amount': buy_amount,
                    'estimated_cost': cost,
                    'storage_percentage': storage_percentage
                },
                user_id
            )
            alerts_created.append(alert)
        
        return alerts_created
    
    def analyze_historical_trends(self, historical_data: List[Dict[str, Any]], 
                                 user_id: str = None):
        """Analyze historical data for maintenance and efficiency trends"""
        if len(historical_data) < 100:  # Need sufficient data
            return []
        
        alerts_created = []
        
        # Convert to DataFrame for analysis
        import pandas as pd
        df = pd.DataFrame(historical_data)
        
        # Check for declining efficiency trends
        df['solar_efficiency'] = df['solar_power'] / (df['sun_intensity'] + 1e-8)
        df['wind_efficiency'] = df['wind_power'] / (df['wind_speed'] + 1e-8)
        
        # Calculate rolling averages for trend analysis
        df['solar_eff_trend'] = df['solar_efficiency'].rolling(window=50).mean().diff()
        df['wind_eff_trend'] = df['wind_efficiency'].rolling(window=50).mean().diff()
        
        # Check for consistent decline
        recent_solar_trend = df['solar_eff_trend'].tail(20).mean()
        recent_wind_trend = df['wind_eff_trend'].tail(20).mean()
        
        if recent_solar_trend < -0.001:  # Declining trend
            alert = self.alert_manager.create_alert(
                AlertType.MAINTENANCE_REQUIRED,
                AlertSeverity.MEDIUM,
                "Solar Panel Maintenance Recommended",
                f"Solar panel efficiency has been declining over time. "
                f"Trend: {recent_solar_trend:.4f} efficiency loss per measurement. "
                f"Consider cleaning panels or professional inspection.",
                {'efficiency_trend': recent_solar_trend},
                user_id
            )
            alerts_created.append(alert)
        
        if recent_wind_trend < -0.002:  # Declining trend
            alert = self.alert_manager.create_alert(
                AlertType.MAINTENANCE_REQUIRED,
                AlertSeverity.MEDIUM,
                "Wind Turbine Maintenance Recommended",
                f"Wind turbine efficiency has been declining over time. "
                f"Trend: {recent_wind_trend:.4f} efficiency loss per measurement. "
                f"Consider professional inspection and maintenance.",
                {'efficiency_trend': recent_wind_trend},
                user_id
            )
            alerts_created.append(alert)
        
        return alerts_created

# Global alert manager instance
alert_manager = AlertManager()
alert_analyzer = EnergyAlertAnalyzer(alert_manager)
