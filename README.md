
# Instrucciones de Instalación

Este proyecto proporciona instrucciones para instalar y ejecutar validaciones de documentos dentro del proyecto crossborder.

## Requisitos Previos

- Python (versión 3.11)
- Git

## Instalación

1. Clona el repositorio desde GitHub:

   ```
   git clone git@github.com:OLVA-TI/document-crossborder
   ```

2. Accede al directorio del proyecto:

   ```
   cd document-crossborder
   ```

3. Crea un entorno virtual para el proyecto (obligatorio):

   ```
   python -m venv venv
   ```

4. Activa el entorno virtual:

   - En Linux/macOS:

     ```
     source venv/bin/activate
     ```

   - En Windows (PowerShell):

     ```
     .\venv\Scripts\Activate
     ```

5. Instala las dependencias del proyecto:

   ```
   pip install -r requirements.txt
   ```

7. Crear un archivo .env y llenar sus variables:

   ```
   cp .env.example .env

   ```
8. Ejecuta el proceso de validaciones:

   ```
   python3 main.py 
   ```

## Contribución

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un fork del proyecto desde GitHub.
2. Clona tu fork a tu máquina local.
3. Crea una nueva rama para tu función o corrección de errores: `git checkout -b nombre-de-la-rama`.
4. Haz tus cambios y realiza los commits: `git commit -m "Descripción de los cambios"`.
5. Sube la rama a tu fork en GitHub: `git push origin nombre-de-la-rama`.
6. Crea un Pull Request en el repositorio original.

## Soporte

Si tienes algún problema o pregunta sobre el proyecto, no dudes en [abrir un issue](https://github.com/OLVA-TI/document-crossborder/issues) en GitHub.