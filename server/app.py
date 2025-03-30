from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
import pandas as pd
import os

app = Flask(__name__, static_folder='static')
CORS(app, resources={ r"/*": { "methods": ["GET"] }})

df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'res.csv'))

def get_bool(val):
    return str(val).lower() == 'true'

# Serve React App at root
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

# Serve all other static files
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/get_rmse_data', methods=['GET'])
def get_rmse_data():
    # Get request parameters 
    gender_param = request.args.get('gender')
    age_param = request.args.get('age')
    occupation_param = request.args.get('occupation')

    if None in [gender_param, age_param, occupation_param]:
        return jsonify({"error": "Missing one or more parameters: gender, age, occupation"}), 400

    # Get boolean values
    try:
        gender = get_bool(gender_param)
        age = get_bool(age_param)
        occupation = get_bool(occupation_param)
    except Exception as e:
        return jsonify({"error": f"Invalid parameter value: {str(e)}"}), 400

    # Filter the dataframe based on the selected boolean features
    filtered_df = df[
        (df['Gender'] == gender) &
        (df['Age'] == age) &
        (df['Occupation'] == occupation)
    ]

    if filtered_df.empty:
        return jsonify({"error": "No matching records found"}), 404

    # Sort by subsample_fraction and transform response to dictionary format for JSON serialization 
    filtered_df = filtered_df.sort_values('subsample_fraction')
    data = filtered_df[['subsample_fraction', 'RMSE']].to_dict('records')
    
    # Return the requested feature data as well as a unique sorted list of subset sizes
    response = {
        "data": data,
        "subset_sizes": sorted(filtered_df['subsample_fraction'].unique().tolist())
    }

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)