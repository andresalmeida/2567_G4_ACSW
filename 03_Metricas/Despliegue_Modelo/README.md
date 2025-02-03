# Despliegue_Modelo_Conjunta
Esta aplicación web permite predecir el salario basado en características personales y profesionales usando un modelo de machine learning. La aplicación se despliega usando Flask y tiene una interfaz web sencilla para ingresar los datos.

## Requisitos

1. **Python**: Asegúrate de tener Python 3.6 o superior instalado.
2. **Flask**: Framework web para Python.
3. **pandas**: Biblioteca para la manipulación de datos.
4. **numpy**: Biblioteca para cálculos numéricos.
5. **joblib**: Biblioteca para la serialización de objetos.

## Preparación de los archivos `joblib`

Primero, necesitas generar los archivos `joblib` desde Google Colab para que la aplicación pueda usarlos. Aquí está el procedimiento:

1. **Entrenamiento del Modelo**:
   - Abre un notebook en Google Colab.
   - Entrena tu modelo de machine learning y guarda el modelo, el escalador, los codificadores y el orden de las columnas usando `joblib`.

   ```python
   import joblib

   # Guardar el modelo
   joblib.dump(model, 'mejor_modelo.joblib')

   # Guardar el escalador
   joblib.dump(scaler, 'scaler.joblib')

   # Guardar los codificadores de etiquetas
   joblib.dump(label_encoders, 'label_encoders.joblib')

   # Guardar el orden de las columnas
   joblib.dump(column_order, 'column_order.joblib')
   
2. **Descargar los Archivos**:
  - Descarga los archivos generados (mejor_modelo.joblib, scaler.joblib, label_encoders.joblib, column_order.joblib) a tu máquina local.
    
## Instalación y Ejecución - Windows
  - Clonar el Repositorio:
```
git clone https://github.com/andresalmeida/Despliegue_Modelo.git
cd Despliegue_Modelo
```
   - Creamos un entorno virtual
```
python -m venv venv
```
   - Activamos el entorno virtual
```
venv\Scripts\activate
```
   - Instalamos los requerimientos
```
pip install -r requirements.txt
```

  - Asegúrate de que requirements.txt contiene:
```
Flask
pandas
numpy
joblib
scikit-learn
```
  - Ejecuta la aplicación Flask
```
python app.py
```
La aplicación se ejecutará en http://127.0.0.1:5001 por defecto. Puedes cambiar el puerto en el archivo app.py si es necesario.

  - Acceder a la Interfaz Web:
  Abre tu navegador web y navega a http://127.0.0.1:5001.
  Aquí encontrarás un formulario para ingresar datos y recibir la predicción del modelo.

## Estructura del Proyecto

Se debe ver así:

```arduino
tu_repositorio/
│
├── app.py
├── requirements.txt
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── templates/
    └── index.html
```

## Problemas Comúnes
  -jinja2.exceptions.TemplateNotFound: index.html:
  Asegúrate de que index.html está en el directorio templates y que el directorio templates está en el mismo directorio que app.py.

  -port 5000 is already in use:
  Cambia el puerto en app.run(debug=True, port=5001) a otro número de puerto si el puerto 5000 está ocupado.

Si tienes problemas adicionales, revisa los logs de error y verifica que todas las rutas y archivos estén correctamente configurados.
