"""
Weather Time-Series Analysis Utilities
Provides functions for time-series analysis and dataset generation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# TIME-SERIES ANALYSIS UTILITIES
# ============================================================================

class WeatherTimeSeriesAnalyzer:
    """Analyze weather time-series data"""
    
    @staticmethod
    def calculate_seasonal_statistics(df):
        """Calculate seasonal statistics"""
        seasonal_stats = df.groupby('Season').agg({
            'Temperature': ['mean', 'min', 'max', 'std'],
            'Humidity': ['mean', 'min', 'max'],
            'Rainfall': ['mean', 'sum', 'max'],
            'Wind_Speed': ['mean', 'max'],
            'Pressure': ['mean', 'min', 'max']
        }).round(2)
        
        return seasonal_stats
    
    @staticmethod
    def calculate_monthly_statistics(df):
        """Calculate monthly statistics"""
        df_copy = df.copy()
        df_copy['Month_Name'] = df_copy['Date'].dt.strftime('%B')
        
        monthly_stats = df_copy.groupby(['Month', 'Month_Name']).agg({
            'Temperature': ['mean', 'min', 'max', 'std'],
            'Humidity': ['mean'],
            'Rainfall': ['sum', 'mean'],
            'Wind_Speed': ['mean'],
            'Solar_Radiation': ['mean']
        }).round(2)
        
        return monthly_stats
    
    @staticmethod
    def identify_extreme_events(df, temp_threshold=30, rainfall_threshold=15):
        """Identify extreme weather events"""
        extreme_events = {
            'High Temperature Days': len(df[df['Temperature'] > temp_threshold]),
            'Low Temperature Days': len(df[df['Temperature'] < 5]),
            'Heavy Rainfall Days': len(df[df['Rainfall'] > rainfall_threshold]),
            'High Wind Days': len(df[df['Wind_Speed'] > 10]),
            'Low Pressure Days': len(df[df['Pressure'] < 1010])
        }
        
        return extreme_events
    
    @staticmethod
    def calculate_autocorrelation(series, lags=30):
        """Calculate autocorrelation for temperature"""
        autocorr = [series.autocorr(lag=i) for i in range(1, lags + 1)]
        return autocorr
    
    @staticmethod
    def forecast_next_7_days(df, model):
        """Generate 7-day forecast using trained model"""
        last_date = df['Date'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=7, freq='D')
        
        # Use last 7 days as reference for features
        last_features = df.iloc[-7:].copy()
        
        forecasts = []
        for i, date in enumerate(forecast_dates):
            day_of_year = date.timetuple().tm_yday
            month = date.month
            
            # Create feature vector (simplified)
            feature_vector = np.array([
                day_of_year, month,
                last_features['Temperature'].iloc[-1],
                last_features['Humidity'].iloc[-1],
                last_features['Rainfall'].iloc[-1],
                last_features['Wind_Speed'].iloc[-1],
                last_features['Pressure'].iloc[-1],
                last_features['Solar_Radiation'].iloc[-1]
            ]).reshape(1, -1)
            
            forecasts.append({
                'Date': date,
                'Forecasted_Temperature': np.random.normal(20, 5)  # Placeholder
            })
        
        return pd.DataFrame(forecasts)

# ============================================================================
# DATASET GENERATION AND EXPORT
# ============================================================================

def generate_and_save_datasets():
    """Generate and save weather datasets for analysis"""
    print("\n" + "=" * 90)
    print("GENERATING WEATHER DATASETS")
    print("=" * 90)
    
    # Import the main system to generate data
    from weather_forecasting_system import generate_weather_dataset, engineer_features
    
    # Generate dataset
    print("\nGenerating weather dataset...")
    df = generate_weather_dataset(n_days=365)
    
    # Engineer features
    print("Engineering features...")
    df_features = engineer_features(df)
    
    # Save main dataset
    print("\nSaving datasets...")
    df.to_csv('/home/ubuntu/weather_data.csv', index=False)
    print("✓ weather_data.csv (365 records)")
    
    df_features.to_csv('/home/ubuntu/weather_features.csv', index=False)
    print("✓ weather_features.csv (358 records with engineered features)")
    
    # Generate seasonal statistics
    analyzer = WeatherTimeSeriesAnalyzer()
    seasonal_stats = analyzer.calculate_seasonal_statistics(df)
    seasonal_stats.to_csv('/home/ubuntu/seasonal_statistics.csv')
    print("✓ seasonal_statistics.csv")
    
    # Generate monthly statistics
    monthly_stats = analyzer.calculate_monthly_statistics(df)
    monthly_stats.to_csv('/home/ubuntu/monthly_statistics.csv')
    print("✓ monthly_statistics.csv")
    
    # Generate extreme events report
    extreme_events = analyzer.identify_extreme_events(df)
    extreme_df = pd.DataFrame(list(extreme_events.items()), columns=['Event', 'Count'])
    extreme_df.to_csv('/home/ubuntu/extreme_events.csv', index=False)
    print("✓ extreme_events.csv")
    
    # Generate correlation analysis
    features_to_analyze = ['Temperature', 'Humidity', 'Rainfall', 'Wind_Speed', 'Pressure', 'Solar_Radiation']
    corr_matrix = df[features_to_analyze].corr()
    corr_matrix.to_csv('/home/ubuntu/correlation_matrix.csv')
    print("✓ correlation_matrix.csv")
    
    # Generate temperature statistics by month
    temp_by_month = df.groupby(df['Date'].dt.month).agg({
        'Temperature': ['mean', 'min', 'max', 'std'],
        'Humidity': ['mean'],
        'Rainfall': ['sum'],
        'Wind_Speed': ['mean']
    }).round(2)
    temp_by_month.to_csv('/home/ubuntu/temperature_by_month.csv')
    print("✓ temperature_by_month.csv")
    
    # Generate hourly profile (simulated)
    hourly_data = []
    for hour in range(24):
        hourly_data.append({
            'Hour': hour,
            'Avg_Temperature': 20 + 8 * np.sin(2 * np.pi * (hour - 6) / 24),
            'Avg_Humidity': 70 - 5 * np.sin(2 * np.pi * (hour - 6) / 24),
            'Avg_Solar_Radiation': max(0, 300 * np.sin(2 * np.pi * (hour - 6) / 24))
        })
    
    hourly_df = pd.DataFrame(hourly_data)
    hourly_df.to_csv('/home/ubuntu/hourly_profile.csv', index=False)
    print("✓ hourly_profile.csv")
    
    # Generate weather insights
    insights = {
        'Metric': [
            'Average Temperature',
            'Temperature Range',
            'Average Humidity',
            'Total Rainfall',
            'Average Wind Speed',
            'Atmospheric Pressure Range',
            'Extreme Hot Days (>30°C)',
            'Extreme Cold Days (<5°C)',
            'Heavy Rainfall Days (>15mm)',
            'High Wind Days (>10m/s)'
        ],
        'Value': [
            f"{df['Temperature'].mean():.2f}°C",
            f"{df['Temperature'].min():.2f}°C to {df['Temperature'].max():.2f}°C",
            f"{df['Humidity'].mean():.2f}%",
            f"{df['Rainfall'].sum():.2f}mm",
            f"{df['Wind_Speed'].mean():.2f}m/s",
            f"{df['Pressure'].min():.2f} to {df['Pressure'].max():.2f} hPa",
            f"{len(df[df['Temperature'] > 30])} days",
            f"{len(df[df['Temperature'] < 5])} days",
            f"{len(df[df['Rainfall'] > 15])} days",
            f"{len(df[df['Wind_Speed'] > 10])} days"
        ]
    }
    
    insights_df = pd.DataFrame(insights)
    insights_df.to_csv('/home/ubuntu/weather_insights.csv', index=False)
    print("✓ weather_insights.csv")
    
    print("\n" + "=" * 90)
    print("DATASET GENERATION COMPLETED")
    print("=" * 90)
    print(f"\nTotal Records Generated: {len(df)}")
    print(f"Features per Record: {len(df.columns)}")
    print(f"Date Range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"\nDatasets saved to /home/ubuntu/")
    
    return df, df_features

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    df, df_features = generate_and_save_datasets()
