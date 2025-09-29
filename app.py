from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
import json
import os
import random
from json import JSONEncoder
from datetime import datetime
import sys

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)

from datetime import datetime, timedelta
import re
import json as json_lib

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import user_manager, User
from models.ml_models import ml_manager
from utils.data_generator import RenewableEnergyDataGenerator, get_current_data, get_historical_data
from utils.alert_system import alert_manager, alert_analyzer, AlertSeverity
import plotly.graph_objs as go
import plotly.utils
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ecoshakti_monitoring_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.json_encoder = CustomJSONEncoder

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the energy monitoring dashboard.'

socketio = SocketIO(app, cors_allowed_origins="*", json=json)

# Initialize data generator
data_generator = RenewableEnergyDataGenerator()

# Grid connection status
grid_connected = True
current_data_cache = {}

@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user(user_id)

# Routes for authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        try:
            user = user_manager.create_user(username, email, password)
            # Auto-verify user since we removed email verification
            user.is_email_verified = True
            user_manager.save_users()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        
        user = user_manager.authenticate_user(username_or_email, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))



# Main dashboard route
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Get current data for dashboard
    current_data = get_current_data()
    
    # Get recent alerts
    recent_alerts = alert_manager.get_alerts(user_id=current_user.id, limit=5)
    alert_summary = alert_manager.get_alert_summary(user_id=current_user.id)
    
    # Get historical data for analysis
    historical_data = get_historical_data(hours=24)
    daily_averages = data_generator.get_daily_averages(historical_data)
    
    # Analyze current data for alerts
    alert_analyzer.analyze_and_create_alerts(current_data, user_id=current_user.id)
    
    return render_template('dashboard.html', 
                         current_data=current_data,
                         recent_alerts=recent_alerts,
                         alert_summary=alert_summary,
                         daily_averages=daily_averages)

# API routes for real-time data
@app.route('/api/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Check if essential services are working
        current_data = get_current_data()  # Test data generation
        user_count = len(user_manager.get_all_users())  # Test user system
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'data_generator': 'ok',
                'user_manager': 'ok',
                'ml_models': 'ok' if ml_manager else 'not_initialized'
            },
            'stats': {
                'users': user_count,
                'grid_connected': grid_connected
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/current-data')
@login_required
def api_current_data():
    global grid_connected, current_data_cache
    
    if grid_connected:
        current_data = get_current_data()
        
        # Cache the current data
        current_data_cache = current_data.copy()
        
        # Analyze for alerts
        alerts_created = alert_analyzer.analyze_and_create_alerts(current_data, user_id=current_user.id)
        
        return jsonify({
            'data': current_data,
            'timestamp': datetime.now().isoformat(),
            'new_alerts': len(alerts_created),
            'grid_connected': grid_connected
        })
    else:
        # Return last known data when disconnected
        return jsonify({
            'data': current_data_cache if current_data_cache else {},
            'timestamp': datetime.now().isoformat(),
            'new_alerts': 0,
            'grid_connected': grid_connected,
            'message': 'Grid disconnected - showing last known data'
        })

@app.route('/api/historical-data')
@login_required
def api_historical_data():
    hours = request.args.get('hours', 24, type=int)
    data = get_historical_data(hours=hours)
    return jsonify(data)

@app.route('/api/solar-analysis')
@login_required
def api_solar_analysis():
    hours = request.args.get('hours', 24, type=int)
    historical_data = get_historical_data(hours=hours)
    
    # Prepare data for sun intensity vs power generation analysis
    analysis_data = []
    faults = data_generator.detect_solar_faults(historical_data)
    
    for record in historical_data[-100:]:  # Last 100 records
        analysis_data.append({
            'timestamp': record['timestamp'].isoformat() if hasattr(record['timestamp'], 'isoformat') else str(record['timestamp']),
            'sun_intensity': record['sun_intensity'],
            'solar_power': record['solar_power'],
            'expected_power': (record['sun_intensity'] / 100) * 10000 * 0.75,
            'efficiency': (record['solar_power'] / ((record['sun_intensity'] / 100) * 10000 * 0.75)) * 100 if record['sun_intensity'] > 0 else 0
        })
    
    return jsonify({
        'analysis_data': analysis_data,
        'faults_detected': len(faults),
        'fault_details': [{
            'timestamp': f['timestamp'].isoformat() if hasattr(f['timestamp'], 'isoformat') else str(f['timestamp']),
            'fault_type': f['fault_type'],
            'efficiency_loss': f['efficiency_loss'],
            'sun_intensity': f['sun_intensity'],
            'actual_power': f['actual_power'],
            'expected_power': f['expected_power']
        } for f in faults]
    })

@app.route('/api/energy-trading')
@login_required
def api_energy_trading():
    hours = request.args.get('hours', 24, type=int)
    historical_data = get_historical_data(hours=hours)
    
    trading_analysis = data_generator.analyze_energy_trading(historical_data)
    optimal_times = ml_manager.predict_optimal_trading_times(historical_data)
    
    return jsonify({
        'trading_opportunities': [{
            'timestamp': t['timestamp'].isoformat() if hasattr(t['timestamp'], 'isoformat') else str(t['timestamp']),
            'opportunity_type': t['opportunity_type'],
            'power_amount': t.get('surplus_power', t.get('deficit_power', 0)),
            'estimated_value': t.get('estimated_revenue', t.get('estimated_cost', 0)),
            'recommended_action': t.get('recommended_sell', t.get('recommended_buy', 0))
        } for t in trading_analysis],
        'optimal_times': optimal_times
    })

@app.route('/api/ml-predictions')
@login_required
def api_ml_predictions():
    current_data = get_current_data()
    historical_data = get_historical_data(hours=24)
    
    try:
        # Get ML predictions
        fault_probability = ml_manager.predict_fault_probability(current_data)
        performance_analysis = ml_manager.analyze_performance_efficiency(historical_data)
        
        return jsonify({
            'fault_probability': fault_probability,
            'performance_analysis': performance_analysis,
            'recommendations': generate_recommendations(current_data, performance_analysis)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'fault_probability': 0.0,
            'performance_analysis': {},
            'recommendations': []
        })

@app.route('/api/alerts')
@login_required
def api_alerts():
    limit = request.args.get('limit', 10, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    
    alerts = alert_manager.get_alerts(
        user_id=current_user.id, 
        unread_only=unread_only, 
        limit=limit
    )
    
    return jsonify({
        'alerts': [{
            'id': alert.id,
            'alert_type': alert.alert_type.value,
            'severity': alert.severity.value,
            'title': alert.title,
            'message': alert.message,
            'timestamp': alert.timestamp,
            'is_read': alert.is_read,
            'is_acknowledged': alert.is_acknowledged
        } for alert in alerts],
        'summary': alert_manager.get_alert_summary(user_id=current_user.id)
    })

@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
@login_required
def api_acknowledge_alert(alert_id):
    success = alert_manager.acknowledge_alert(alert_id, current_user.id)
    return jsonify({'success': success})

@app.route('/api/alerts/<alert_id>/read', methods=['POST'])
@login_required
def api_mark_alert_read(alert_id):
    success = alert_manager.mark_alert_as_read(alert_id)
    return jsonify({'success': success})

# Chart generation routes
@app.route('/api/charts/power-overview')
@login_required
def api_chart_power_overview():
    hours = request.args.get('hours', 24, type=int)
    historical_data = get_historical_data(hours=hours)
    
    # Prepare data for chart
    df = pd.DataFrame(historical_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Smart sampling based on time range
    if hours <= 6:
        df_sampled = df.iloc[::5]  # Every 5 minutes for detailed view
    elif hours <= 24:
        df_sampled = df.iloc[::10]  # Every 10 minutes
    else:
        df_sampled = df.iloc[::30]  # Every 30 minutes for longer periods
    
    fig = go.Figure()
    
    # Enhanced color scheme with better contrast
    colors = {
        'solar': '#FFB800',      # Bright Orange/Gold
        'wind': '#00B4D8',       # Bright Blue
        'consumption': '#E63946',  # Red
        'total': '#06D6A0',      # Green
        'surplus': '#06D6A0',    # Green for surplus
        'deficit': '#E63946'     # Red for deficit
    }
    
    # Add solar power with area fill
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['solar_power'],
        mode='lines',
        name='☀️ Solar Generation',
        line=dict(color=colors['solar'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba(255, 184, 0, 0.2)",
        hovertemplate='<b>Solar Power</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>Clean renewable energy</i><extra></extra>'
    ))
    
    # Add dedicated wind power line (blue)
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['wind_power'],
        mode='lines+markers',
        name='💨 Wind Generation',
        line=dict(color=colors['wind'], width=3),
        marker=dict(size=4, color=colors['wind']),
        hovertemplate='<b>Wind Power</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>Wind energy generation</i><extra></extra>'
    ))
    
    # Add wind power stacked area (for visual comparison)
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['solar_power'] + df_sampled['wind_power'],
        mode='lines',
        name='Combined Renewables',
        line=dict(color='rgba(108, 117, 125, 0.3)', width=1, dash='dot'),
        fill='tonexty',
        fillcolor=f"rgba(0, 180, 216, 0.1)",
        showlegend=False,
        hovertemplate='<b>Combined Solar + Wind</b><br>%{y:,.0f} W<br>%{x|%H:%M}<extra></extra>'
    ))
    
    # Add total generation line (bold)
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['total_generation'],
        mode='lines+markers',
        name='⚡ Total Generation',
        line=dict(color=colors['total'], width=4, dash='solid'),
        marker=dict(size=4, color=colors['total']),
        hovertemplate='<b>Total Generation</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>Combined renewable power</i><extra></extra>'
    ))
    
    # Add consumption line with distinct style
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['consumption'],
        mode='lines+markers',
        name='🏠 Energy Consumption',
        line=dict(color=colors['consumption'], width=4, dash='dash'),
        marker=dict(size=5, symbol='square', color=colors['consumption']),
        hovertemplate='<b>Energy Consumption</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>Total power usage</i><extra></extra>'
    ))
    
    # Add energy balance indicator (surplus/deficit)
    df_sampled = df_sampled.copy()
    df_sampled['energy_balance'] = df_sampled['total_generation'] - df_sampled['consumption']
    
    # Separate surplus and deficit for different colors
    surplus_mask = df_sampled['energy_balance'] >= 0
    deficit_mask = df_sampled['energy_balance'] < 0
    
    if surplus_mask.any():
        fig.add_trace(go.Scatter(
            x=df_sampled[surplus_mask]['timestamp'],
            y=df_sampled[surplus_mask]['energy_balance'],
            mode='lines+markers',
            name='📈 Energy Surplus',
            line=dict(color=colors['surplus'], width=2),
            marker=dict(size=4, color=colors['surplus']),
            yaxis='y2',
            hovertemplate='<b>Energy Surplus</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>Excess power available</i><extra></extra>'
        ))
    
    if deficit_mask.any():
        fig.add_trace(go.Scatter(
            x=df_sampled[deficit_mask]['timestamp'],
            y=df_sampled[deficit_mask]['energy_balance'],
            mode='lines+markers',
            name='📉 Energy Deficit',
            line=dict(color=colors['deficit'], width=2),
            marker=dict(size=4, color=colors['deficit']),
            yaxis='y2',
            hovertemplate='<b>Energy Deficit</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>Additional power needed</i><extra></extra>'
        ))
    
    # Enhanced layout with dual y-axes and better styling
    fig.update_layout(
        title=dict(
            text=f'⚡ Power Analysis ({hours}h)',
            font=dict(size=16, color='#2C3E50'),
            x=0.5,
            y=0.98
        ),
        xaxis=dict(
            title='Time',
            title_font=dict(size=14, color='#34495E'),
            tickfont=dict(size=12),
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7'
        ),
        yaxis=dict(
            title='Power (Watts)',
            title_font=dict(size=14, color='#34495E'),
            tickfont=dict(size=12),
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickformat=',.0f',
            side='left'
        ),
        yaxis2=dict(
            title='Energy Balance (W)',
            title_font=dict(size=12, color='#7F8C8D'),
            tickfont=dict(size=10, color='#7F8C8D'),
            side='right',
            overlaying='y',
            zeroline=True,
            zerolinecolor='#95A5A6',
            zerolinewidth=2
        ),
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#BDC3C7',
            borderwidth=1
        ),
        margin=dict(l=50, r=60, t=50, b=40),
        height=320,
        showlegend=True
    )
    
    # Add annotations for key insights
    max_generation = df_sampled['total_generation'].max()
    max_generation_time = df_sampled.loc[df_sampled['total_generation'].idxmax(), 'timestamp']
    
    fig.add_annotation(
        x=max_generation_time,
        y=max_generation,
        text=f"Peak: {max_generation:,.0f}W",
        arrowhead=2,
        arrowsize=1,
        arrowcolor=colors['total'],
        bgcolor='rgba(6, 214, 160, 0.8)',
        bordercolor=colors['total'],
        font=dict(size=10, color='white')
    )
    
    # Add summary text box
    avg_generation = df_sampled['total_generation'].mean()
    avg_consumption = df_sampled['consumption'].mean()
    avg_solar = df_sampled['solar_power'].mean()
    avg_wind = df_sampled['wind_power'].mean()
    energy_independence = (avg_generation / avg_consumption) * 100 if avg_consumption > 0 else 0
    
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        text=f"📊 Summary<br>" +
             f"Avg Solar: {avg_solar:,.0f}W<br>" +
             f"Avg Wind: {avg_wind:,.0f}W<br>" +
             f"Avg Total: {avg_generation:,.0f}W<br>" +
             f"Avg Consumption: {avg_consumption:,.0f}W<br>" +
             f"Energy Independence: {energy_independence:.1f}%",
        showarrow=False,
        font=dict(size=10),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#BDC3C7",
        borderwidth=1
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/charts/sun-intensity-correlation')
@login_required
def api_chart_sun_intensity():
    hours = request.args.get('hours', 24, type=int)
    historical_data = get_historical_data(hours=hours)
    
    # Filter for meaningful daylight data
    daylight_data = [d for d in historical_data if d['sun_intensity'] > 5]
    
    if not daylight_data:
        return jsonify({'error': 'No sufficient daylight data available for analysis'})
    
    df = pd.DataFrame(daylight_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Smart sampling based on time range
    if hours <= 6:
        df_sampled = df.iloc[::5]  # Every 5 minutes for detailed view
    elif hours <= 24:
        df_sampled = df.iloc[::10]  # Every 10 minutes
    else:
        df_sampled = df.iloc[::30]  # Every 30 minutes for longer periods
    
    # Calculate efficiency and machine health indicators
    df_sampled = df_sampled.copy()
    df_sampled['expected_power'] = df_sampled['sun_intensity'] * 75  # Expected power based on intensity
    df_sampled['efficiency'] = ((df_sampled['solar_power'] / df_sampled['expected_power']) * 100).fillna(0)
    df_sampled['efficiency'] = df_sampled['efficiency'].clip(0, 100)
    
    # Machine health analysis
    df_sampled['health_status'] = df_sampled.apply(lambda row: 
        'Excellent' if row['efficiency'] >= 85 else
        'Good' if row['efficiency'] >= 70 else
        'Fair' if row['efficiency'] >= 50 else
        'Poor' if row['efficiency'] >= 30 else
        'Critical', axis=1)
    
    # Color coding based on health status
    df_sampled['health_color'] = df_sampled['health_status'].map({
        'Excellent': '#00C851',    # Green
        'Good': '#39C0ED',         # Blue
        'Fair': '#FFD700',         # Yellow
        'Poor': '#FF8800',         # Orange
        'Critical': '#FF4444'      # Red
    })
    
    # Create dual-axis chart
    fig = go.Figure()
    
    # Enhanced color scheme
    colors = {
        'sun_intensity': '#FF8C00',    # Orange for sun
        'solar_power': '#06D6A0',      # Green for power
        'expected_power': '#9370DB'    # Purple for expected
    }
    
    # Add sun intensity line with area fill
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['sun_intensity'],
        mode='lines+markers',
        name='☀️ Sun Intensity',
        line=dict(color=colors['sun_intensity'], width=4),
        marker=dict(size=6, color=colors['sun_intensity']),
        fill='tozeroy',
        fillcolor=f"rgba(255, 140, 0, 0.2)",
        yaxis='y',
        hovertemplate='<b>Sun Intensity</b><br>%{y:.1f}%<br>%{x|%H:%M}<br><i>Solar irradiance level</i><extra></extra>'
    ))
    
    # Add expected power line (reference)
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['expected_power'],
        mode='lines',
        name='📈 Expected Power',
        line=dict(color=colors['expected_power'], width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Expected Power</b><br>%{y:,.0f}W<br>%{x|%H:%M}<br><i>Theoretical output</i><extra></extra>'
    ))
    
    # Add actual solar power with health-based color coding
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['solar_power'],
        mode='lines+markers',
        name='⚡ Actual Solar Power',
        line=dict(color=colors['solar_power'], width=4),
        marker=dict(
            size=8,
            color=df_sampled['health_color'],
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        fill='tozeroy',
        fillcolor=f"rgba(6, 214, 160, 0.2)",
        yaxis='y2',
        customdata=list(zip(df_sampled['efficiency'], df_sampled['health_status'])),
        hovertemplate='<b>Solar Power</b><br>%{y:,.0f}W<br>%{x|%H:%M}<br>' +
                     '<b>Efficiency:</b> %{customdata[0]:.1f}%<br>' +
                     '<b>Health:</b> %{customdata[1]}<extra></extra>'
    ))
    
    # Enhanced layout with dual y-axes and health indicators
    fig.update_layout(
        title=dict(
            text=f'☀️ Solar Health Analysis ({hours}h)',
            font=dict(size=16, color='#2C3E50'),
            x=0.5,
            y=0.98
        ),
        xaxis=dict(
            title='Time',
            title_font=dict(size=12, color='#34495E'),
            tickfont=dict(size=10),
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7'
        ),
        yaxis=dict(
            title='Sun Intensity (%)',
            title_font=dict(size=12, color='#FF8C00'),
            tickfont=dict(size=10, color='#FF8C00'),
            gridcolor='#ECF0F1',
            linecolor='#FF8C00',
            range=[0, 105]
        ),
        yaxis2=dict(
            title='Solar Power (W)',
            title_font=dict(size=12, color='#06D6A0'),
            tickfont=dict(size=10, color='#06D6A0'),
            overlaying='y',
            side='right',
            tickformat=',.0f',
            linecolor='#06D6A0'
        ),
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#BDC3C7',
            borderwidth=1
        ),
        margin=dict(l=50, r=60, t=50, b=40),
        height=380,
        showlegend=True
    )
    
    # Calculate health metrics
    avg_efficiency = df_sampled['efficiency'].mean()
    current_efficiency = df_sampled['efficiency'].iloc[-1] if not df_sampled.empty else 0
    health_issues = len(df_sampled[df_sampled['efficiency'] < 50])
    total_points = len(df_sampled)
    health_percentage = ((total_points - health_issues) / total_points * 100) if total_points > 0 else 100
    
    # Determine overall system health
    if avg_efficiency >= 85:
        system_health = 'Excellent'
        health_color = '#00C851'
        health_icon = '🟢'
    elif avg_efficiency >= 70:
        system_health = 'Good'
        health_color = '#39C0ED'
        health_icon = '🔵'
    elif avg_efficiency >= 50:
        system_health = 'Fair'
        health_color = '#FFD700'
        health_icon = '🟡'
    elif avg_efficiency >= 30:
        system_health = 'Poor'
        health_color = '#FF8800'
        health_icon = '🟠'
    else:
        system_health = 'Critical'
        health_color = '#FF4444'
        health_icon = '🔴'
    
    # Add health status annotation
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        text=f"🏥 <b>Machine Health</b><br>" +
             f"{health_icon} Status: <span style='color:{health_color}'><b>{system_health}</b></span><br>" +
             f"📊 Avg Efficiency: {avg_efficiency:.1f}%<br>" +
             f"⚡ Current: {current_efficiency:.1f}%<br>" +
             f"🎯 Health Score: {health_percentage:.0f}%",
        showarrow=False,
        font=dict(size=10),
        bgcolor="rgba(255, 255, 255, 0.95)",
        bordercolor=health_color,
        borderwidth=2,
        align="left"
    )
    
    # Add health legend
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=0.98,
        text=f"🔍 <b>Health Indicators</b><br>" +
             f"🟢 Excellent (85%+)<br>" +
             f"🔵 Good (70-85%)<br>" +
             f"🟡 Fair (50-70%)<br>" +
             f"🟠 Poor (30-50%)<br>" +
             f"🔴 Critical (<30%)",
        showarrow=False,
        font=dict(size=9),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#BDC3C7",
        borderwidth=1,
        align="left",
        xanchor="right"
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/charts/storage-status')
@login_required
def api_chart_storage():
    hours = request.args.get('hours', 24, type=int)
    historical_data = get_historical_data(hours=hours)
    
    df = pd.DataFrame(historical_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Smart sampling based on time range
    if hours <= 6:
        df_sampled = df.iloc[::8]   # Every 8 minutes for detailed view
    elif hours <= 24:
        df_sampled = df.iloc[::15]  # Every 15 minutes
    else:
        df_sampled = df.iloc[::30]  # Every 30 minutes for longer periods
    
    fig = go.Figure()
    
    # Enhanced battery level visualization with color zones
    battery_colors = []
    for level in df_sampled['storage_percentage']:
        if level < 20:
            battery_colors.append('#E74C3C')    # Critical - Red
        elif level < 40:
            battery_colors.append('#F39C12')    # Low - Orange
        elif level < 70:
            battery_colors.append('#F1C40F')    # Medium - Yellow
        else:
            battery_colors.append('#27AE60')    # High - Green
    
    # Add battery level with gradient fill
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['storage_percentage'],
        mode='lines+markers',
        name='🔋 Battery Level',
        line=dict(color='#2E8B57', width=4, shape='spline'),
        marker=dict(
            size=8,
            color=battery_colors,
            symbol='circle',
            line=dict(width=2, color='white')
        ),
        fill='tozeroy',
        fillcolor='rgba(46, 139, 87, 0.2)',
        yaxis='y',
        hovertemplate='<b>Battery</b><br>%{y:.1f}%<br>%{x|%H:%M}<extra></extra>'
    ))
    
    # Add battery capacity reference lines
    fig.add_hline(y=20, line_dash="dot", line_color="#E74C3C", 
                  annotation_text="Critical (20%)", annotation_position="right")
    fig.add_hline(y=80, line_dash="dot", line_color="#27AE60", 
                  annotation_text="Optimal (80%)", annotation_position="right")
    
    # Add net power with enhanced styling
    net_power_colors = ['#E74C3C' if x < 0 else '#2ECC71' for x in df_sampled['net_power']]
    
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['net_power'],
        mode='lines+markers',
        name='⚡ Net Power Flow',
        line=dict(color='#3498DB', width=3),
        marker=dict(
            size=6,
            color=net_power_colors,
            symbol='diamond',
            line=dict(width=1, color='white')
        ),
        yaxis='y2',
        hovertemplate='<b>Net Power</b><br>%{y:,.0f} W<br>%{x|%H:%M}<br><i>%{customdata}</i><extra></extra>',
        customdata=['Surplus' if x >= 0 else 'Deficit' for x in df_sampled['net_power']]
    ))
    
    # Add grid import/export visualization
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=df_sampled['grid_export'],
        mode='lines',
        name='🏠→🌐 Grid Export',
        line=dict(color='#2ECC71', width=2, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(46, 204, 113, 0.1)',
        yaxis='y2',
        hovertemplate='<b>Grid Export</b><br>%{y:,.0f} W<br>%{x|%H:%M}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_sampled['timestamp'],
        y=[-x for x in df_sampled['grid_import']],  # Negative for visual distinction
        mode='lines',
        name='🌐→🏠 Grid Import',
        line=dict(color='#E74C3C', width=2, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(231, 76, 60, 0.1)',
        yaxis='y2',
        hovertemplate='<b>Grid Import</b><br>%{y:,.0f} W<br>%{x|%H:%M}<extra></extra>'
    ))
    
    # Enhanced layout with dual y-axes
    fig.update_layout(
        title=dict(
            text=f'🔋 Storage & Grid ({hours}h)',
            font=dict(size=16, color='#2C3E50'),
            x=0.5,
            y=0.98
        ),
        xaxis=dict(
            title='Time',
            title_font=dict(size=14, color='#34495E'),
            tickfont=dict(size=12),
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7'
        ),
        yaxis=dict(
            title='Battery Level (%)',
            title_font=dict(size=14, color='#2E8B57'),
            tickfont=dict(size=12, color='#2E8B57'),
            side='left',
            range=[0, 105],
            gridcolor='#ECF0F1',
            linecolor='#2E8B57',
            ticksuffix='%'
        ),
        yaxis2=dict(
            title='Power Flow (Watts)',
            title_font=dict(size=14, color='#3498DB'),
            tickfont=dict(size=12, color='#3498DB'),
            side='right',
            overlaying='y',
            gridcolor='rgba(52, 152, 219, 0.1)',
            linecolor='#3498DB',
            tickformat=',.0f',
            zeroline=True,
            zerolinecolor='#95A5A6',
            zerolinewidth=2
        ),
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#BDC3C7',
            borderwidth=1
        ),
        margin=dict(l=50, r=60, t=50, b=40),
        height=380,
        showlegend=True
    )
    
    # Add annotations for critical battery levels
    critical_points = df_sampled[df_sampled['storage_percentage'] < 25]
    if not critical_points.empty:
        lowest_point = critical_points.loc[critical_points['storage_percentage'].idxmin()]
        fig.add_annotation(
            x=lowest_point['timestamp'],
            y=lowest_point['storage_percentage'],
            text=f"Low: {lowest_point['storage_percentage']:.1f}%",
            arrowhead=2,
            arrowsize=1,
            arrowcolor='#E74C3C',
            bgcolor='rgba(231, 76, 60, 0.8)',
            bordercolor='#E74C3C',
            font=dict(size=10, color='white'),
            yref='y'
        )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/analysis')
@login_required
def analysis_page():
    return render_template('analysis.html')

@app.route('/alerts')
@login_required
def alerts_page():
    alerts = alert_manager.get_alerts(user_id=current_user.id, limit=50)
    alert_summary = alert_manager.get_alert_summary(user_id=current_user.id)
    return render_template('alerts.html', alerts=alerts, alert_summary=alert_summary)

@app.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html', user=current_user)

@app.route('/user-management')
@login_required
def user_management_page():
    return render_template('user_management.html')

# WebSocket events for real-time updates
@socketio.on('connect')
@login_required
def handle_connect():
    print(f'User {current_user.username} connected to WebSocket')
    emit('status', {'msg': 'Connected to real-time energy monitoring'})

@socketio.on('request_data_update')
@login_required
def handle_data_request():
    global grid_connected, current_data_cache
    
    if grid_connected:
        # Generate fresh current data with enhanced randomness
        current_data = get_current_data()
        
        # Add some real-time variation to make it feel more alive
        current_data['timestamp'] = datetime.now()
        
        # Enhanced random variations for demonstration
        base_solar = current_data.get('solar_power', 0)
        base_wind = current_data.get('wind_power', 0)
        base_consumption = current_data.get('consumption', 0)
        
        # Add small random fluctuations (±2-5%) to simulate real sensor readings
        if base_solar > 0:
            current_data['solar_power'] = max(0, base_solar * random.uniform(0.95, 1.05))
        if base_wind > 0:
            current_data['wind_power'] = max(0, base_wind * random.uniform(0.92, 1.08))
        if base_consumption > 0:
            current_data['consumption'] = max(800, base_consumption * random.uniform(0.98, 1.02))
        
        # Recalculate dependent values
        current_data['total_generation'] = current_data['solar_power'] + current_data['wind_power']
        current_data['net_power'] = current_data['total_generation'] - current_data['consumption']
        
        # Battery simulation with more realistic behavior
        storage_change = (current_data['net_power'] / 10000) * 5  # Rough charge/discharge rate
        current_storage = current_data.get('storage_percentage', 50)
        new_storage = max(0, min(100, current_storage + storage_change + random.uniform(-0.2, 0.2)))
        current_data['storage_percentage'] = round(new_storage, 1)
        current_data['storage_kwh'] = round((new_storage / 100) * 50, 1)  # Assuming 50kWh capacity
        
        # Check for new alerts with enhanced analysis
        alerts_created = alert_analyzer.analyze_and_create_alerts(current_data, user_id=current_user.id)
        
        # Store current data for when disconnected
        current_data_cache = current_data.copy()
    else:
        # Use last known data when disconnected
        current_data = current_data_cache if current_data_cache else get_current_data()
        current_data['timestamp'] = datetime.now()
        alerts_created = []
    
    # Convert datetime objects to strings for JSON serialization
    serializable_data = current_data.copy()
    if 'timestamp' in serializable_data:
        timestamp = serializable_data['timestamp']
        serializable_data['timestamp'] = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
    
    emit('data_update', {
        'data': serializable_data,
        'timestamp': datetime.now().isoformat(),
        'new_alerts': len(alerts_created),
        'grid_connected': grid_connected
    })

def generate_recommendations(current_data, performance_analysis):
    """Generate recommendations based on current data and performance analysis"""
    recommendations = []
    
    # Energy efficiency recommendations
    if performance_analysis.get('avg_overall_efficiency', 1) < 0.8:
        recommendations.append({
            'type': 'efficiency',
            'priority': 'high',
            'title': 'Improve Energy Efficiency',
            'description': 'Overall system efficiency is below 80%. Consider optimizing consumption patterns or checking equipment.'
        })
    
    # Battery management recommendations
    storage_pct = current_data.get('storage_percentage', 50)
    if storage_pct < 30:
        recommendations.append({
            'type': 'battery',
            'priority': 'medium',
            'title': 'Battery Management',
            'description': 'Battery level is low. Consider reducing non-essential consumption or check charging systems.'
        })
    elif storage_pct > 85:
        recommendations.append({
            'type': 'trading',
            'priority': 'low',
            'title': 'Energy Trading Opportunity',
            'description': 'Battery is nearly full. Good time to sell excess energy to the grid.'
        })
    
    # Solar panel recommendations
    if current_data.get('sun_intensity', 0) > 70 and current_data.get('solar_power', 0) < 5000:
        recommendations.append({
            'type': 'maintenance',
            'priority': 'high',
            'title': 'Solar Panel Check',
            'description': 'High sun intensity but low solar power output. Panels may need cleaning or maintenance.'
        })
    
    return recommendations

# Profile management endpoints
@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_update_profile():
    """Update user profile information"""
    try:
        profile_data = request.get_json()
        
        # Validate required fields
        if not profile_data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        # Update user profile
        success = user_manager.update_user_profile(current_user.id, profile_data)
        
        if success:
            # Update current_user object attributes for immediate reflection
            for key, value in profile_data.items():
                if hasattr(current_user, key) and value is not None:
                    setattr(current_user, key, value)
            
            return jsonify({
                'success': True, 
                'message': 'Profile updated successfully',
                'data': {
                    'full_name': current_user.full_name,
                    'phone_number': current_user.phone_number,
                    'address': current_user.address,
                    'pincode': current_user.pincode,
                    'state': current_user.state,
                    'grid_id': current_user.grid_id
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update profile'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# User management endpoints
@app.route('/api/users/export/<format_type>')
@login_required
def api_export_users(format_type):
    """Export users in CSV or JSON format"""
    try:
        if format_type.lower() == 'csv':
            csv_data = user_manager.export_users_csv()
            
            # Create response with CSV data
            from flask import Response
            response = Response(
                csv_data,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename=ecoshakti_users.csv'
                }
            )
            return response
            
        elif format_type.lower() == 'json':
            json_data = user_manager.export_users_json()
            
            # Create response with JSON data
            from flask import Response
            response = Response(
                json_data,
                mimetype='application/json',
                headers={
                    'Content-Disposition': 'attachment; filename=ecoshakti_users.json'
                }
            )
            return response
            
        else:
            return jsonify({'success': False, 'error': 'Invalid format. Use csv or json'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users/import', methods=['POST'])
@login_required
def api_import_users():
    """Import users from uploaded file"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Get overwrite preference
        overwrite_existing = request.form.get('overwrite_existing', 'false').lower() == 'true'
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
        # Determine file type and import
        if file.filename.lower().endswith('.csv'):
            result = user_manager.import_users_from_csv(file_content, overwrite_existing)
        elif file.filename.lower().endswith('.json'):
            result = user_manager.import_users_from_json(file_content, overwrite_existing)
        else:
            return jsonify({
                'success': False, 
                'error': 'Invalid file type. Only CSV and JSON files are supported.'
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users/delete/<user_id>', methods=['DELETE'])
@login_required
def api_delete_user(user_id):
    """Delete a user by ID"""
    try:
        # Prevent self-deletion
        if user_id == current_user.id:
            return jsonify({
                'success': False, 
                'error': 'Cannot delete your own account'
            })
        
        # Delete user
        success = user_manager.delete_user(user_id)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'User {user_id} deleted successfully'
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'User not found or could not be deleted'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users/list')
@login_required
def api_list_users():
    """Get list of all users (for admin purposes)"""
    try:
        users = user_manager.get_all_users()
        users_data = []
        
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'grid_id': user.grid_id,
                'created_at': user.created_at,
                'is_current': user.id == current_user.id
            }
            users_data.append(user_dict)
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total_count': len(users_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/get', methods=['GET'])
@login_required
def api_get_profile():
    """Get current user profile information"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'full_name': current_user.full_name,
                'phone_number': current_user.phone_number,
                'address': current_user.address,
                'pincode': current_user.pincode,
                'state': current_user.state,
                'grid_id': current_user.grid_id,
                'created_at': current_user.created_at
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Grid connection management endpoints
@app.route('/api/grid/status', methods=['GET'])
@login_required
def api_grid_status():
    """Get current grid connection status"""
    global grid_connected
    return jsonify({
        'success': True,
        'connected': grid_connected,
        'status': 'Connected' if grid_connected else 'Disconnected'
    })

@app.route('/api/grid/toggle', methods=['POST'])
@login_required
def api_grid_toggle():
    """Toggle grid connection status"""
    global grid_connected
    try:
        data = request.get_json()
        new_status = data.get('connect', not grid_connected)
        grid_connected = bool(new_status)
        
        return jsonify({
            'success': True,
            'connected': grid_connected,
            'status': 'Connected' if grid_connected else 'Disconnected',
            'message': f'Grid {"connected" if grid_connected else "disconnected"} successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# AI Chatbot endpoints
@app.route('/api/chatbot/ask', methods=['POST'])
@login_required
def api_chatbot_ask():
    """Process chatbot questions about grid data"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False, 
                'error': 'Please provide a question'
            })
        
        # Process the question and generate response
        response = process_chatbot_question(question, current_user.id)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

# Chatbot helper functions
def process_chatbot_question(question, user_id):
    """Process user question and generate intelligent response based on grid data"""
    question_lower = question.lower()
    
    # Get current and historical data
    current_data = get_current_data()
    today_data = get_historical_data(hours=24)
    yesterday_data = get_historical_data_for_date(datetime.now() - timedelta(days=1))
    
    # Calculate aggregated metrics
    today_metrics = calculate_daily_metrics(today_data)
    yesterday_metrics = calculate_daily_metrics(yesterday_data) if yesterday_data else {}
    
    # Check for grid/energy-related questions first
    if any(word in question_lower for word in ['consumption', 'usage', 'used', 'consume', 'energy', 'power', 'kwh', 'watts']):
        return handle_consumption_questions(question_lower, current_data, today_metrics, yesterday_metrics)
    
    elif any(word in question_lower for word in ['storage', 'battery', 'stored', 'charge', 'discharge']):
        return handle_storage_questions(question_lower, current_data, today_metrics, yesterday_metrics)
    
    elif any(word in question_lower for word in ['generation', 'generated', 'produce', 'solar', 'wind', 'renewable']):
        return handle_generation_questions(question_lower, current_data, today_metrics, yesterday_metrics)
    
    elif any(word in question_lower for word in ['efficiency', 'performance', 'status', 'grid', 'health', 'machine', 'fault', 'diagnosis']):
        return handle_efficiency_questions(question_lower, current_data, today_metrics)
    
    elif any(word in question_lower for word in ['trading', 'export', 'import', 'sell', 'buy', 'revenue', 'cost']):
        return handle_trading_questions(question_lower, current_data, today_metrics, yesterday_metrics)
    
    elif any(word in question_lower for word in ['weather', 'sun', 'wind speed', 'intensity', 'temperature']):
        return handle_weather_questions(question_lower, current_data, today_metrics)
    
    elif any(word in question_lower for word in ['alert', 'warning', 'problem', 'fault', 'error']):
        return handle_alert_questions(question_lower, user_id)
    
    elif any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference']):
        return handle_comparison_questions(question_lower, today_metrics, yesterday_metrics)
    
    # Handle general non-energy questions
    else:
        return handle_general_non_energy_questions(question_lower, current_data, today_metrics)

def handle_consumption_questions(question, current_data, today_metrics, yesterday_metrics):
    """Handle questions about energy consumption"""
    if 'today' in question:
        consumption = today_metrics.get('total_consumption', 0)
        return f"📊 **Today's Energy Consumption**: {consumption:.2f} kWh\n\n" + \
               f"Current usage rate: {current_data.get('consumption', 0):,.0f} W\n" + \
               f"Average hourly consumption: {consumption/24:.2f} kWh\n" + \
               f"Peak consumption: {today_metrics.get('peak_consumption', 0):,.0f} W"
    
    elif 'yesterday' in question:
        if yesterday_metrics:
            consumption = yesterday_metrics.get('total_consumption', 0)
            return f"📊 **Yesterday's Energy Consumption**: {consumption:.2f} kWh\n\n" + \
                   f"Average hourly consumption: {consumption/24:.2f} kWh\n" + \
                   f"Peak consumption: {yesterday_metrics.get('peak_consumption', 0):,.0f} W"
        else:
            return "❌ Sorry, I don't have yesterday's consumption data available."
    
    elif 'current' in question or 'now' in question:
        current_consumption = current_data.get('consumption', 0)
        return f"⚡ **Current Energy Consumption**: {current_consumption:,.0f} W\n\n" + \
               f"This represents {(current_consumption/10000)*100:.1f}% of your maximum capacity.\n" + \
               f"Today's total so far: {today_metrics.get('total_consumption', 0):.2f} kWh"
    
    else:
        return f"📊 **Energy Consumption Overview**:\n\n" + \
               f"• Current: {current_data.get('consumption', 0):,.0f} W\n" + \
               f"• Today's total: {today_metrics.get('total_consumption', 0):.2f} kWh\n" + \
               f"• Average today: {today_metrics.get('avg_consumption', 0):,.0f} W"

def handle_storage_questions(question, current_data, today_metrics, yesterday_metrics):
    """Handle questions about battery storage"""
    current_storage = current_data.get('storage_percentage', 0)
    current_kwh = current_data.get('storage_kwh', 0)
    
    if 'today' in question:
        return f"🔋 **Today's Battery Storage**:\n\n" + \
               f"Current level: {current_storage:.1f}% ({current_kwh:.1f} kWh)\n" + \
               f"Highest level today: {today_metrics.get('max_storage', 0):.1f}%\n" + \
               f"Lowest level today: {today_metrics.get('min_storage', 0):.1f}%\n" + \
               f"Average level: {today_metrics.get('avg_storage', 0):.1f}%"
    
    elif 'yesterday' in question:
        if yesterday_metrics:
            return f"🔋 **Yesterday's Battery Storage**:\n\n" + \
                   f"Highest level: {yesterday_metrics.get('max_storage', 0):.1f}%\n" + \
                   f"Lowest level: {yesterday_metrics.get('min_storage', 0):.1f}%\n" + \
                   f"Average level: {yesterday_metrics.get('avg_storage', 0):.1f}%"
        else:
            return "❌ Sorry, I don't have yesterday's storage data available."
    
    elif 'current' in question or 'now' in question:
        status = "High" if current_storage > 75 else "Medium" if current_storage > 25 else "Low"
        return f"🔋 **Current Battery Status**: {status}\n\n" + \
               f"Level: {current_storage:.1f}% ({current_kwh:.1f} kWh)\n" + \
               f"Capacity: {current_kwh:.1f} kWh out of 50 kWh total\n" + \
               f"Estimated runtime: {(current_kwh/5):.1f} hours at current consumption"
    
    else:
        return f"🔋 **Battery Storage Overview**:\n\n" + \
               f"• Current: {current_storage:.1f}% ({current_kwh:.1f} kWh)\n" + \
               f"• Today's range: {today_metrics.get('min_storage', 0):.1f}% - {today_metrics.get('max_storage', 0):.1f}%\n" + \
               f"• Average today: {today_metrics.get('avg_storage', 0):.1f}%"

def handle_generation_questions(question, current_data, today_metrics, yesterday_metrics):
    """Handle questions about energy generation"""
    if 'today' in question:
        solar_gen = today_metrics.get('total_solar_generation', 0)
        wind_gen = today_metrics.get('total_wind_generation', 0)
        total_gen = solar_gen + wind_gen
        return f"⚡ **Today's Energy Generation**: {total_gen:.2f} kWh\n\n" + \
               f"☀️ Solar: {solar_gen:.2f} kWh ({(solar_gen/total_gen*100) if total_gen > 0 else 0:.1f}%)\n" + \
               f"💨 Wind: {wind_gen:.2f} kWh ({(wind_gen/total_gen*100) if total_gen > 0 else 0:.1f}%)\n" + \
               f"Peak generation: {today_metrics.get('peak_generation', 0):,.0f} W"
    
    elif 'yesterday' in question:
        if yesterday_metrics:
            solar_gen = yesterday_metrics.get('total_solar_generation', 0)
            wind_gen = yesterday_metrics.get('total_wind_generation', 0)
            total_gen = solar_gen + wind_gen
            return f"⚡ **Yesterday's Energy Generation**: {total_gen:.2f} kWh\n\n" + \
                   f"☀️ Solar: {solar_gen:.2f} kWh\n" + \
                   f"💨 Wind: {wind_gen:.2f} kWh\n" + \
                   f"Peak generation: {yesterday_metrics.get('peak_generation', 0):,.0f} W"
        else:
            return "❌ Sorry, I don't have yesterday's generation data available."
    
    elif 'solar' in question:
        current_solar = current_data.get('solar_power', 0)
        return f"☀️ **Solar Generation**:\n\n" + \
               f"Current output: {current_solar:,.0f} W\n" + \
               f"Today's total: {today_metrics.get('total_solar_generation', 0):.2f} kWh\n" + \
               f"Efficiency: {((current_solar / (current_data.get('sun_intensity', 1) * 75)) * 100):.1f}%\n" + \
               f"Sun intensity: {current_data.get('sun_intensity', 0):.1f}%"
    
    elif 'wind' in question:
        current_wind = current_data.get('wind_power', 0)
        return f"💨 **Wind Generation**:\n\n" + \
               f"Current output: {current_wind:,.0f} W\n" + \
               f"Today's total: {today_metrics.get('total_wind_generation', 0):.2f} kWh\n" + \
               f"Wind speed: {current_data.get('wind_speed', 0):.1f} m/s"
    
    else:
        current_total = current_data.get('total_generation', 0)
        return f"⚡ **Energy Generation Overview**:\n\n" + \
               f"• Current total: {current_total:,.0f} W\n" + \
               f"• Solar: {current_data.get('solar_power', 0):,.0f} W\n" + \
               f"• Wind: {current_data.get('wind_power', 0):,.0f} W\n" + \
               f"• Today's total: {today_metrics.get('total_generation', 0):.2f} kWh"

def handle_efficiency_questions(question, current_data, today_metrics):
    """Handle questions about system efficiency and performance"""
    question_lower = question.lower()
    solar_efficiency = ((current_data.get('solar_power', 0) / (current_data.get('sun_intensity', 1) * 75)) * 100) if current_data.get('sun_intensity', 0) > 0 else 0
    energy_independence = (today_metrics.get('total_generation', 0) / today_metrics.get('total_consumption', 1)) * 100 if today_metrics.get('total_consumption', 0) > 0 else 0
    
    # Machine health specific questions
    if any(word in question_lower for word in ['health', 'machine', 'fault', 'diagnosis', 'equipment', 'panel']):
        return handle_machine_health_questions(question_lower, current_data, solar_efficiency)
    
    # General efficiency questions
    return f"📈 **System Performance Overview**:\n\n" + \
           f"• Solar efficiency: {solar_efficiency:.1f}%\n" + \
           f"• Energy independence: {energy_independence:.1f}%\n" + \
           f"• Current generation: {current_data.get('total_generation', 0):,.0f} W\n" + \
           f"• Current consumption: {current_data.get('consumption', 0):,.0f} W\n" + \
           f"• Net energy balance: {current_data.get('net_power', 0):,.0f} W\n" + \
           f"• System status: {'🟢 Optimal' if energy_independence > 100 else '🟡 Good' if energy_independence > 80 else '🔴 Needs attention'}"

def handle_machine_health_questions(question, current_data, solar_efficiency):
    """Handle specific machine health and diagnostic questions"""
    sun_intensity = current_data.get('sun_intensity', 0)
    solar_power = current_data.get('solar_power', 0)
    expected_power = (sun_intensity / 100) * 10000 * 0.75 if sun_intensity > 0 else 0
    efficiency = (solar_power / expected_power * 100) if expected_power > 0 else 0
    
    # Determine health status based on efficiency
    if efficiency >= 85:
        health_status = 'Excellent'
        health_icon = '🟢'
        health_color = 'Green'
        diagnosis = 'Solar panels are operating at optimal efficiency. No maintenance required.'
    elif efficiency >= 70:
        health_status = 'Good'
        health_icon = '🔵'
        health_color = 'Blue'
        diagnosis = 'Solar panels are performing well. Minor optimization possible.'
    elif efficiency >= 50:
        health_status = 'Fair'
        health_icon = '🟡'
        health_color = 'Yellow'
        diagnosis = 'Solar panels show moderate efficiency. Consider cleaning or inspection.'
    elif efficiency >= 30:
        health_status = 'Poor'
        health_icon = '🟠'
        health_color = 'Orange'
        diagnosis = 'Solar panels are underperforming. Maintenance required soon.'
    else:
        health_status = 'Critical'
        health_icon = '🔴'
        health_color = 'Red'
        diagnosis = 'Solar panels may have significant issues. Immediate inspection recommended.'
    
    # Fault detection logic
    fault_detected = False
    fault_details = []
    
    if sun_intensity > 70 and solar_power < 5000:
        fault_detected = True
        fault_details.append('⚠️ High sun intensity but low power output')
        fault_details.append('💡 Possible causes: Dirty panels, shading, or equipment malfunction')
    
    if efficiency < 50 and sun_intensity > 30:
        fault_detected = True
        fault_details.append('⚠️ Low efficiency despite adequate sunlight')
        fault_details.append('💡 Possible causes: Panel degradation, inverter issues, or wiring problems')
    
    # Build response
    response = f"🏥 **Machine Health Analysis**:\n\n"
    response += f"{health_icon} **Overall Health**: {health_status} ({health_color})\n"
    response += f"📊 **Efficiency**: {efficiency:.1f}%\n"
    response += f"☀️ **Sun Intensity**: {sun_intensity:.1f}%\n"
    response += f"⚡ **Current Output**: {solar_power:,.0f}W\n"
    response += f"🎯 **Expected Output**: {expected_power:,.0f}W\n\n"
    
    response += f"🔍 **Diagnosis**: {diagnosis}\n\n"
    
    if fault_detected:
        response += f"🚨 **Fault Detection**:\n"
        for detail in fault_details:
            response += f"{detail}\n"
        response += f"\n📞 **Recommendation**: Schedule maintenance inspection\n"
    else:
        response += f"✅ **System Status**: No faults detected\n"
        response += f"🔧 **Maintenance**: Regular cleaning recommended\n"
    
    # Add performance trend
    if efficiency >= 85:
        response += f"📈 **Performance**: Excellent - panels operating optimally"
    elif efficiency >= 70:
        response += f"📊 **Performance**: Good - minor efficiency improvements possible"
    elif efficiency >= 50:
        response += f"📉 **Performance**: Fair - consider maintenance to improve output"
    else:
        response += f"🔴 **Performance**: Poor - immediate attention required"
    
    return response

def handle_trading_questions(question, current_data, today_metrics, yesterday_metrics):
    """Handle questions about energy trading and grid interaction"""
    net_power = current_data.get('net_power', 0)
    grid_export = today_metrics.get('total_grid_export', 0)
    grid_import = today_metrics.get('total_grid_import', 0)
    
    if 'export' in question or 'sell' in question:
        return f"📤 **Energy Export Overview**:\n\n" + \
               f"Today's exports: {grid_export:.2f} kWh\n" + \
               f"Estimated revenue: ${grid_export * 0.15:.2f}\n" + \
               f"Current surplus: {max(0, net_power):,.0f} W\n" + \
               f"Export recommendation: {'🟢 Good time to sell' if net_power > 2000 else '🟡 Moderate surplus' if net_power > 0 else '🔴 No surplus available'}"
    
    elif 'import' in question or 'buy' in question:
        return f"📥 **Energy Import Overview**:\n\n" + \
               f"Today's imports: {grid_import:.2f} kWh\n" + \
               f"Estimated cost: ${grid_import * 0.12:.2f}\n" + \
               f"Current deficit: {abs(min(0, net_power)):,.0f} W\n" + \
               f"Import status: {'🔴 High import needed' if net_power < -1000 else '🟡 Moderate import' if net_power < 0 else '🟢 No import needed'}"
    
    else:
        net_revenue = (grid_export * 0.15) - (grid_import * 0.12)
        return f"💰 **Energy Trading Summary**:\n\n" + \
               f"Today's exports: {grid_export:.2f} kWh\n" + \
               f"Today's imports: {grid_import:.2f} kWh\n" + \
               f"Net energy balance: {grid_export - grid_import:.2f} kWh\n" + \
               f"Net revenue: ${net_revenue:.2f}\n" + \
               f"Trading advice: {'🟢 Sell excess energy' if net_power > 2000 else '🟡 Optimize consumption' if abs(net_power) < 1000 else '🔴 Consider purchasing energy'}"

def handle_weather_questions(question, current_data, today_metrics):
    """Handle questions about weather conditions affecting generation"""
    sun_intensity = current_data.get('sun_intensity', 0)
    wind_speed = current_data.get('wind_speed', 0)
    
    return f"🌤️ **Current Weather Conditions**:\n\n" + \
           f"☀️ Sun intensity: {sun_intensity:.1f}%\n" + \
           f"💨 Wind speed: {wind_speed:.1f} m/s\n" + \
           f"Solar impact: {'🟢 Excellent' if sun_intensity > 80 else '🟡 Good' if sun_intensity > 50 else '🔴 Poor'}\n" + \
           f"Wind impact: {'🟢 Excellent' if wind_speed > 8 else '🟡 Good' if wind_speed > 4 else '🔴 Poor'}\n" + \
           f"Overall generation potential: {((sun_intensity + wind_speed*10)/110)*100:.1f}%"

def handle_alert_questions(question, user_id):
    """Handle questions about system alerts and warnings"""
    recent_alerts = alert_manager.get_alerts(user_id=user_id, limit=5)
    alert_summary = alert_manager.get_alert_summary(user_id=user_id)
    
    if recent_alerts:
        alert_text = "\n".join([f"• {alert.title} ({alert.severity.value})" for alert in recent_alerts[:3]])
        return f"🚨 **Recent System Alerts**:\n\n{alert_text}\n\n" + \
               f"Total alerts: {alert_summary.get('total', 0)}\n" + \
               f"Unread: {alert_summary.get('unread', 0)}\n" + \
               f"Critical: {alert_summary.get('critical', 0)}"
    else:
        return "✅ **System Status**: No recent alerts\n\nYour renewable energy system is operating normally with no warnings or critical issues."

def handle_comparison_questions(question, today_metrics, yesterday_metrics):
    """Handle comparison questions between different time periods"""
    if not yesterday_metrics:
        return "❌ Sorry, I don't have enough data to make comparisons with yesterday."
    
    today_gen = today_metrics.get('total_generation', 0)
    yesterday_gen = yesterday_metrics.get('total_generation', 0)
    today_cons = today_metrics.get('total_consumption', 0)
    yesterday_cons = yesterday_metrics.get('total_consumption', 0)
    
    gen_change = ((today_gen - yesterday_gen) / yesterday_gen * 100) if yesterday_gen > 0 else 0
    cons_change = ((today_cons - yesterday_cons) / yesterday_cons * 100) if yesterday_cons > 0 else 0
    
    return f"📊 **Today vs Yesterday Comparison**:\n\n" + \
           f"**Generation:**\n" + \
           f"• Today: {today_gen:.2f} kWh\n" + \
           f"• Yesterday: {yesterday_gen:.2f} kWh\n" + \
           f"• Change: {gen_change:+.1f}%\n\n" + \
           f"**Consumption:**\n" + \
           f"• Today: {today_cons:.2f} kWh\n" + \
           f"• Yesterday: {yesterday_cons:.2f} kWh\n" + \
           f"• Change: {cons_change:+.1f}%"

def handle_general_questions(question, current_data, today_metrics):
    """Handle general questions about the system"""
    return f"📋 **Grid System Overview**:\n\n" + \
           f"⚡ **Current Status:**\n" + \
           f"• Generation: {current_data.get('total_generation', 0):,.0f} W\n" + \
           f"• Consumption: {current_data.get('consumption', 0):,.0f} W\n" + \
           f"• Battery: {current_data.get('storage_percentage', 0):.1f}%\n" + \
           f"• Net balance: {current_data.get('net_power', 0):,.0f} W\n\n" + \
           f"📊 **Today's Performance:**\n" + \
           f"• Total generated: {today_metrics.get('total_generation', 0):.2f} kWh\n" + \
           f"• Total consumed: {today_metrics.get('total_consumption', 0):.2f} kWh\n" + \
           f"• Energy independence: {(today_metrics.get('total_generation', 0) / today_metrics.get('total_consumption', 1) * 100) if today_metrics.get('total_consumption', 0) > 0 else 0:.1f}%"

def handle_general_non_energy_questions(question, current_data, today_metrics):
    """Handle general non-energy questions with intelligent responses"""
    question_lower = question.lower()
    
    # Greeting patterns
    if any(word in question_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "👋 **Hello there!** I'm your intelligent Grid AI Assistant!\n\n" + \
               f"I'm here to help you with:\n" + \
               f"🔋 Energy & grid management questions\n" + \
               f"📊 System performance analysis\n" + \
               f"💡 General assistance and information\n" + \
               f"🤖 Smart recommendations\n\n" + \
               f"**Quick Tip:** Try asking me about your energy consumption, battery status, or just say 'help' for more options!"
    
    # Help and assistance
    elif any(word in question_lower for word in ['help', 'assist', 'support', 'what can you do', 'commands']):
        return "🆘 **I'm here to help!** Here's what I can assist you with:\n\n" + \
               f"🔋 **Energy Questions:**\n" + \
               f"• 'What's my consumption today?'\n" + \
               f"• 'How much battery do I have?'\n" + \
               f"• 'What's my solar generation?'\n" + \
               f"• 'Compare today vs yesterday'\n\n" + \
               f"💡 **General Topics:**\n" + \
               f"• Time and date information\n" + \
               f"• Basic calculations\n" + \
               f"• Weather discussions\n" + \
               f"• Technology explanations\n" + \
               f"• General knowledge questions\n\n" + \
               f"Just ask me anything! I'll do my best to help! 🤖"
    
    # Time and date questions
    elif any(word in question_lower for word in ['time', 'date', 'today', 'now', 'current', 'what day', 'what time']):
        now = datetime.now()
        return f"🕐 **Current Time & Date Information:**\n\n" + \
               f"📅 Date: {now.strftime('%A, %B %d, %Y')}\n" + \
               f"⏰ Time: {now.strftime('%I:%M %p')}\n" + \
               f"🌐 Day of week: {now.strftime('%A')}\n" + \
               f"📊 Week of year: Week {now.strftime('%U')}\n\n" + \
               f"💡 **Bonus:** Your grid has been active for {(now.hour * 60 + now.minute)} minutes today!"
    
    # Math and calculations
    elif any(word in question_lower for word in ['calculate', 'math', 'plus', 'minus', 'multiply', 'divide', '+', '-', '*', '/', 'equation']):
        # Simple math detection
        import re
        math_pattern = r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)'
        match = re.search(math_pattern, question)
        
        if match:
            num1, operator, num2 = match.groups()
            num1, num2 = float(num1), float(num2)
            
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/' and num2 != 0:
                result = num1 / num2
            else:
                result = "Error: Division by zero"
            
            return f"🧮 **Math Calculation:**\n\n" + \
                   f"📝 Problem: {num1} {operator} {num2}\n" + \
                   f"✅ Answer: **{result}**\n\n" + \
                   f"💡 **Energy Context:** That's like having {result * 100:.0f}W of power generation!"
        else:
            return "🧮 **Math Helper:**\n\n" + \
                   f"I can help with basic calculations! Try asking:\n" + \
                   f"• '15 + 25'\n" + \
                   f"• '100 / 4'\n" + \
                   f"• 'What's 50 * 2?'\n\n" + \
                   f"I can also relate numbers to your energy system for better context!"
    
    # Weather (general, not grid-related)
    elif 'weather' in question_lower and not any(word in question_lower for word in ['solar', 'generation', 'power', 'intensity']):
        return "🌤️ **Weather Discussion:**\n\n" + \
               f"I don't have access to real weather data, but I can see how weather affects your renewable energy system!\n\n" + \
               f"🌞 **Current sun intensity:** {current_data.get('sun_intensity', 0):.1f}%\n" + \
               f"💨 **Wind conditions:** {current_data.get('wind_speed', 0):.1f} m/s\n\n" + \
               f"For detailed weather forecasts, I recommend checking your local weather service. Meanwhile, I can help you understand how weather impacts your energy generation!"
    
    # Technology explanations
    elif any(word in question_lower for word in ['explain', 'what is', 'how does', 'technology', 'ai', 'artificial intelligence', 'machine learning']):
        if any(word in question_lower for word in ['ai', 'artificial intelligence']):
            return "🤖 **About Artificial Intelligence:**\n\n" + \
                   f"AI is technology that enables machines to perform tasks that typically require human intelligence!\n\n" + \
                   f"🧠 **In this system, I use AI for:**\n" + \
                   f"• Understanding your natural language questions\n" + \
                   f"• Analyzing your energy patterns\n" + \
                   f"• Predicting optimal energy usage\n" + \
                   f"• Detecting system anomalies\n\n" + \
                   f"💡 **Fun fact:** I process your grid data in real-time to give you personalized insights!"
        
        elif any(word in question_lower for word in ['renewable energy', 'solar', 'wind energy']):
            return "🌱 **Renewable Energy Explained:**\n\n" + \
                   f"Renewable energy comes from natural sources that replenish themselves!\n\n" + \
                   f"☀️ **Solar Power:** Converts sunlight into electricity using photovoltaic panels\n" + \
                   f"💨 **Wind Power:** Uses wind turbines to generate electricity from air movement\n" + \
                   f"🔋 **Battery Storage:** Stores excess energy for use when generation is low\n\n" + \
                   f"🏠 **Your System:** Currently generating {current_data.get('total_generation', 0):,.0f}W of clean energy!"
        
        else:
            return "💡 **Technology Discussion:**\n\n" + \
                   f"I'd be happy to explain technology concepts! I'm particularly knowledgeable about:\n\n" + \
                   f"🔋 Renewable energy systems\n" + \
                   f"🤖 Artificial intelligence\n" + \
                   f"📊 Data analysis\n" + \
                   f"🌐 Smart grid technology\n" + \
                   f"⚡ Energy management\n\n" + \
                   f"What specific technology would you like to learn about?"
    
    # Appreciation and thanks
    elif any(word in question_lower for word in ['thank', 'thanks', 'appreciate', 'good job', 'well done', 'awesome']):
        return "😊 **You're very welcome!**\n\n" + \
               f"I'm glad I could help! It's my pleasure to assist you with your renewable energy system and answer your questions.\n\n" + \
               f"🔋 **Current system status:** Everything looks good!\n" + \
               f"📊 **Performance:** {(today_metrics.get('total_generation', 0) / today_metrics.get('total_consumption', 1) * 100) if today_metrics.get('total_consumption', 0) > 0 else 0:.1f}% energy independence today\n\n" + \
               f"Feel free to ask me anything else! 🤖✨"
    
    # Who are you / about
    elif any(word in question_lower for word in ['who are you', 'what are you', 'about you', 'your name']):
        return "🤖 **About Me - Your Grid AI Assistant:**\n\n" + \
               f"I'm an intelligent AI assistant specifically designed for renewable energy systems!\n\n" + \
               f"🎯 **My Purpose:**\n" + \
               f"• Monitor and analyze your energy grid\n" + \
               f"• Answer questions about your system\n" + \
               f"• Provide insights and recommendations\n" + \
               f"• Help with general questions too!\n\n" + \
               f"🧠 **My Capabilities:**\n" + \
               f"• Real-time data analysis\n" + \
               f"• Natural language understanding\n" + \
               f"• Energy optimization suggestions\n" + \
               f"• 24/7 assistance\n\n" + \
               f"💚 I'm here to make your renewable energy experience better!"
    
    # Fun and entertainment
    elif any(word in question_lower for word in ['joke', 'funny', 'laugh', 'entertainment', 'fun']):
        jokes = [
            "Why don't solar panels ever get tired? Because they're always charged up! ⚡😄",
            "What did the wind turbine say to the solar panel? 'You're really bright!' ☀️💨",
            "Why did the battery go to therapy? It had too many negative charges! 🔋😂",
            "What's a renewable energy system's favorite music? Heavy metal... because of all the equipment! 🎵⚡",
            "Why don't energy meters lie? Because they're always current! 📊⚡"
        ]
        import random
        joke = random.choice(jokes)
        
        return f"😄 **Here's a renewable energy joke for you:**\n\n" + \
               f"{joke}\n\n" + \
               f"🎉 **Fun Fact:** While we're having fun, your system generated {current_data.get('total_generation', 0):,.0f}W of clean energy just now!"
    
    # Default response for unrecognized questions
    else:
        return f"🤔 **Interesting question!**\n\n" + \
               f"I may not have a specific answer for that, but I'm always learning! \n\n" + \
               f"💡 **Here's what I can definitely help with:**\n" + \
               f"🔋 Your energy system (consumption, generation, storage)\n" + \
               f"📊 Performance analysis and comparisons\n" + \
               f"⚡ Grid optimization recommendations\n" + \
               f"🕐 Time/date information\n" + \
               f"🧮 Basic calculations\n" + \
               f"🤖 Technology explanations\n\n" + \
               f"**Current system status:** Generating {current_data.get('total_generation', 0):,.0f}W, consuming {current_data.get('consumption', 0):,.0f}W\n\n" + \
               f"Try rephrasing your question or ask me about your renewable energy system! 🌱"

def calculate_daily_metrics(data_points):
    """Calculate aggregated daily metrics from historical data"""
    if not data_points:
        return {}
    
    df = pd.DataFrame(data_points)
    
    return {
        'total_consumption': (df['consumption'].sum() / 1000) / 60,  # Convert to kWh
        'total_generation': ((df['solar_power'] + df['wind_power']).sum() / 1000) / 60,
        'total_solar_generation': (df['solar_power'].sum() / 1000) / 60,
        'total_wind_generation': (df['wind_power'].sum() / 1000) / 60,
        'total_grid_export': (df['grid_export'].sum() / 1000) / 60,
        'total_grid_import': (df['grid_import'].sum() / 1000) / 60,
        'avg_consumption': df['consumption'].mean(),
        'avg_generation': (df['solar_power'] + df['wind_power']).mean(),
        'avg_storage': df['storage_percentage'].mean(),
        'max_storage': df['storage_percentage'].max(),
        'min_storage': df['storage_percentage'].min(),
        'peak_consumption': df['consumption'].max(),
        'peak_generation': (df['solar_power'] + df['wind_power']).max()
    }

def get_historical_data_for_date(target_date):
    """Get historical data for a specific date"""
    try:
        # For demo purposes, generate data for the target date
        # In a real system, this would query actual historical data
        start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=24)
        
        data_points = []
        current_time = start_time
        
        while current_time < end_time:
            # Generate historical data point
            data_point = data_generator.generate_historical_point(current_time)
            data_points.append(data_point)
            current_time += timedelta(minutes=1)
        
        return data_points
    except Exception as e:
        print(f"Error getting historical data for date: {e}")
        return []

def initialize_app():
    """Initialize the application for production deployment"""
    print("Initializing EcoShakti monitoring system...")
    
    # Generate some sample data for ML training
    sample_data = data_generator.generate_complete_dataset(hours_back=72)
    
    # Train models if they don't exist
    try:
        ml_manager.train_solar_predictor(sample_data, epochs=50)
        ml_manager.train_fault_detector(sample_data, epochs=50)
        print("ML models trained successfully!")
    except Exception as e:
        print(f"Warning: Could not train ML models: {e}")
    
    print("EcoShakti initialization complete!")

# Initialize the app when imported (for production deployment)
if os.environ.get('FLASK_ENV') == 'production':
    initialize_app()

if __name__ == '__main__':
    # Only run the development server if not in production
    if os.environ.get('FLASK_ENV') != 'production':
        # Initialize for development
        initialize_app()
        print("Starting Flask-SocketIO development server...")
        socketio.run(app, debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("Production mode: Use gunicorn to start the server")
