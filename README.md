This program:

    Data Collection: Fetches historical transaction fee data from Blockchain.com API
    Feature Engineering: Creates time-based features and rolling averages
    Machine Learning: Uses Random Forest regression to predict fees
    Visualization: Plots historical fee data
    Prediction: Estimates fees for specific times and categorizes them as Low/Medium/High

## Key features:

    Uses multiple time-based features (hour, day of week, etc.)
    Includes 24-hour rolling average for context
    Categorizes predictions based on historical percentiles
    Provides visual representation of fee patterns
    Calculates model accuracy using MAE

## To use:

    Install required packages: pip install pandas numpy scikit-learn matplotlib requests
    Run the script
    The program will:

        Download 60 days of historical data

        Train a prediction model

        Show a fee history chart

        Predict fees for 6 hours in the future
