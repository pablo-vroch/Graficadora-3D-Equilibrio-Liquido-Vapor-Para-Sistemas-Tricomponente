# Graficadora-3D-Equilibrio-Liquido-Vapor-Para-Sistemas-Tricomponente
Este proyecto consiste en un archivo .exe (ejecutable de windows) que te permite visualizar el equilibrio liquido-vapor de una mezcla de tres compuestos químicos como una superficie 3D. En la figura 1 se ve un ejemplo de una grafica generada por este programa.

![Superficie 3D representando el equilibrio liquido-vapor para una mezcla de benceno, ethanol y hexano](/imagenes/fig1.png)

## Detalles del modelo termodinámico 
La grafica presenta la temperatura de burbuja y rocío de la mezcla para cada composicion posible (considerando que son 3 compuestos). Cada composicion posible se representa sobre un diagrama ternario, y la altura de la grafica representa la temperatura de burbuja (de color azul) y la temperatura de rocio (con un mapa de colores). 
El modelo de equilibrio es el modelo de doble phi.

$$
y_i \ \phi_i^{V} = x_i \ \phi_i^{L}
$$

Los coeficientes de fugacidad se calculan empleando la ecuación de estado de Peng-Robinson. El sistema se resuelve mediante el método númerico de Newton-Raphson para funciones vectoriales.

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

- **Presion en bar**:
La gráfica es a presión constante, entonces aqui se ingresa la presion del sistema

 - **Número de divisiones entre composiciones**:
Cuantas divisiones hay entre los vertices del diagrama tenrario. Se relaciona con la resolución del diagrama, mientras mas divisiones halla, tendra mayor resolución pero le tomara mas tiempo ejecutarse.

- **Deseas que el programa continue ejecutandose a pesar de errores de calculo?**:
Si se escoge un sistema complicado (por ejemplo que contenga compuestos con gran diferencia de volatilidad o muy polares), muchas veces la solución númerica no converge para un punto en especifico. Si se activa esta opcion, el diagrama continuara graficandose a pesar de estos puntos erroneos. En otro caso el programa se detendra.


