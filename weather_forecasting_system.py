"""
Weather Forecasting System for Predicting Daily Temperature
Predicts daily temperature using historical climate data and machine learning
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC WEATHER DATASET
# ============================================================================

def generate_weather_dataset(n_days=365, random_state=42):
    """Generate synthetic weather dataset with realistic climate patterns"""
    np.random.seed(random_state)
    
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='D')
    day_of_year = np.arange(1, n_days + 1)
    
    # Generate seasonal temperature pattern
    base_temp = 20 + 15 * np.sin(2 * np.pi * day_of_year / 365)
    temp_noise = np.random.normal(0, 2, n_days)
    temperature = base_temp + temp_noise
    
    # Generate humidity (inversely correlated with temperature)
    humidity = 70 - 0.5 * (temperature - 20) + np.random.normal(0, 5, n_days)
    humidity = np.clip(humidity, 20, 100)
    
    # Generate rainfall (seasonal pattern)
    rainfall = 5 + 10 * np.sin(2 * np.pi * day_of_year / 365) + np.random.exponential(2, n_days)
    rainfall = np.clip(rainfall, 0, 50)
    
    # Generate wind speed (random with seasonal variation)
    wind_speed = 5 + 3 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 1, n_days)
    wind_speed = np.clip(wind_speed, 0, 20)
    
    # Generate atmospheric pressure (inversely correlated with rainfall)
    pressure = 1013 - 0.3 * rainfall + np.random.normal(0, 1, n_days)
    
    # Generate solar radiation (seasonal pattern)
    solar_radiation = 200 + 150 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 20, n_days)
    solar_radiation = np.clip(solar_radiation, 50, 400)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Day_of_Year': day_of_year,
        'Month': dates.month,
        'Season': pd.cut(dates.month, bins=[0, 3, 6, 9, 12], labels=['Winter', 'Spring', 'Summer', 'Fall']),
        'Temperature': temperature,
        'Humidity': humidity,
        'Rainfall': rainfall,
        'Wind_Speed': wind_speed,
        'Pressure': pressure,
        'Solar_Radiation': solar_radiation
    })
    
    print("=" * 90)
    print("WEATHER FORECASTING SYSTEM - DATASET OVERVIEW")
    print("=" * 90)
    print(f"\nTotal Days: {len(df)}")
    print(f"\nTemperature Statistics:")
    print(f"  Mean: {df['Temperature'].mean():.2f}°C")
    print(f"  Min: {df['Temperature'].min():.2f}°C")
    print(f"  Max: {df['Temperature'].max():.2f}°C")
    print(f"  Std Dev: {df['Temperature'].std():.2f}°C")
    print(f"\nHumidity Statistics:")
    print(f"  Mean: {df['Humidity'].mean():.2f}%")
    print(f"  Range: {df['Humidity'].min():.2f}% - {df['Humidity'].max():.2f}%")
    print(f"\nRainfall Statistics:")
    print(f"  Mean: {df['Rainfall'].mean():.2f}mm")
    print(f"  Max: {df['Rainfall'].max():.2f}mm")
    print(f"\nWind Speed Statistics:")
    print(f"  Mean: {df['Wind_Speed'].mean():.2f}m/s")
    print(f"  Max: {df['Wind_Speed'].max():.2f}m/s")
    
    return df

# ============================================================================
# 2. FEATURE ENGINEERING
# ============================================================================

def engineer_features(df):
    """Create advanced features from raw weather data"""
    print("\n" + "=" * 90)
    print("FEATURE ENGINEERING")
    print("=" * 90)
    
    df_features = df.copy()
    
    # Lagged features (previous day values)
    df_features['Temp_Lag1'] = df_features['Temperature'].shift(1)
    df_features['Temp_Lag7'] = df_features['Temperature'].shift(7)
    df_features['Humidity_Lag1'] = df_features['Humidity'].shift(1)
    df_features['Rainfall_Lag1'] = df_features['Rainfall'].shift(1)
    
    # Rolling averages
    df_features['Temp_MA7'] = df_features['Temperature'].rolling(window=7, min_periods=1).mean()
    df_features['Humidity_MA7'] = df_features['Humidity'].rolling(window=7, min_periods=1).mean()
    df_features['Wind_MA7'] = df_features['Wind_Speed'].rolling(window=7, min_periods=1).mean()
    
    # Seasonal indicators
    df_features['Is_Winter'] = (df_features['Month'].isin([12, 1, 2])).astype(int)
    df_features['Is_Spring'] = (df_features['Month'].isin([3, 4, 5])).astype(int)
    df_features['Is_Summer'] = (df_features['Month'].isin([6, 7, 8])).astype(int)
    df_features['Is_Fall'] = (df_features['Month'].isin([9, 10, 11])).astype(int)
    
    # Drop rows with NaN values from lagged features
    df_features = df_features.dropna()
    
    print(f"\nOriginal features: {len(df.columns)}")
    print(f"Engineered features: {len(df_features.columns)}")
    print(f"Total samples after feature engineering: {len(df_features)}")
    
    return df_features

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def visualize_weather_patterns(df):
    """Visualize weather patterns and seasonal trends"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Temperature over time
    axes[0, 0].plot(df['Date'], df['Temperature'], linewidth=1.5, color='#D62828', alpha=0.7)
    axes[0, 0].fill_between(df['Date'], df['Temperature'], alpha=0.3, color='#D62828')
    axes[0, 0].set_title('Daily Temperature Over Time', fontweight='bold', fontsize=12)
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Temperature (°C)')
    axes[0, 0].grid(alpha=0.3)
    
    # Humidity and Rainfall
    ax1 = axes[0, 1]
    ax2 = ax1.twinx()
    
    line1 = ax1.plot(df['Date'], df['Humidity'], color='#2E86AB', linewidth=1.5, label='Humidity')
    line2 = ax2.bar(df['Date'], df['Rainfall'], alpha=0.3, color='#A23B72', label='Rainfall')
    
    ax1.set_title('Humidity and Rainfall Patterns', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Humidity (%)', color='#2E86AB')
    ax2.set_ylabel('Rainfall (mm)', color='#A23B72')
    ax1.tick_params(axis='y', labelcolor='#2E86AB')
    ax2.tick_params(axis='y', labelcolor='#A23B72')
    ax1.grid(alpha=0.3)
    
    # Wind Speed and Pressure
    ax3 = axes[1, 0]
    ax4 = ax3.twinx()
    
    ax3.plot(df['Date'], df['Wind_Speed'], color='#F18F01', linewidth=1.5, label='Wind Speed')
    ax4.plot(df['Date'], df['Pressure'], color='#C73E1D', linewidth=1.5, label='Pressure')
    
    ax3.set_title('Wind Speed and Atmospheric Pressure', fontweight='bold', fontsize=12)
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Wind Speed (m/s)', color='#F18F01')
    ax4.set_ylabel('Pressure (hPa)', color='#C73E1D')
    ax3.tick_params(axis='y', labelcolor='#F18F01')
    ax4.tick_params(axis='y', labelcolor='#C73E1D')
    ax3.grid(alpha=0.3)
    
    # Temperature by season
    seasons_order = ['Winter', 'Spring', 'Summer', 'Fall']
    season_data = [df[df['Season'] == season]['Temperature'].values for season in seasons_order]
    
    bp = axes[1, 1].boxplot(season_data, labels=seasons_order, patch_artist=True)
    colors = ['#4A90E2', '#7ED321', '#F5A623', '#F8E71C']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    axes[1, 1].set_title('Temperature Distribution by Season', fontweight='bold', fontsize=12)
    axes[1, 1].set_ylabel('Temperature (°C)')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/weather_patterns.png', dpi=300, bbox_inches='tight')
    print("✓ Weather patterns visualization saved")
    plt.close()

def visualize_correlations(df):
    """Visualize feature correlations"""
    features_to_plot = ['Temperature', 'Humidity', 'Rainfall', 'Wind_Speed', 'Pressure', 'Solar_Radiation']
    corr_matrix = df[features_to_plot].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title('Feature Correlation Matrix', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_correlations.png', dpi=300, bbox_inches='tight')
    print("✓ Feature correlations visualization saved")
    plt.close()

def visualize_model_comparison(results):
    """Visualize model performance comparison"""
    models = list(results.keys())
    mae = [results[m]['MAE'] for m in models]
    rmse = [results[m]['RMSE'] for m in models]
    r2 = [results[m]['R2'] for m in models]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # MAE comparison
    axes[0].bar(models, mae, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8, edgecolor='black')
    axes[0].set_title('Mean Absolute Error (MAE)', fontweight='bold', fontsize=12)
    axes[0].set_ylabel('MAE (°C)')
    axes[0].grid(axis='y', alpha=0.3)
    
    # RMSE comparison
    axes[1].bar(models, rmse, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8, edgecolor='black')
    axes[1].set_title('Root Mean Squared Error (RMSE)', fontweight='bold', fontsize=12)
    axes[1].set_ylabel('RMSE (°C)')
    axes[1].grid(axis='y', alpha=0.3)
    
    # R² comparison
    axes[2].bar(models, r2, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8, edgecolor='black')
    axes[2].set_title('R² Score', fontweight='bold', fontsize=12)
    axes[2].set_ylabel('R² Score')
    axes[2].set_ylim([0, 1])
    axes[2].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Model comparison visualization saved")
    plt.close()

def visualize_predictions(y_test, y_pred_lr, y_pred_rf, y_pred_gb):
    """Visualize actual vs predicted temperatures"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    models_data = [
        ('Linear Regression', y_pred_lr),
        ('Random Forest', y_pred_rf),
        ('Gradient Boosting', y_pred_gb)
    ]
    
    for idx, (name, y_pred) in enumerate(models_data):
        axes[idx].scatter(y_test, y_pred, alpha=0.6, s=30, color='#2E86AB', edgecolor='black')
        
        # Perfect prediction line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        axes[idx].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        axes[idx].set_title(f'{name}', fontweight='bold', fontsize=12)
        axes[idx].set_xlabel('Actual Temperature (°C)')
        axes[idx].set_ylabel('Predicted Temperature (°C)')
        axes[idx].legend()
        axes[idx].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/predictions_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Predictions comparison visualization saved")
    plt.close()

def visualize_residuals(y_test, y_pred_lr, y_pred_rf, y_pred_gb):
    """Visualize prediction residuals"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    models_data = [
        ('Linear Regression', y_pred_lr),
        ('Random Forest', y_pred_rf),
        ('Gradient Boosting', y_pred_gb)
    ]
    
    for idx, (name, y_pred) in enumerate(models_data):
        residuals = y_test - y_pred
        
        axes[idx].scatter(y_pred, residuals, alpha=0.6, s=30, color='#A23B72', edgecolor='black')
        axes[idx].axhline(y=0, color='r', linestyle='--', linewidth=2)
        
        axes[idx].set_title(f'{name} - Residuals', fontweight='bold', fontsize=12)
        axes[idx].set_xlabel('Predicted Temperature (°C)')
        axes[idx].set_ylabel('Residuals (°C)')
        axes[idx].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/residuals_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Residuals analysis visualization saved")
    plt.close()

# ============================================================================
# 4. MODEL BUILDING AND TRAINING
# ============================================================================

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple regression models"""
    print("\n" + "=" * 90)
    print("MODEL TRAINING")
    print("=" * 90)
    
    results = {}
    models = {}
    predictions = {}
    
    # Linear Regression
    print("\nTraining Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    
    results['Linear Regression'] = {
        'MAE': mean_absolute_error(y_test, y_pred_lr),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_lr)),
        'R2': r2_score(y_test, y_pred_lr)
    }
    models['Linear Regression'] = lr_model
    predictions['Linear Regression'] = y_pred_lr
    
    # Random Forest
    print("Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    
    results['Random Forest'] = {
        'MAE': mean_absolute_error(y_test, y_pred_rf),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'R2': r2_score(y_test, y_pred_rf)
    }
    models['Random Forest'] = rf_model
    predictions['Random Forest'] = y_pred_rf
    
    # Gradient Boosting
    print("Training Gradient Boosting Regressor...")
    gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    
    results['Gradient Boosting'] = {
        'MAE': mean_absolute_error(y_test, y_pred_gb),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'R2': r2_score(y_test, y_pred_gb)
    }
    models['Gradient Boosting'] = gb_model
    predictions['Gradient Boosting'] = y_pred_gb
    
    return results, models, predictions, y_pred_lr, y_pred_rf, y_pred_gb

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 90)
    print("WEATHER FORECASTING SYSTEM FOR PREDICTING DAILY TEMPERATURE")
    print("=" * 90)
    
    # Generate dataset
    print("\n[Step 1] Generating Weather Dataset...")
    df = generate_weather_dataset(n_days=365)
    
    # Engineer features
    print("\n[Step 2] Engineering Features...")
    df_features = engineer_features(df)
    
    # Prepare data for modeling
    print("\n[Step 3] Preparing Data for Modeling...")
    feature_cols = [col for col in df_features.columns if col not in ['Date', 'Temperature', 'Season']]
    X = df_features[feature_cols].values
    y = df_features['Temperature'].values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    print("\n[Step 4] Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    print(f"Training set size: {len(X_train)} days")
    print(f"Test set size: {len(X_test)} days")
    
    # Generate visualizations
    print("\n[Step 5] Generating Visualizations...")
    print("Creating weather patterns visualization...")
    visualize_weather_patterns(df)
    
    print("Creating feature correlations...")
    visualize_correlations(df)
    
    # Train models
    print("\n[Step 6] Training Regression Models...")
    results, models, predictions, y_pred_lr, y_pred_rf, y_pred_gb = train_models(
        X_train, X_test, y_train, y_test
    )
    
    # Print results
    print("\n" + "=" * 90)
    print("MODEL PERFORMANCE RESULTS")
    print("=" * 90)
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    # Generate additional visualizations
    print("\n[Step 7] Generating Additional Visualizations...")
    print("Creating model comparison...")
    visualize_model_comparison(results)
    
    print("Creating predictions comparison...")
    visualize_predictions(y_test, y_pred_lr, y_pred_rf, y_pred_gb)
    
    print("Creating residuals analysis...")
    visualize_residuals(y_test, y_pred_lr, y_pred_rf, y_pred_gb)
    
    print("\n" + "=" * 90)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 90)
    print("\nGenerated Visualizations:")
    print("  1. weather_patterns.png")
    print("  2. feature_correlations.png")
    print("  3. model_comparison.png")
    print("  4. predictions_comparison.png")
    print("  5. residuals_analysis.png")
    
    return df, df_features, X_train, X_test, y_train, y_test, results, models

if __name__ == "__main__":
    df, df_features, X_train, X_test, y_train, y_test, results, models = main()
