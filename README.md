Berry Analyzer v2 cmd
=====================
Requisitos
-------------------------
Para hacer uso de estas funciones, se debe tener instalado Python 3 junto al administrador de paquetes `pip` (se recomienda instalar la distribución Python de Anaconda <https://www.anaconda.com/distribution/> ya que cuenta con muchos de los paquetes necesarios para hacer uso de estas funciones).

Instalar las siguientes librerías:

`pip install numpy opencv-python ar-markers`

Descargar este proyecto o clonar con `git`

Desde la carpeta principal del proyecto, inicie una linea de comandos y utilice el archivo `ba_v2_bash.py` para realizar los análisis. Esta es la forma básica para realizar un análisis:

`python ba_v2_bash.py -i "dir/to/image/files" -o "dir/for/output/data" -g organ_to_be_analyzed`