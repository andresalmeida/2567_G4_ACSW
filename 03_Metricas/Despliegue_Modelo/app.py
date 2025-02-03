from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# Cargar el modelo, scaler, encoders y el orden de las columnas
best_model = joblib.load('mejor_modelo.joblib')
scaler = joblib.load('scaler.joblib')
encoders = joblib.load('label_encoders.joblib')
column_order = joblib.load('column_order.joblib')

# Definir las columnas categóricas
categorical_columns = ['ClaseObrera', 'Educacion', 'EstadoMarital', 'Ocupacion', 'EstadoCivil', 'Raza', 'Sexo', 'Pais']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # Crear un DataFrame a partir de los datos recibidos
    data_df = pd.DataFrame([data])
    
    # Aplicar Label Encoding a las columnas categóricas
    for col in categorical_columns:
        if col in data_df.columns:
            if col not in encoders:
                return jsonify({'error': f"No encoder found for column {col}. Skipping encoding for this column."}), 400
            encoder = encoders[col]
            # Manejar valores desconocidos
            data_df[col] = data_df[col].apply(lambda x: x if x in encoder.classes_ else 'Unknown')
            if 'Unknown' not in encoder.classes_:
                encoder.classes_ = np.append(encoder.classes_, 'Unknown')
            data_df[col] = encoder.transform(data_df[col])
    
    # Asegurarse de que las columnas están en el mismo orden que durante el entrenamiento
    missing_cols = set(column_order) - set(data_df.columns)
    for col in missing_cols:
        data_df[col] = 0  # o cualquier otro valor por defecto
    data_df = data_df.reindex(columns=column_order)
    
    # Convertir las columnas a float64 y llenar NaNs con 0
    data_df = data_df.astype(float).fillna(0)
    
    # Escalar los datos
    scaled_features = scaler.transform(data_df)
    
    # Hacer la predicción
    prediction = best_model.predict(scaled_features)
    
    # Verificar si el modelo tiene el método predict_proba
    if hasattr(best_model, 'predict_proba'):
        probability = best_model.predict_proba(scaled_features)[:, 1]
    else:
        probability = None  # Para modelos que no proporcionan probabilidades
    
    return jsonify({
        'prediction': int(prediction[0]),
        'probability': float(probability[0]) if probability is not None else None
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
