import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
import os

class SolarPowerPredictor(nn.Module):
    """Neural network model for predicting solar power generation"""
    
    def __init__(self, input_size=5):
        super(SolarPowerPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class WindPowerPredictor(nn.Module):
    """Neural network model for predicting wind power generation"""
    
    def __init__(self, input_size=4):
        super(WindPowerPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, 48)
        self.fc2 = nn.Linear(48, 24)
        self.fc3 = nn.Linear(24, 12)
        self.fc4 = nn.Linear(12, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.15)
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class FaultDetectionModel(nn.Module):
    """Neural network model for detecting equipment faults"""
    
    def __init__(self, input_size=8):
        super(FaultDetectionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))
        return x

class EnergyConsumptionPredictor(nn.Module):
    """Neural network model for predicting energy consumption"""
    
    def __init__(self, input_size=6):
        super(EnergyConsumptionPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, 56)
        self.fc2 = nn.Linear(56, 28)
        self.fc3 = nn.Linear(28, 14)
        self.fc4 = nn.Linear(14, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.25)
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class RenewableEnergyMLManager:
    """Manager class for all machine learning models and operations"""
    
    def __init__(self, model_dir='ml_models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.solar_predictor = SolarPowerPredictor()
        self.wind_predictor = WindPowerPredictor()
        self.fault_detector = FaultDetectionModel()
        self.consumption_predictor = EnergyConsumptionPredictor()
        
        # Initialize scalers
        self.solar_scaler = StandardScaler()
        self.wind_scaler = StandardScaler()
        self.fault_scaler = StandardScaler()
        self.consumption_scaler = StandardScaler()
        
        self.load_models()
    
    def prepare_solar_features(self, data):
        """Prepare features for solar power prediction"""
        df = pd.DataFrame(data)
        
        # Extract time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        df['month'] = df['timestamp'].dt.month
        
        # Select features
        features = ['sun_intensity', 'hour', 'day_of_year', 'month', 'storage_percentage']
        
        return df[features].values
    
    def prepare_wind_features(self, data):
        """Prepare features for wind power prediction"""
        df = pd.DataFrame(data)
        
        # Extract time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['season'] = (df['timestamp'].dt.month % 12 + 3) // 3
        
        # Select features (wind_speed would come from weather data)
        features = ['wind_speed', 'hour', 'season', 'storage_percentage']
        
        return df[features].values
    
    def prepare_fault_features(self, data):
        """Prepare features for fault detection"""
        df = pd.DataFrame(data)
        
        # Calculate efficiency ratios and anomalies
        df['solar_efficiency'] = df['solar_power'] / (df['sun_intensity'] + 1e-8)
        df['wind_efficiency'] = df['wind_power'] / (df['wind_speed'] + 1e-8)
        df['generation_ratio'] = df['total_generation'] / (df['consumption'] + 1e-8)
        df['power_variance'] = df['total_generation'].rolling(window=10, min_periods=1).std().fillna(0)
        
        features = ['sun_intensity', 'solar_power', 'wind_speed', 'wind_power', 
                   'solar_efficiency', 'wind_efficiency', 'generation_ratio', 'power_variance']
        
        return df[features].values
    
    def prepare_consumption_features(self, data):
        """Prepare features for consumption prediction"""
        df = pd.DataFrame(data)
        
        # Extract time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Rolling averages
        df['consumption_ma'] = df['consumption'].rolling(window=60, min_periods=1).mean()
        df['generation_ma'] = df['total_generation'].rolling(window=60, min_periods=1).mean()
        
        features = ['hour', 'day_of_week', 'is_weekend', 'consumption_ma', 
                   'generation_ma', 'storage_percentage']
        
        return df[features].values
    
    def train_solar_predictor(self, data, epochs=100):
        """Train the solar power prediction model"""
        X = self.prepare_solar_features(data)
        y = np.array([d['solar_power'] for d in data]).reshape(-1, 1)
        
        # Scale features
        X_scaled = self.solar_scaler.fit_transform(X)
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.FloatTensor(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_tensor, y_tensor, test_size=0.2, random_state=42
        )
        
        # Training
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.solar_predictor.parameters(), lr=0.001)
        
        self.solar_predictor.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.solar_predictor(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 20 == 0:
                print(f'Solar Predictor - Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
        
        # Evaluate
        self.solar_predictor.eval()
        with torch.no_grad():
            test_outputs = self.solar_predictor(X_test)
            test_loss = criterion(test_outputs, y_test)
            print(f'Solar Predictor Test Loss: {test_loss.item():.4f}')
        
        self.save_model('solar_predictor', self.solar_predictor, self.solar_scaler)
    
    def train_fault_detector(self, data, epochs=150):
        """Train the fault detection model"""
        X = self.prepare_fault_features(data)
        
        # Create fault labels (simplified - based on efficiency drops)
        df = pd.DataFrame(data)
        df['solar_efficiency'] = df['solar_power'] / (df['sun_intensity'] + 1e-8)
        df['wind_efficiency'] = df['wind_power'] / (df['wind_speed'] + 1e-8)
        
        # Label as fault if efficiency is below threshold
        solar_threshold = df['solar_efficiency'].quantile(0.3)
        wind_threshold = df['wind_efficiency'].quantile(0.3)
        
        y = ((df['solar_efficiency'] < solar_threshold) | 
             (df['wind_efficiency'] < wind_threshold)).astype(int).values.reshape(-1, 1)
        
        # Scale features
        X_scaled = self.fault_scaler.fit_transform(X)
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.FloatTensor(y)
        
        # Training
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.fault_detector.parameters(), lr=0.001)
        
        self.fault_detector.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.fault_detector(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 30 == 0:
                print(f'Fault Detector - Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
        
        self.save_model('fault_detector', self.fault_detector, self.fault_scaler)
    
    def predict_solar_power(self, current_data):
        """Predict solar power generation"""
        self.solar_predictor.eval()
        
        X = self.prepare_solar_features([current_data])
        X_scaled = self.solar_scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled)
        
        with torch.no_grad():
            prediction = self.solar_predictor(X_tensor)
            return prediction.item()
    
    def predict_fault_probability(self, current_data):
        """Predict probability of equipment fault"""
        self.fault_detector.eval()
        
        X = self.prepare_fault_features([current_data])
        X_scaled = self.fault_scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled)
        
        with torch.no_grad():
            probability = self.fault_detector(X_tensor)
            return probability.item()
    
    def analyze_performance_efficiency(self, data):
        """Analyze system performance and efficiency"""
        df = pd.DataFrame(data)
        
        # Calculate various efficiency metrics
        df['solar_efficiency'] = df['solar_power'] / (df['sun_intensity'] * 100 + 1e-8)
        df['wind_efficiency'] = df['wind_power'] / (df['wind_speed'] ** 3 + 1e-8)
        df['overall_efficiency'] = df['total_generation'] / (df['consumption'] + 1e-8)
        
        # Convert timestamps to strings for JSON serialization
        peak_gen_timestamp = df.loc[df['total_generation'].idxmax(), 'timestamp']
        peak_cons_timestamp = df.loc[df['consumption'].idxmax(), 'timestamp']
        
        analysis = {
            'avg_solar_efficiency': float(df['solar_efficiency'].mean()),
            'avg_wind_efficiency': float(df['wind_efficiency'].mean()),
            'avg_overall_efficiency': float(df['overall_efficiency'].mean()),
            'efficiency_trend': float(df['overall_efficiency'].diff().mean()),
            'peak_generation_hour': peak_gen_timestamp.isoformat() if hasattr(peak_gen_timestamp, 'isoformat') else str(peak_gen_timestamp),
            'peak_consumption_hour': peak_cons_timestamp.isoformat() if hasattr(peak_cons_timestamp, 'isoformat') else str(peak_cons_timestamp),
            'energy_independence_score': float(min(1.0, df['total_generation'].sum() / df['consumption'].sum()))
        }
        
        return analysis
    
    def predict_optimal_trading_times(self, data):
        """Predict optimal times for energy trading"""
        df = pd.DataFrame(data)
        
        # Calculate surplus/deficit patterns
        df['net_energy'] = df['total_generation'] - df['consumption']
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        
        # Find patterns in surplus/deficit by hour
        hourly_patterns = df.groupby('hour').agg({
            'net_energy': ['mean', 'std'],
            'storage_percentage': 'mean',
            'grid_export': 'sum',
            'grid_import': 'sum'
        }).reset_index()
        
        # Identify best selling hours (high surplus, high storage)
        hourly_patterns['sell_score'] = (
            hourly_patterns['net_energy']['mean'] * 
            hourly_patterns['storage_percentage']['mean'] / 100
        )
        
        # Identify best buying hours (low generation, low storage)
        hourly_patterns['buy_score'] = (
            -hourly_patterns['net_energy']['mean'] * 
            (100 - hourly_patterns['storage_percentage']['mean']) / 100
        )
        
        best_sell_hours = hourly_patterns.nlargest(3, 'sell_score')['hour'].tolist()
        best_buy_hours = hourly_patterns.nlargest(3, 'buy_score')['hour'].tolist()
        
        return {
            'best_sell_hours': best_sell_hours,
            'best_buy_hours': best_buy_hours,
            'hourly_patterns': [
                {
                    'hour': int(row['hour']),
                    'avg_net_energy': float(row[('net_energy', 'mean')]),
                    'net_energy_std': float(row[('net_energy', 'std')]),
                    'avg_storage': float(row[('storage_percentage', 'mean')]),
                    'total_grid_export': float(row[('grid_export', 'sum')]),
                    'total_grid_import': float(row[('grid_import', 'sum')]),
                    'sell_score': float(row['sell_score']),
                    'buy_score': float(row['buy_score'])
                }
                for _, row in hourly_patterns.iterrows()
            ]
        }
    
    def save_model(self, name, model, scaler):
        """Save model and scaler to disk"""
        model_path = os.path.join(self.model_dir, f'{name}.pth')
        scaler_path = os.path.join(self.model_dir, f'{name}_scaler.pkl')
        
        torch.save(model.state_dict(), model_path)
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
    
    def load_models(self):
        """Load saved models from disk"""
        models = {
            'solar_predictor': self.solar_predictor,
            'wind_predictor': self.wind_predictor,
            'fault_detector': self.fault_detector,
            'consumption_predictor': self.consumption_predictor
        }
        
        scalers = {
            'solar_predictor': self.solar_scaler,
            'wind_predictor': self.wind_scaler,
            'fault_detector': self.fault_scaler,
            'consumption_predictor': self.consumption_scaler
        }
        
        for name, model in models.items():
            model_path = os.path.join(self.model_dir, f'{name}.pth')
            scaler_path = os.path.join(self.model_dir, f'{name}_scaler.pkl')
            
            if os.path.exists(model_path):
                model.load_state_dict(torch.load(model_path))
                print(f'Loaded {name} model')
            
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    scalers[name] = pickle.load(f)
                print(f'Loaded {name} scaler')

# Global ML manager instance
ml_manager = RenewableEnergyMLManager()
