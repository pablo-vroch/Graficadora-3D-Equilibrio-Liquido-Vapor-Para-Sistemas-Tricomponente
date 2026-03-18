# Graficadora-3D-Equilibrio-Liquido-Vapor-Para-Sistemas-Tricomponente
Este proyecto consiste en un archivo .exe (ejecutable de windows) que te permite visualizar el equilibrio liquido-vapor de una mezcla de tres compuestos químicos como una superficie 3D. En la figura 1 se ve un ejemplo de una grafica generada por este programa.

![Superficie 3D representando el equilibrio liquido-vapor para una mezcla de benceno, ethanol y hexano](/imagenes/fig1.png)

## Detalles del modelo termodinámico 

## ¿Como usar el programa?
Es importante considerar que el programa unicamente funciona en sistema operativo Windows ;(
- Ingresar al siguiente vinculo https://github.com/pablo-vroch/Graficadora-3D-Equilibrio-Liquido-Vapor-Para-Sistemas-Tricomponente/releases/tag/v1.0
- Descargar el archivo "Proyecto.Equilibrio.Fisico.Pablo.Vargas.Y.Regina.Noriega.exe"
- Al abrir el archivo, se abrira la terminal de windows y el programa comenzara haciendo una serie de preguntas.

### Información sobre las preguntas
- **Inserte: nombre, numero ID o codigo CAS del compuesto**
Nombre: Nombre IUPAC o nombre común (En ingles) del compuesto quimico.
Numero ID: Numero identificado en el Data Bank para el compuesto quimico.
Codigo CAS: Numero identificador unico del compuesto quimico.

Es importante considerar que el compuesto debe existir en el Data Bank del libro *The Properties of Gases and Liquids* (5th ed.), de Poling, Prausnitz y O’Connell (2001). De alli se obtienen los parametros termodinámicos para los calculos.

Despues de esta pregunta se imprime la temperatura de ebullición normal de los compuestos que vas seleccionando, esto con el proporsito de que te des una idea de que tan volatiles son. Ya que si se escogen compuestos con volatilidades totalmente diferentes pues no existe el equiliibrio liqudio-vapor y el programa falla al intentar modelarlo. 

- **Presion en bar**
La gráfica 
