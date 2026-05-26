# Simulador de Órbitas 3D desde TLE

Este proyecto contiene un notebook de Jupyter que permite simular órbitas 3D de satélites a partir de sus TLE (Two-Line Element).

## Requisitos

- Python 3.14
- Bibliotecas: skyfield, matplotlib, requests, numpy, plotly

## Uso

1. Abre el notebook `orbit_simulator.ipynb` en VS Code o Jupyter.
2. Ejecuta las celdas en orden.
3. En la celda 3, cambia `norad_id` por el ID NORAD del satélite deseado (ej. '25544' para ISS).
4. Ejecuta el resto de celdas para descargar el TLE, propagar la órbita y visualizarla en 3D.

## Propagador

Utiliza el modelo SGP4 a través de la biblioteca Skyfield para propagar las órbitas.

## Visualización

Muestra la órbita del satélite en coordenadas geocéntricas con la Tierra representada de manera realista usando colores que simulan océanos y continentes (escala 'Earth' de Plotly). La visualización es interactiva con Plotly.