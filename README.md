# Salida - Presupuesto

App en Streamlit para armar el presupuesto de la salida y repartirlo entre dos personas.

Los precios salen de `Presupuesto.xlsx`, que es la fuente de verdad.

## Correr en local

    pip install -r requirements.txt
    streamlit run app.py

En Windows tambien sirve hacer doble clic en `run.bat`.

## Que se puede escoger

- Hospedaje: barra de $0 a $350.000
- Almuerzo: 1 entre 4 opciones
- Cenas: 2 (se puede repetir la misma)
- Lavada de carro: opcional
- Division del gasto entre Juan Fernando y Gabriela con una barra de porcentaje

Los desayunos son fijos y no se escogen.

## Nota sobre los links de Airbnb

Los links viven en `hospedajes.json`. En la app desplegada, lo que se edite desde la
pestana Airbnb se pierde cuando la app se reinicia: para que queden fijos hay que
guardarlos en ese archivo y hacer commit.
