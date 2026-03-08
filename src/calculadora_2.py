import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import funciones as f

# Interfaz de usuario para que seleccione datos
input('Grafica la temperatura de burbuja y temperatura de rocio de una mezcla de tres componentes en un diagrama ternario. presiona [Enter] para continuar')

# Detener el programa si no se encuentra una solucion?
modo_libre = input('Deseas que el programa continue ejecutandose a pesar de errores de calculo? [SI/NO]: ')
modo_libre = f.procesar_modo_despreocupado(modo_libre)

# Obtenemos compuesto 1, e imprimimos nombre y temperatura de ebullicion
compuesto_1 = input('Inserte nombre o ID del primer compuesto: ')
teb, nombre = f.obtener_vectores_propiedades_objeto([compuesto_1], ['tbp', 'nombre'])
print(f'Temperatura de ebullicion de {nombre[0,0]}: {round(teb[0,0] - 273.15, 1)}°C')

# Compuesto 2
compuesto_2 = input('Compuesto 2: ')
teb, nombre = f.obtener_vectores_propiedades_objeto([compuesto_2], ['tbp', 'nombre'])
print(f'Temperatura de ebullicion de {nombre[0,0]}: {round(teb[0,0] - 273.15, 1)}°C')

# Compuesto 3
compuesto_3 = input('Compuesto 3: ')
teb, nombre = f.obtener_vectores_propiedades_objeto([compuesto_3], ['tbp', 'nombre'])
print(f'Temperatura de ebullicion de {nombre[0,0]}: {round(teb[0,0] - 273.15, 1)}°C')

# Presion
presion = input('La presion en bar: ')

# Numero de puntos
num_puntos = input('Numero de divisiones entre composiciones (resolucion del diagrama): ')


# Procesamos entradas del usuario
compuestos = [compuesto_1, compuesto_2, compuesto_3]
presion = f.procesar_presion(presion)
num_puntos = f.procesar_num_puntos(num_puntos)


# GENERAMOS ARRAYS DE NUMPY
antoine_a, antoine_b, antoine_c, teb, pc, tc, w = f.obtener_vectores_propiedades(compuestos, ['anta', 'antb', 'antc', 'tbp', 'pc', 'tc', 'w'])
k = np.zeros((3,3))
presion = np.array([presion], dtype=np.float64)
presion = presion[np.newaxis, :]


# Generamos todas las combinaciones de composiciones
z1 = np.linspace(0, 1, num=num_puntos)
z2 = z1.copy()
z1, z2 = np.meshgrid(z1, z2, indexing='xy')


# Eliminamos valores done z1 + z2 > 1
valores_invalidos = z1 + z2 > 1
z1[valores_invalidos], z2[valores_invalidos] = np.nan, np.nan


# Defnimos funcion que encuentra la temperatura de saturacion promedio de la mezcla
# Esta funcion es necesaria ya que el modelo doble phi es sumamente inestable. Una mala suposicion inicial provoca
# que el metodo de newton raphson no converga, erroes de calculo (ej. divisiones por cero, logarimtos negativos etc)
def temperatura_promedio(z1, z2):

    # Calculamos temperaturas de saturacion usando la ecuacion de antoine
    temp_sat_antoine = antoine_b / (antoine_a - np.log10(presion)) - antoine_c + 273.15

    # Calculamos temperaturas de saturacion usando una interpolacion exponencial entre (Teb, atm) y (Tc, Pc)
    temp_sat_aprox = np.log(presion / 1.013) * (tc - teb) / np.log(pc / 1.013) + teb
    temp_sat_aprox = temp_sat_aprox.ravel()

    # Si algun compuesto no tiene constantes de antoine. Tendra valores np.nan en su lugar. Aqui sustituimos np.nan por la aproximacion exponencial de temperatura
    temperatura_sat = temp_sat_antoine.ravel()
    valores_nan = np.isnan(temperatura_sat)
    temperatura_sat[valores_nan] = temp_sat_aprox[valores_nan]
    
    # Convertimos composiciones a un vector
    z = np.array([z1, z2, 1 - z1 - z2], dtype=np.float64)

    # Devolvemos la temperatura ponderada
    return np.sum(temperatura_sat * z)


# Definimos funcion para obtener el error de la condicion de equilibrio
def error(x1, x2, y1, y2, temp):
    """
    Devuelve un vector del error en la condicion de equilibrio para una mezcla
    F(x,y,T) = (f1, f2, f3)
    donde:
    fi = phi_i_liqido * xi - phi_i_vapor * yi
    Args:
        x1, x2 (float): composiciones molares en el liquido
        y1, y2 (float): composiciones molares en el vapor
        temp (float): temperatura en kelvin
    Returns:
        error (3, ): Vector de errores para cada condicion de equilibrio

    """
    # Vectorizamos entradas para que sean compatibles con la funcion
    x = np.array([x1, x2, 1-x1-x2], dtype=np.float64)
    y = np.array([y1, y2, 1-y1-y2], dtype=np.float64)
    x = x[:, np.newaxis]
    y = y[:, np.newaxis]
    temp = np.array([[temp]], dtype=np.float64)

    # Calculamos coeficientes de fugacidad
    phi_liq = f.coef_fugacidad_mezcla_peng_robinson(presion, temp, x, pc, tc, w, k, volumen_num=0)
    phi_vap = f.coef_fugacidad_mezcla_peng_robinson(presion, temp, y, pc, tc, w, k, volumen_num=2)

    # Calculamos error en base a la condicion de equilibrio
    error = x * phi_liq - y * phi_vap

    return error.ravel()


# Funcion para encontrar temperatura de burbuja
def resolver_burbuja(z1, z2):
    """
    Encuentra la temperatura de burbuja de una mezcla a las composiciones molares z1, z2
    Args:
        z1, z2 (float): Composiciones molares totales en la mezcla de los compuestos 1 y 2
    Returns:
        (y1, y2, temperatura_burbuja) (tuple)

        y1, y2 (numpy.float64): Composiciones del compuesto 1 y 2 en en vapor cuando el v/f = 0
        temperatura_burbuja (numpy.float64): Temperatura de burbuja la mezcla
    """
    # Si z1 es np.nan. Devolver np.nan
    if np.isnan(z1):
        return np.nan
    
    # En el punto de burbuja xi = zi
    x1, x2 = z1, z2

    # Guess inicial de vector de solucion (y1, y2, temp. burbuja)
    inc = np.array([0.333, 0.333, temperatura_promedio(z1, z2)], dtype=np.float64)

    # Definimos una funcion compatible con el metodo de newton raphson
    def error_burbuja(incognita):
        """
        Esta funcion toma un np.ndarray que contiene (y1, y2, temperatura_burbuja)
        y devuelve un vector de error de la condicion de equilibrio (err1, err2, err3)
        """
        y1, y2, temperatura = incognita[0], incognita[1], incognita[2]
        return error(x1, x2, y1, y2, temperatura)
    
    # Aplicamos el metodo de newton raphson.
    solucion = f.resolver_newton_raphson(error_burbuja, np.zeros((3,)), inc)

    # Desempaquetamos temperatura de burbuja y la devolvemos
    temperatura_burbuja = solucion[2]
    return temperatura_burbuja


# Funcion para encontrar temperatura de rocío
def resolver_rocio(z1, z2):
    """
    Encuentra la temperatura de rocio de una mezcla a las composiciones molares z1, z2
    Args:
        z1, z2 (float): Composiciones molares totales en la mezcla de los compuestos 1 y 2
    Returns:
        x1, x2, temperatura_rocio (tuple)
        x1, x2 (numpy.float64): Composiciones molares en la fase liquida de los compuestos 1 y 2
        cuando v/f = 1
        temperatura_rocio (numpy.float64): Temperatura de burbuja de la mezcla
    """
    # Si z1 o z2 son np.nan. Devolver np.nan
    if np.isnan(z1):
        return np.nan
    
    # En el punto de rocío yi = zi
    y1, y2 = z1, z2

    # Guess inicial de vector de solucion (x1, x2, temp. rocio)
    inc = np.array([0.333, 0.333, temperatura_promedio(z1, z2)], dtype=np.float64)

    # Definimos una funcion compatible con el metodo de newton raphson
    def error_rocio(incognita):
        """
        Esta funcion toma un np.ndarray cuyas componentes [x1, x2, temperatura_rocio] y devuelve
        un vector que representa el error de la condicion de equilibrio [err1, err2, err3]
        """
        x1, x2, temperatura = incognita[0], incognita[1], incognita[2]
        return error(x1, x2, y1, y2, temperatura)
    
    # Aplicamos el metodo de newton raphson
    solucion = f.resolver_newton_raphson(error_rocio, np.zeros((3)), inc)

    # Desempaquetamos temperatura de rocio y la devolvemos
    temperatura_rocio = solucion[2]
    return temperatura_rocio

### ### ### ###
# A continuacion, se iterara por cada elemento y se encontrara la temperatura de burbuja, y la temperatura de rocio
### ### ### ###

# Generamos array vacio de temperatura de rocio, burbuja
temperatura_burbuja = np.empty(z1.shape, dtype=np.float64)
temperatura_rocio = np.empty(z1.shape, dtype=np.float64)


# Bucle que itera sobre las matrices de composiciones z1 y z2. Encontramos temp. rocio y burbuja en cada punto
filas = z1.shape[0]
columnas = z1.shape[1]
puntos_totales = filas * columnas
contador = 0

# Si el modo libre esta habilitado. Ignora cualquier error y sigue calculado
if modo_libre:
    for i in range(filas):
        for j in range(columnas):

            try:
                temperatura_burbuja[i,j] = resolver_burbuja(z1[i,j], z2[i,j])
                temperatura_rocio[i,j] = resolver_rocio(z1[i,j], z2[i,j])
            except:
                temperatura_burbuja[i,j] = np.nan
                temperatura_rocio[i,j] = np.nan
            contador += 1
            progreso = contador / puntos_totales * 100
            print(f'{round(progreso, 2)}%')

# Si el modo libre no esta habilitado. Deja que python se detenga ante un error
else:
    for i in range(filas):
        for j in range(columnas):
            temperatura_burbuja[i,j] = resolver_burbuja(z1[i,j], z2[i,j])
            temperatura_rocio[i,j] = resolver_rocio(z1[i,j], z2[i,j])

            contador += 1
            progreso = contador / puntos_totales * 100
            print(f'{round(progreso, 2)}%')

# Aqui generamos la superficie
# Hacemos un cambio de coordenadas para graficar en el diagrama ternario
# z1 => (x=0, y=0), z2 => (x=0.5, y=1.5), z3 => (x=1, y=0)
x = 1/2 * (z2 + 2 * (1 - z1 - z2))
y = 3/2 * z2

# Convertimos las temperaturas de Kelvin a Celsius
temperatura_rocio = temperatura_rocio - 273.15
temperatura_burbuja = temperatura_burbuja - 273.15

# Graficamos con matplotlib
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.plot_surface(x, y, temperatura_burbuja, cmap=cm.plasma)
ax.plot_surface(x, y, temperatura_rocio, cmap=cm.plasma)

# Calculamos las temperaturas de saturacion de los compuestos (para saber a que altura z colocar etiquetas en la grafica)
temp_sat_antoine = antoine_b / (antoine_a - np.log10(presion)) - antoine_c + 273.15
temp_sat_aprox = np.log(presion / 1.013) * (tc - teb) / np.log(pc / 1.013) + teb
temp_sat_aprox = temp_sat_aprox.ravel()
temperatura_sat = temp_sat_antoine.ravel()
valores_nan = np.isnan(temperatura_sat)
temperatura_sat[valores_nan] = temp_sat_aprox[valores_nan]
temperatura_sat = temperatura_sat - 273.15

# Colocamos el nombre de cada compuesto en el diagrama ternario
ax.text(x=0, y=0, z=temperatura_sat[0], s=compuestos[0])
ax.text(x=0.5, y=1.5, z=temperatura_sat[1], s=compuestos[1])
ax.text(x=1, y=0, z=temperatura_sat[2], s=compuestos[2])

# Colocamos nombre del eje vertical
ax.set_zlabel("Temperatura [°C]")
plt.show()
