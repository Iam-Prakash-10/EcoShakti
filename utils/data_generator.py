import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math
import random

class RenewableEnergyDataGenerator:
    def __init__(self):
        self.solar_efficiency = 0.85 + random.uniform(-0.15, 0.10)  # Solar panel efficiency
        self.wind_efficiency = 0.80 + random.uniform(-0.10, 0.15)   # Wind turbine efficiency
        
    def generate_solar_data(self, hours_back=24):
        """Generate realistic solar energy data with enhanced randomness and weather patterns"""
        current_time = datetime.now()
        data = []
        
        # Generate different weather patterns for variety
        weather_patterns = ['sunny', 'partly_cloudy', 'cloudy', 'clear']
        current_weather = random.choice(weather_patterns)
        weather_change_interval = random.randint(60, 180)  # Change weather every 1-3 hours
        
        for i in range(hours_back * 60):  # Generate minute-by-minute data
            timestamp = current_time - timedelta(minutes=i)
            hour = timestamp.hour
            minute = timestamp.minute
            
            # Change weather pattern periodically
            if i % weather_change_interval == 0:
                current_weather = random.choice(weather_patterns)
            
            # Base sun intensity with more complex pattern
            if 5 <= hour <= 19:  # Extended daylight hours
                # Multi-layered sine wave for more realistic pattern
                primary_angle = math.sin((hour - 5) * math.pi / 14)  # Main daily curve
                secondary_angle = math.sin((minute) * math.pi / 30)  # Minute variations
                base_intensity = max(0, primary_angle * 95 + secondary_angle * 5)
                
                # Peak hours boost (10 AM - 3 PM)
                if 10 <= hour <= 15:
                    base_intensity = min(100, base_intensity * random.uniform(1.1, 1.3))
            else:
                base_intensity = random.uniform(0, 2)  # Minimal night readings
            
            # Weather-based variations with more dramatic changes
            weather_factors = {
                'sunny': random.uniform(0.9, 1.0),
                'clear': random.uniform(0.85, 0.95), 
                'partly_cloudy': random.uniform(0.6, 0.85),
                'cloudy': random.uniform(0.3, 0.65)
            }
            weather_factor = weather_factors[current_weather]
            
            # Add random cloud shadows and atmospheric effects
            atmospheric_noise = random.uniform(-8, 12)
            cloud_shadow = random.uniform(-15, 5) if random.random() < 0.15 else 0
            
            sun_intensity = max(0, min(100, base_intensity * weather_factor + atmospheric_noise + cloud_shadow))
            
            # Enhanced power generation calculation
            max_power = random.uniform(9500, 10500)  # Slight system variations
            efficiency_variation = random.uniform(0.95, 1.05)  # Daily efficiency changes
            power_generation = (sun_intensity / 100) * max_power * self.solar_efficiency * efficiency_variation
            
            # More varied fault conditions
            if random.random() < 0.08:  # Increased fault probability
                fault_severity = random.choice(['minor', 'moderate', 'severe'])
                fault_factors = {'minor': random.uniform(0.8, 0.9), 'moderate': random.uniform(0.5, 0.8), 'severe': random.uniform(0.2, 0.5)}
                power_generation *= fault_factors[fault_severity]
            
            data.append({
                'timestamp': timestamp,
                'sun_intensity': round(sun_intensity, 2),
                'solar_power': round(power_generation, 2),
                'type': 'solar'
            })
        
        return data
    
    def generate_wind_data(self, hours_back=24):
        """Generate realistic wind energy data with enhanced variations"""
        current_time = datetime.now()
        data = []
        
        # Generate wind patterns (calm, breezy, windy, stormy)
        wind_patterns = ['calm', 'light', 'moderate', 'strong', 'gusty']
        current_pattern = random.choice(wind_patterns)
        pattern_change_interval = random.randint(120, 300)  # Change every 2-5 hours
        
        for i in range(hours_back * 60):
            timestamp = current_time - timedelta(minutes=i)
            hour = timestamp.hour
            minute = timestamp.minute
            
            # Change wind pattern periodically
            if i % pattern_change_interval == 0:
                current_pattern = random.choice(wind_patterns)
            
            # Enhanced base wind calculation with seasonal and diurnal patterns
            # More wind at night and early morning, less during midday
            diurnal_factor = 1.2 - 0.4 * math.sin((hour - 6) * math.pi / 12)
            seasonal_base = random.uniform(6, 12)  # Seasonal variation
            base_wind = seasonal_base * diurnal_factor
            
            # Wind pattern modifiers
            pattern_factors = {
                'calm': random.uniform(0.3, 0.6),
                'light': random.uniform(0.6, 0.9),
                'moderate': random.uniform(0.9, 1.2),
                'strong': random.uniform(1.2, 1.6),
                'gusty': random.uniform(0.8, 1.8)  # High variability
            }
            
            # Add turbulence and gusts
            turbulence = random.uniform(-3, 3)
            gust_chance = 0.1 if current_pattern == 'gusty' else 0.03
            gust = random.uniform(3, 8) if random.random() < gust_chance else 0
            
            wind_speed = max(0, base_wind * pattern_factors[current_pattern] + turbulence + gust)
            
            # Enhanced wind turbine power curve with more realistic variations
            max_power = random.uniform(7800, 8200)  # System variations
            turbine_efficiency = random.uniform(0.95, 1.05)
            
            if wind_speed < 3:  # Cut-in speed
                wind_power = random.uniform(0, 50)  # Minimal parasitic power
            elif wind_speed > 25:  # Cut-out speed (safety)
                wind_power = random.uniform(0, 100)  # Emergency shutdown
            elif wind_speed > 14:  # Rated speed
                wind_power = max_power * random.uniform(0.95, 1.02)  # Near maximum
            else:
                # More complex power curve with efficiency variations
                base_power = max_power * ((wind_speed - 3) / 11) ** 2.8  # Slightly less than cubic
                wind_power = base_power * turbine_efficiency
            
            wind_power *= self.wind_efficiency
            
            # Enhanced fault simulation
            if random.random() < 0.05:  # Increased fault probability
                fault_types = ['blade_issue', 'gearbox', 'electrical', 'maintenance']
                fault_type = random.choice(fault_types)
                fault_reductions = {
                    'blade_issue': random.uniform(0.4, 0.7),
                    'gearbox': random.uniform(0.2, 0.5),
                    'electrical': random.uniform(0.1, 0.6),
                    'maintenance': random.uniform(0.0, 0.3)
                }
                wind_power *= fault_reductions[fault_type]
            
            data.append({
                'timestamp': timestamp,
                'wind_speed': round(wind_speed, 2),
                'wind_power': round(wind_power, 2),
                'type': 'wind'
            })
        
        return data
    
    def generate_consumption_data(self, hours_back=24):
        """Generate realistic energy consumption data with appliance-based patterns"""
        current_time = datetime.now()
        data = []
        
        # Define consumption profiles
        consumption_profiles = ['residential', 'commercial', 'mixed']
        profile = random.choice(consumption_profiles)
        
        for i in range(hours_back * 60):
            timestamp = current_time - timedelta(minutes=i)
            hour = timestamp.hour
            minute = timestamp.minute
            day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
            
            # Base consumption patterns by profile
            if profile == 'residential':
                # Residential: morning peak (6-9), evening peak (17-22), low at night
                if 6 <= hour <= 9:  # Morning peak
                    base_consumption = random.uniform(4500, 7000)
                elif 17 <= hour <= 22:  # Evening peak
                    base_consumption = random.uniform(5500, 8500)
                elif 23 <= hour or hour <= 5:  # Night
                    base_consumption = random.uniform(1500, 2800)
                else:  # Daytime
                    base_consumption = random.uniform(2800, 4500)
            
            elif profile == 'commercial':
                # Commercial: high during business hours, low at night/weekends
                if day_of_week >= 5:  # Weekend
                    base_consumption = random.uniform(1200, 2500)
                elif 8 <= hour <= 18:  # Business hours
                    base_consumption = random.uniform(6000, 9500)
                else:
                    base_consumption = random.uniform(2000, 3500)
            
            else:  # Mixed profile
                # Combination of patterns with more variation
                daily_factor = 1 + 0.3 * math.sin((hour - 6) * math.pi / 12)
                base_consumption = random.uniform(3000, 6500) * daily_factor
            
            # Add appliance-specific variations with more randomness
            appliance_spikes = {
                'hvac': {'prob': 0.25, 'power': random.uniform(1000, 3000)},
                'electric_vehicle': {'prob': 0.15, 'power': random.uniform(3000, 7000)},
                'water_heater': {'prob': 0.18, 'power': random.uniform(2000, 4000)},
                'kitchen': {'prob': 0.12, 'power': random.uniform(800, 2000)},
                'laundry': {'prob': 0.08, 'power': random.uniform(1500, 2500)},
                'electronics': {'prob': 0.3, 'power': random.uniform(200, 800)}
            }
            
            # Apply random appliance usage
            for appliance, config in appliance_spikes.items():
                if random.random() < config['prob']:
                    base_consumption += config['power']
            
            # Weather-based consumption (AC/heating)
            weather_adjustment = random.uniform(-500, 1500)
            
            # Random minute-to-minute variations
            minute_variation = random.uniform(-300, 300)
            
            consumption = max(800, base_consumption + weather_adjustment + minute_variation)
            
            data.append({
                'timestamp': timestamp,
                'consumption': round(consumption, 2),
                'type': 'consumption'
            })
        
        return data
    
    def generate_storage_data(self, solar_data, wind_data, consumption_data):
        """Generate battery storage data based on generation and consumption"""
        storage_data = []
        battery_capacity = 20000  # 20kWh battery
        current_storage = battery_capacity * 0.5  # Start at 50%
        
        for i in range(len(solar_data)):
            total_generation = solar_data[i]['solar_power'] + wind_data[i]['wind_power']
            consumption = consumption_data[i]['consumption']
            
            net_power = total_generation - consumption
            
            # Battery charging/discharging
            if net_power > 0:  # Surplus - charge battery
                charge_power = min(net_power, battery_capacity * 0.1)  # Max 10% per hour charging rate
                current_storage = min(battery_capacity, current_storage + (charge_power / 60))
                grid_export = max(0, net_power - charge_power)
            else:  # Deficit - discharge battery
                discharge_power = min(abs(net_power), current_storage * 6, battery_capacity * 0.2)  # Max discharge rate
                current_storage = max(0, current_storage - (discharge_power / 60))
                grid_import = max(0, abs(net_power) - discharge_power)
            
            storage_percentage = (current_storage / battery_capacity) * 100
            
            storage_data.append({
                'timestamp': solar_data[i]['timestamp'],
                'storage_kwh': round(current_storage, 2),
                'storage_percentage': round(storage_percentage, 2),
                'grid_export': round(grid_export if net_power > 0 else 0, 2),
                'grid_import': round(grid_import if net_power < 0 else 0, 2),
                'net_power': round(net_power, 2)
            })
        
        return storage_data
    
    def generate_complete_dataset(self, hours_back=24):
        """Generate complete renewable energy dataset"""
        solar_data = self.generate_solar_data(hours_back)
        wind_data = self.generate_wind_data(hours_back)
        consumption_data = self.generate_consumption_data(hours_back)
        storage_data = self.generate_storage_data(solar_data, wind_data, consumption_data)
        
        # Combine all data
        complete_data = []
        for i in range(len(solar_data)):
            complete_data.append({
                'timestamp': solar_data[i]['timestamp'],
                'sun_intensity': solar_data[i]['sun_intensity'],
                'solar_power': solar_data[i]['solar_power'],
                'wind_speed': wind_data[i]['wind_speed'],
                'wind_power': wind_data[i]['wind_power'],
                'consumption': consumption_data[i]['consumption'],
                'storage_kwh': storage_data[i]['storage_kwh'],
                'storage_percentage': storage_data[i]['storage_percentage'],
                'grid_export': storage_data[i]['grid_export'],
                'grid_import': storage_data[i]['grid_import'],
                'net_power': storage_data[i]['net_power'],
                'total_generation': solar_data[i]['solar_power'] + wind_data[i]['wind_power']
            })
        
        return complete_data
    
    def get_daily_averages(self, data):
        """Calculate daily averages for analysis"""
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        daily_averages = df.groupby('date').agg({
            'solar_power': 'mean',
            'wind_power': 'mean',
            'total_generation': 'mean',
            'consumption': 'mean',
            'storage_percentage': 'mean',
            'sun_intensity': 'mean',
            'grid_export': 'sum',
            'grid_import': 'sum'
        }).reset_index()
        
        return daily_averages.to_dict('records')
    
    def detect_solar_faults(self, data):
        """Detect potential solar panel faults based on sun intensity vs power generation"""
        faults = []
        
        for record in data:
            sun_intensity = record['sun_intensity']
            solar_power = record['solar_power']
            
            if sun_intensity > 70:  # High sun intensity
                expected_power = (sun_intensity / 100) * 10000 * 0.75  # Expected with some losses
                
                if solar_power < expected_power * 0.6:  # Less than 60% of expected
                    faults.append({
                        'timestamp': record['timestamp'],
                        'fault_type': 'Low Solar Efficiency',
                        'sun_intensity': sun_intensity,
                        'actual_power': solar_power,
                        'expected_power': expected_power,
                        'efficiency_loss': round(((expected_power - solar_power) / expected_power) * 100, 2)
                    })
        
        return faults
    
    def analyze_energy_trading(self, data):
        """Analyze energy surplus/deficit for trading opportunities"""
        trading_opportunities = []
        
        for record in data:
            net_power = record['net_power']
            storage_percentage = record['storage_percentage']
            
            # Selling opportunity when surplus and battery is nearly full
            if net_power > 2000 and storage_percentage > 80:
                trading_opportunities.append({
                    'timestamp': record['timestamp'],
                    'opportunity_type': 'SELL',
                    'surplus_power': round(net_power, 2),
                    'recommended_sell': round(net_power * 0.8, 2),  # Sell 80% of surplus
                    'estimated_revenue': round(net_power * 0.8 * 0.15, 2)  # $0.15 per kWh
                })
            
            # Buying opportunity when deficit and battery is low
            elif net_power < -1000 and storage_percentage < 30:
                trading_opportunities.append({
                    'timestamp': record['timestamp'],
                    'opportunity_type': 'BUY',
                    'deficit_power': round(abs(net_power), 2),
                    'recommended_buy': round(abs(net_power) * 0.5, 2),
                    'estimated_cost': round(abs(net_power) * 0.5 * 0.12, 2)  # $0.12 per kWh
                })
        
        return trading_opportunities
    
    def generate_historical_point(self, timestamp):
        """Generate a single historical data point for a specific timestamp"""
        hour = timestamp.hour
        minute = timestamp.minute
        
        # Solar generation based on time of day
        if 5 <= hour <= 19:
            primary_angle = math.sin((hour - 5) * math.pi / 14)
            secondary_angle = math.sin(minute * math.pi / 30)
            sun_intensity = max(0, primary_angle * 95 + secondary_angle * 5)
            
            if 10 <= hour <= 15:
                sun_intensity = min(100, sun_intensity * random.uniform(1.1, 1.3))
        else:
            sun_intensity = random.uniform(0, 2)
        
        # Weather factor
        weather_factor = random.uniform(0.7, 1.0)
        sun_intensity = max(0, min(100, sun_intensity * weather_factor + random.uniform(-5, 5)))
        
        # Solar power
        max_solar_power = random.uniform(9500, 10500)
        solar_power = (sun_intensity / 100) * max_solar_power * self.solar_efficiency
        
        # Wind generation
        base_wind_speed = random.uniform(4, 12)
        wind_speed = max(0, base_wind_speed + random.uniform(-2, 2))
        
        if wind_speed < 3:
            wind_power = random.uniform(0, 50)
        elif wind_speed > 25:
            wind_power = random.uniform(0, 100)
        elif wind_speed > 14:
            wind_power = random.uniform(7500, 8200)
        else:
            wind_power = 8000 * ((wind_speed - 3) / 11) ** 2.8
        
        wind_power *= self.wind_efficiency
        
        # Consumption based on time of day
        if 6 <= hour <= 9 or 17 <= hour <= 22:
            consumption = random.uniform(4500, 7500)
        elif 23 <= hour or hour <= 5:
            consumption = random.uniform(1500, 2800)
        else:
            consumption = random.uniform(2800, 4500)
        
        # Storage and other calculations
        total_generation = solar_power + wind_power
        net_power = total_generation - consumption
        
        # Simple storage simulation
        storage_percentage = random.uniform(20, 90)
        storage_kwh = (storage_percentage / 100) * 50
        
        # Grid interaction
        grid_export = max(0, net_power / 1000) if net_power > 0 else 0
        grid_import = abs(min(0, net_power / 1000)) if net_power < 0 else 0
        
        return {
            'timestamp': timestamp,
            'solar_power': round(solar_power, 2),
            'wind_power': round(wind_power, 2),
            'total_generation': round(total_generation, 2),
            'consumption': round(consumption, 2),
            'net_power': round(net_power, 2),
            'storage_percentage': round(storage_percentage, 1),
            'storage_kwh': round(storage_kwh, 1),
            'sun_intensity': round(sun_intensity, 1),
            'wind_speed': round(wind_speed, 1),
            'grid_export': round(grid_export, 3),
            'grid_import': round(grid_import, 3)
        }

# Utility function to get current data
def get_current_data():
    """Get current renewable energy data"""
    generator = RenewableEnergyDataGenerator()
    return generator.generate_complete_dataset(hours_back=1)[-1]  # Last minute data

def get_historical_data(hours=24):
    """Get historical renewable energy data"""
    generator = RenewableEnergyDataGenerator()
    return generator.generate_complete_dataset(hours_back=hours)
