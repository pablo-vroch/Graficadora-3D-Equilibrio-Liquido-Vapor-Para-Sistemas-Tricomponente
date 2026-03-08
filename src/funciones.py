import numpy as np
import json
import sys
import os


# Funcion para encontrar ruta relativa de archivos
def ruta_relativa(nombre_archivo):
    if hasattr(sys, '_MEIPASS'):
        # Estamos corriendo desde un .exe
        return os.path.join(sys._MEIPASS, nombre_archivo)
    else:
        # Estamos corriendo como .py
        return os.path.join(os.path.dirname(__file__), nombre_archivo)


# Abrimos los archivos usando rutas absolutas
with open(ruta_relativa('MAPA_ID.json'), 'r', encoding='utf-8') as file:
    MAPA_ID = json.loads(file.read())

with open(ruta_relativa('MAPA_COLUMNAS.json'), 'r', encoding='utf-8') as file:
    MAPA_COLUMNAS = json.loads(file.read())

PROP_TERMOF = np.load(ruta_relativa('PROP_TERMOF_2.1.npy'), allow_pickle=True)

# CONSTANTES
R = 83.14472
ERROR_PERMITIDO = 1e-8

# Funciones para la base de datos
def normalizar_entrada(entrada : str) -> str:
    # Hacer todo minusculas, eliminar guiones '-', eliminar espacios ' '
    entrada = entrada.casefold().replace('-','').replace(' ','')
    return entrada


def obtener_id(compuesto : float | int | str):
    """
    Devuelve la fila dentro de PROP_TERMOF donde se encuentra ubicado un compuesto
    """

    # Si es un numero del tipo int, tomalo como el ID directamente
    if isinstance(compuesto, int):
        return compuesto
    
    # Si es un numero del tipo float, conviertelo a int solamente si es entero. Sino levanta un error
    if isinstance(compuesto, float):
        if compuesto % 1 != 0:
            raise TypeError(f'El ID del compuesto debe ser un número entero. El valor : {compuesto} : levanto el error')
        else:
            return int(compuesto)
    
    # Si cualquiera de los elementos del string es una letra, entonces te proporcionaron el nombre del compuesto:
    for i in compuesto:
        if i.isalpha():

            # normalizalo y buscalo en el diccionario
            compuesto_normalizado = normalizar_entrada(compuesto)
            try:
                return MAPA_ID['NOMBRE'][compuesto_normalizado]
            except KeyError:
                raise KeyError(f'{compuesto} no esta en la base de datos, revisa que este bien escrito')
    
    # Si ninguno de los caracteres es una letra, buscalo directamente ya que debe ser el CAS
    try:
        return MAPA_ID['CAS'][compuesto]
    except KeyError:
        raise KeyError(f'{compuesto} no esta en la base de datos, revisa que este bien escrito')
    

def obtener_columna(propiedad : str) -> int | tuple:
    # Si propiedad es un valor del tipo int entonces debe ser directamente el numero de columna
    if isinstance(propiedad, int):
        return propiedad
    
    # Si propiedad es un valor del tipo float, conviertelo a entero SOLO SI es un número entero
    if isinstance(propiedad, float):
        if propiedad % 1 != 0:
            raise TypeError(f'La columna de la propiedad debe ser un número entero. El valor : {propiedad} : levanto el error')
        else:
            return int(propiedad)

    # Normalizamos el string de entrada
    propiedad = normalizar_entrada(propiedad)

    try:
        return MAPA_COLUMNAS[propiedad] 
    except KeyError:
        raise KeyError(f'la propiedad: {propiedad} no esta en la base de datos, revisa que este bien escrita')


def obtener_ids_lista(lista : list) -> list:
    """
    Recibe una lista de referencias a compuestos y devuelve otra lista correspondiente al numero
    de fila de cada compuesto

    IN:
    [['Water'], ['Ethanol'], ['7440-63-3']]
    OUT:
    np.array([440, 66, 468])
    """
    id = np.array([obtener_id(i) for i in lista], dtype=np.int16)
    return id


def obtener_columnas_lista(lista : list) -> list:
    """
    Recibe una lista de referencias a propiedades termodinamicas y devuelve otra lista
    con su correspondiente numero de columna en PROP_TERMOF.
    Si la lista contiene valores 'None' simplemente los elimina.

    IN:
    [['nombre'], ['tc'], [None], ['pc']]
    OUT:
    np.array([1, 6, 7])
    """

    # Generamos lista de numero de columnas excluyendo valores None
    columnas = list()
    for elemento in lista:

        # Excluimos elementos None
        if elemento is not None:
            col = obtener_columna(elemento)
            
            # Si la propiedad involucra varias columnas en la matriz, desempaquetalos
            if isinstance(col, list):
                columnas.extend(col)
            # Si la propiedad solo es una columna, añadela y ya esta.
            else:
                columnas.append(col)
    
    columnas = np.array(columnas, dtype=np.int16)
    return columnas


def obtener_vectores_propiedades(compuestos, propiedades):
    """
    devuelve todas las propiedades de todos los compuestos como vectores columnas de propiedades:
    Ejemplo:
    tc, pc, w = obtener_propiedades(['water', 'ethanol'], ['tc', 'pc', 'w'])
    """
    # Obtenemos vectores de las filas y columnas de los compuestos y propiedades
    filas = obtener_ids_lista(compuestos)
    columnas = obtener_columnas_lista(propiedades)

    # Generamos todas las combinaciones posibles de filas con columnas
    filas, columnas = np.meshgrid(filas, columnas, indexing='ij')

    # Generamos matriz a partir de la base de datos
    matriz_propiedades = PROP_TERMOF[filas, columnas].copy()

    # Separamos las columnas de la matriz en vectores columna de propiedades
    vectores_de_propiedades = list()
    for col in range(matriz_propiedades.shape[1]):
        vector_columna = matriz_propiedades[:, [col]].astype(np.float64)
        vectores_de_propiedades.append(vector_columna)

    # Devolvemos los vectores de propiedades desempaquetados
    return tuple(vectores_de_propiedades)


def obtener_vectores_propiedades_objeto(compuestos, propiedades):
    """
    devuelve todas las propiedades de todos los compuestos como vectores columnas de propiedades:
    Ejemplo:
    tc, pc, w = obtener_propiedades(['water', 'ethanol'], ['tc', 'pc', 'w'])

    Pero no transforma a numpy.ndarray de tipo np.float64. Sino deja los valores como objetos de python
    """
    # Obtenemos vectores de las filas y columnas de los compuestos y propiedades
    filas = obtener_ids_lista(compuestos)
    columnas = obtener_columnas_lista(propiedades)

    # Generamos todas las combinaciones posibles de filas con columnas
    filas, columnas = np.meshgrid(filas, columnas, indexing='ij')

    # Generamos matriz a partir de la base de datos
    matriz_propiedades = PROP_TERMOF[filas, columnas].copy()

    # Separamos las columnas de la matriz en vectores columna de propiedades
    vectores_de_propiedades = list()
    for col in range(matriz_propiedades.shape[1]):
        vector_columna = matriz_propiedades[:, [col]]
        vectores_de_propiedades.append(vector_columna)

    # Devolvemos los vectores de propiedades desempaquetados
    return tuple(vectores_de_propiedades)


# Funciones para procesar entradas del usuario
def procesar_num_puntos(string):
    try:
        valor_procesado = int(string)
        if valor_procesado < 0:
            raise ValueError(f'el numero de divisiones debe ser un numero positivo')
    except ValueError:
        raise ValueError(f'El numero de divisiones debe ser un numero entero positivo')
    return valor_procesado


def procesar_presion(string):
    try:
        valor_procesado = float(string)
        if valor_procesado < 0:
            raise ValueError(f'La presion debe ser positiva')
    except ValueError:
        raise ValueError(f'La presion debe ser un numero positivo')
    return valor_procesado


def procesar_modo_libre(string):
    string_procesado = string.casefold().replace('í','i').replace('ó','o').replace('0','o').replace('p','').replace(' ','')
    if string_procesado == 'si':
        return True
    if string_procesado == 'no':
        return False
    else:
        raise ValueError(f'¿¿"{string}"?? La respuesta debe ser si/no')


def comprobar_existencia_de_datos(nombre, pc, tc, w):
    """
    Corrobora si un compuesto contiene pc, tc y w. En caso de ser np.nan levanta un error
    y notifica que no tiene ese valor.
    """
    if pc[0,0] is  np.nan:
        raise ValueError(f'{nombre[0,0]} no tiene presion critica en la base de datos')
    elif tc[0,0] is np.nan:
        raise ValueError(f'{nombre[0,0]} no tiene temperatura critica en la base de datos')
    elif w[0,0] is np.nan:
        raise ValueError(f'{nombre[0,0]} no tiene factor acentrico en la base de datos')


# Funciones para calculos
def obtener_a_alfa_mezcla_y_tensor_mezclado(y, a, alfa, k):
    """
    Calcula a_alfa_mezcla y el tensor de mezclado. Ambos usados en el calculo de coeficientes de
    fugacidad en una mezcla.
    El tensor de mezclado es: sqrt(ai * aj * alfai * alfaj) * (1 - kij)

    Args:
        Variables Termodinámicas ---------------------
        alfa (C, T): Valor 'alfa' proveniente de la ecuación cúbica de estado.

        Propiedades de Compuesto ---------------------
        y (C, 1): Composiciones del compuesto i-ésimo.
        a (C, 1): Constante 'a' proveniente de la ecuación cúbica de estado.
        k (C, C): Matriz del factor de interacción binaria entre el compuesto-i y compuesto-j.

    Returns:
        a_alfa_mezcla (1, T): Vector de constante a_alfa_mezcla para diferentes temperaturas.
        tensor_mezclado (C, C, T): Tensor de tercer orden para cálculo de coeficientes de fugacidad.
    """
    # Los calculos se llevaran en los tensores de la forma:
    # (C, i, T) = (propiedad_compuesto, propiedad_compuesto, variable_termodinamica)

    # Generamos tensores aptos para broadcasting
    yi = y[:, np.newaxis]
    yj = y[np.newaxis, :]
    ai = a[:, np.newaxis]
    aj = a[np.newaxis, :]
    alfa_i = alfa[:, np.newaxis, :]
    alfa_j = alfa[np.newaxis, :, :]
    kij = k[:, :, np.newaxis]

    # Tensor auxiliar 'pepe' resultara muy util para el calculo de coeficientes de fugacidad
    tensor_mezclado = np.sqrt(ai * aj * alfa_i * alfa_j) * (1 - kij)
    a_alfa_mezcla = yi * yj * tensor_mezclado

    # Sumamos sobre los ejes de las composiciones (C, i, T)
    a_alfa_mezcla = np.sum(np.sum(a_alfa_mezcla, axis=0), axis=0)

    # Regresamos a_alfa_mezcla con shape: (1, T) 
    # Regresamos tensor_mezclado con shape = (C, C, T)
    return a_alfa_mezcla[np.newaxis, :], tensor_mezclado


def cardano_vectorizado(a : np.ndarray, b : np.ndarray, c : np.ndarray, d : np.ndarray):
    """
    Encuentra las raíces reales de un polinomios de tercer grado usando el metodo de cardano.
    funciona con Numpy de manera vectorizada
    El polinomio tiene la forma : 
    P(x) = a*x^3 + b*x^2 + c*x + d
    
    Args:
        a, b, c, d (1, T): vectores de coeficientes del polinomio.

    Returns:
        array_soluciones (3, T) : Matriz que contiene las raices reales del polinomio.
    """
    array_soluciones = np.empty((3, a.shape[1]), dtype=np.float64) # La matriz de soluciones a devolver

    p = (3*a*c - b**2) / (3*a**2)
    q = (2*b**3 - 9*a*b*c + 27*a**2*d) / (27*a**3)
    dis = q**2 + (4*p**3) / 27
    b_entre_3a = b / (3 * a)

    # CASO 1 -> UNICA RAIZ REAL
    caso_1 = dis > 1e-12
    dis_caso = dis[caso_1]
    b_entre_3a_caso = b_entre_3a[caso_1]
    q_caso = q[caso_1]

    u = np.cbrt(
        (-q_caso + np.sqrt(dis_caso)) / 2
    )
    v = np.cbrt(
        (-q_caso - np.sqrt(dis_caso)) / 2
    )
    z_caso_1 = u + v - b_entre_3a_caso
    z_caso_1 = np.vstack([z_caso_1, np.full(z_caso_1.shape, np.nan), np.full(z_caso_1.shape, np.nan)])
    
    # CASO 2 -> Se fragmenta en otros dos casos
    caso_2 = np.isclose(dis, 0, atol=1e-12)
    p_y_q_son_cero = np.logical_and(np.isclose(p, 0, atol=1e-12), np.isclose(q, 0, atol=1e-12))

    # CASO 2_1 -> Tres soluciones reales identicas -> Det = 0 y p = 0 y q = 0
    caso_2_1 = np.logical_and(caso_2, p_y_q_son_cero)
    
    z_caso_2_1 = -b_entre_3a[caso_2_1]
    z_caso_2_1 = np.vstack([z_caso_2_1, z_caso_2_1, z_caso_2_1])

    # CASO 2_2 -> Tres soluciones reales, dos iguales -> Det = 0 y (p != 0 o q != 0)
    caso_2_2 = np.logical_and(caso_2, np.logical_not(caso_2_1))
    p_caso = p[caso_2_2]
    q_caso = q[caso_2_2]
    b_entre_3a_caso = b_entre_3a[caso_2_2]

    z1_caso_2_2 = 3 * q_caso / p_caso - b_entre_3a_caso
    z2_caso_2_2 = -3 * q_caso / (2 * p_caso) - b_entre_3a_caso
    z_caso_2_2 = np.vstack([z1_caso_2_2, z2_caso_2_2, z2_caso_2_2])
    z_caso_2_2 = np.sort(z_caso_2_2, axis=0)

    # CASO 3 -> Tres soluciones reales todas diferentes -> dis < 0
    caso_3 = dis < -1e-12
    dis_caso = dis[caso_3]
    p_caso = p[caso_3]
    q_caso = q[caso_3]
    b_entre_3a_caso = b_entre_3a[caso_3]

    theta = np.arccos(
        (3 * q_caso) / (2 * p_caso) * np.sqrt(-3 / p_caso)
    )
    z1_caso_3 = 2 * np.sqrt(-p_caso / 3) * np.cos(theta / 3) - b_entre_3a_caso
    z2_caso_3 = 2 * np.sqrt(-p_caso / 3) * np.cos((theta + 2*np.pi) / 3) - b_entre_3a_caso
    z3_caso_3 = 2 * np.sqrt(-p_caso / 3) * np.cos((theta + 4*np.pi) / 3) - b_entre_3a_caso
    z_caso_3 = np.vstack([z2_caso_3, z3_caso_3, z1_caso_3])

    # Juntar todos los casos en un solo array
    # vamos a usar los siguientes numeros para distinguir entre casos:
    # CASO_1 : 0, CASO_2_1 : 1, CASO_2_2 : 2, CASO_3 : 3

    # Creamos vector que contiene todos los casos
    casos = 1*caso_2_1 + 2*caso_2_2 + 3*caso_3
    casos = casos.ravel()

    # Dependiendo de cada caso insertamos sus raíces respectivas
    array_soluciones[:, casos == 0] = z_caso_1
    array_soluciones[:, casos == 1] = z_caso_2_1
    array_soluciones[:, casos == 2] = z_caso_2_2
    array_soluciones[:, casos == 3] = z_caso_3

    return array_soluciones


def coef_fugacidad_mezcla_peng_robinson(presion, temperatura, composiciones, pc, tc, w, k, volumen_num=0):
    """
    Funcion de compuesto: Devuelve el coeficiente de fugacidad de un compuesto a las dierentes condiciones
    de presion y temperatura. En una mezcla homogenea (ya sea liquido o vapor) de compuestos.

    Todos los calculos hechos aqui estan basados en el libro: Chemical, Biochemical and engineering thermodynamics
    5ta edicion de: Stanley I. Sandler. En la pagina: 440.

    Args:
        Variables Termodinamicas ---------------------------------------------------------
        presion (1, T) : vector de presion en bar.
        temperatura (1, T) : vector de temperaturas kelvin.

        Propiedades de Compuesto -----------------------------------------------------------
        composiciones (C, 1) : vector de las composiciones de cada compuesto de la mezcla.
        pc (C, 1) : vector de las presiones críticas de cada compuesto de la mezcla.
        tc (C, 1) : vector de las temperaturas críticas de cada compuesto de la mezcla.
        w (C, 1) : vector de factores acentricos.
        k (C, C) : matriz de factor de interacción binaria entre compuesto-i y compuesto-j

        kwargs --------------------------------------------------------------------------
        volumen_num=0: Peng Robinson puede devolver un unico volumen ó un volumen de la fase liquida y 
        volumen de la fase vapor. Siempre organizadas de menor a mayor. Este argumento te permite escoger
        con que raiz te quedas.
        CUIDADO: si la ecuacion devuelve una raiz unica entonces se organizan de la siguiente manera:
        [raiz_unica, np.nan, np.nan] entonces volumen_num = 1,2 devolvera np.nan.

    Returns:
        coef_fugacidad (C, T): Devuelve el coeficiente de fugacidad del compuesto 'C' a las condiciones 'T'
        en la mezcla.
    """
    # Calculamos parametros de la ecuacion de peng robinson
    a = (0.45724 * R**2 * tc**2) / pc
    b = (0.0778 * R * tc) / pc
    pw = 0.37464 + 1.54226 * w - 0.26992 * w**2
    alfa = (1 + pw * (1 - np.sqrt(temperatura / tc)))**2
    b_mezcla = np.sum(composiciones * b)

    # Calculamos a_alfa_mezcla y tensor de mezclado.
    a_alfa_mezcla, tensor_mezclado = obtener_a_alfa_mezcla_y_tensor_mezclado(composiciones, a, alfa, k)

    # Calculamos tensor A_ij (checar libro Sandler)
    aij = presion[np.newaxis, :] / (R * temperatura[np.newaxis, :])**2 * tensor_mezclado

    # Calculamos volumenes.
    termino_cubo = presion
    termino_cuadrado = b_mezcla * presion - R * temperatura
    termino_lineal = a_alfa_mezcla - 2 * R * temperatura * b_mezcla - 3 * presion * b_mezcla**2
    termino_independiente = presion * b_mezcla**3 + R * temperatura * b_mezcla**2 - a_alfa_mezcla * b_mezcla
    volumen = cardano_vectorizado(termino_cubo, termino_cuadrado, termino_lineal, termino_independiente)

    # Nos quedamos solamente con un volumen
    volumen = volumen[volumen_num, :]

    # Calculamos factor de compresibilidad y variables de calculo
    z_mix = presion * volumen / (R * temperatura)
    bi = b * presion / (R * temperatura)
    ai = a * alfa * presion / (R * temperatura)**2
    a_mix = a_alfa_mezcla * presion / (R * temperatura)**2
    b_mix = b_mezcla * presion / (R * temperatura)

    # Calculamos el logaritmo natural del coeficiente de fugacidad
    suma_yj_aij = np.sum(composiciones[:, np.newaxis] * aij, axis=0) # Calculamos un termino de sumatoria
    log_phi = bi / b_mix * (z_mix - 1) - np.log(z_mix - b_mix) - a_mix / (2 * np.sqrt(2) * b_mix) * (2 * suma_yj_aij / a_mix - bi / b_mix) * np.log((z_mix + (1 + np.sqrt(2)) * b_mix) / (z_mix + (1 - np.sqrt(2)) * b_mix))

    # Regresamos matriz de coeficientes de fugacidad
    return np.exp(log_phi) 


def resolver_newton_raphson(funcion, objetivo, suposicion, max_iter=100, tol=ERROR_PERMITIDO, jacobiano=None):
    """
    Aplica el metodo de newton raphson a una funcion tal que evaluada en la salida de esta funcion. Sea igual a objetivo.
    """
    # Si no se especifica un jacobiano de transformacion lineal, calcularlo numericamente
    if not jacobiano:
        tamaño_entradas = len(suposicion)
        tamaño_salidas = len(objetivo)
        identidad = np.identity(tamaño_entradas)

        def jacobiano(x):
            jac = np.empty((tamaño_salidas, tamaño_entradas), dtype=np.float64)

            for i in range(tamaño_entradas):
                step = 1e-6 * identidad[:, i]
                dfdx = ((funcion(x + step) - funcion(x - step)) / 2e-6)
                jac[:, i] = dfdx

            return jac
        
    # Iniciamos el bucle del metodo de Newton Raphson
    for _ in range(max_iter // 5):
        # Itermaos 5 veces antes de checar que hayamos encontrado la solucion
        for _ in range(5):
            fx = funcion(suposicion) - objetivo
            j = jacobiano(suposicion)

            sol_local = np.linalg.solve(j, -fx)
            suposicion = suposicion + sol_local

        # Checamos si encontramos la solucion
        if np.linalg.norm(funcion(suposicion) - objetivo) <= ERROR_PERMITIDO:
            return suposicion

