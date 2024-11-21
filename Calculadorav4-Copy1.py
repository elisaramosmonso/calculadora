#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
import streamlit as st
import sqlite3
import openpyxl
import openpyxl
from io import BytesIO

lat = st.sidebar.selectbox('Menú principal',('Calculadora','Gestionar empleados','Histórico'))

def cargar_datos(uploaded_file):
    t1 = pd.read_excel(uploaded_file, sheet_name='TABLA 1')
    t22 = pd.read_excel(uploaded_file, sheet_name='tabla 2.2')
    t2 = pd.read_excel(uploaded_file, sheet_name='TABLA 2')
    t33 = pd.read_excel(uploaded_file, sheet_name='Tabla3.3')
    t3 = pd.read_excel(uploaded_file, sheet_name='TABLA 3')
    t4 = pd.read_excel(uploaded_file, sheet_name='TABLA 4')
    return t1, t22, t2, t33, t3, t4

if lat == 'Calculadora':
    st.title('CALCULADORA DE RETRIBUCIONES')

    # Verificar si ya existe un archivo cargado en session_state
    if 'uploaded_file' in st.session_state:
        uploaded_file = st.session_state.uploaded_file
        t1 = st.session_state.t1
        t22 = st.session_state.t22
        t2 = st.session_state.t2
        t33 = st.session_state.t33
        t3 = st.session_state.t3
        t4 = st.session_state.t4
        st.info("Archivo recuperado de la sesión.")
    else:
        uploaded_file = st.file_uploader("Elige un archivo Excel", type=["xlsx", "xls", "xlsm"])

        # Si se carga un archivo, lo guardamos en session_state
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            t1, t22, t2, t33, t3, t4 = cargar_datos(uploaded_file)
            # Guardamos los DataFrames en session_state
            st.session_state.t1 = t1
            st.session_state.t22 = t22
            st.session_state.t2 = t2
            st.session_state.t33 = t33
            st.session_state.t3 = t3
            st.session_state.t4 = t4
            st.success("Archivo cargado")
        else:
            st.warning("Por favor, carga un archivo Excel para continuar.")

    # Si las tablas están definidas, realizamos el cálculo
    if 't1' in st.session_state and 't22' in st.session_state:
        t1 = st.session_state.t1
        t22 = st.session_state.t22

        dummy = 'Selecciona una opción'
        error1 = 'No has seleccionado un área o departamento'
        areas = t1['ÁREA'].drop_duplicates().to_list()
    
        st.header('Calculadora de retribuciones')
        area = st.selectbox('Área / Departamento',options = [dummy] + areas,index = 0)
    
        if area is not dummy:
            puestos = t1[t1['ÁREA'] == area]['PUESTO'].drop_duplicates().to_list()
            puesto = st.selectbox('Puesto',[dummy] + puestos, index = 0)
    
        else:
            puesto = st.selectbox('Puesto',[error1])
    
        if (puesto is not dummy) and (puesto is not error1):
            trabajadores = t1[(t1['ÁREA'] == area) & (t1['PUESTO'] == puesto)]['NOMBRE'].drop_duplicates().to_list()
            trabajador = st.selectbox('Empleado',[dummy]+trabajadores, index = 0)
    
        else:
            trabajador = st.selectbox('Trabajador',['No has seleccionado un puesto'])
    
        niveles = t22['Nivel'].drop_duplicates().to_list()
        nivel = st.selectbox('Nivel',[dummy] + niveles, index = 0)
        nivel_g = st.selectbox('Nivel Gerencia',[dummy] + niveles, index = 0)
    
        if (nivel is not dummy) and (nivel_g is not dummy):
    
            # Calculando los valores
            bs = pd.DataFrame(columns = ['Banda \n salarial \n actual','Banda \n salarial \n Responsable',
                                     'Banda \n salarial \n Gerencia','PROPUESTA \n DE RETRIBUCIÓN','DIFERENCIA \n DE RETRIBUCIÓN'])
    
            bsact = float(str(t4[(t4['NOMBRE'] == trabajador) & (t4['PUESTO'] == puesto)]['SALARIO BRUTO AÑO'].iloc[0]).replace(',','.'))
            bsresp = float(str(t33[(t33['PUESTO']==puesto) & (t33['Nivel']==nivel)]['Rango Retributivo'].iloc[0]).replace(',','.'))
            bsger = float(str(t33[(t33['PUESTO']==puesto) & (t33['Nivel']==nivel_g)]['Rango Retributivo'].iloc[0]).replace(',','.'))
            propret = 0.5*(bsresp+bsger)
            difret = propret-bsact
    
            bs.loc[len(bs)] = [round(bsact,2),round(bsresp,2),round(bsger,2),round(propret,2),round(difret,2)]
    
            v = pd.DataFrame(columns = ['Valoración Responsable','Valoración Gerencia','Nivel Esperado - Comparador Responsable',
                                    'Nivel Esperado - Comparador Gerencia','Diferencia Nivel - Valoración Responsable',
                                    'Diferencia Nivel - Valoración Gerencia'])
    
            zoom = pd.DataFrame(columns = ['ID','Conocimientos Técnicos','Valoración Responsable','Valoración Gerencia',
                                       'Nivel Esperado - Comparador Responsable','Nivel Esperado - Comparador Gerencia',
                                       'Diferencia Nivel - Valoración Responsable','Diferencia Nivel - Valoración Gerencia'])
    
            IDS = t1[(t1['NOMBRE']==trabajador) & (t1['PUESTO'] == puesto) & (t1['ÁREA'] == area)]['ID CONOCIMIENTO'].to_list()
            IDS = list(map(int,IDS))
            conoc = t1[(t1['NOMBRE']==trabajador) & (t1['PUESTO'] == puesto) & (t1['ÁREA'] == area)]['CONOCIMIENTO'].to_list()
            valres = t1[(t1['NOMBRE']==trabajador) & (t1['PUESTO'] == puesto) & (t1['ÁREA'] == area)]['VALORACIÓN'].to_list()
            valres = list(map(int, valres))
    
            # Simulamos la valoración por Gerencia (todos los valores a 0 por ahora)
            valger = [0]*len(valres)
    
            necr = []
            necg = []
    
            for i in range(0,len(IDS)):
                val = t22[(t22['ID CONOCIMIENTO']==IDS[i]) & (t22['CONOCIMIENTO']==conoc[i]) & (t22['Nivel']==nivel)]['Valor'].to_list()[0]
                val_g = t22[(t22['ID CONOCIMIENTO']==IDS[i]) & (t22['CONOCIMIENTO']==conoc[i]) & (t22['Nivel']==nivel_g)]['Valor'].to_list()[0]
                necr.append(int(val))
                necg.append(int(val_g))
    
            zoom['ID'] = IDS
            zoom['Conocimientos Técnicos'] = conoc
            zoom['Valoración Responsable'] = valres
            zoom['Valoración Gerencia'] = valger
            zoom['Nivel Esperado - Comparador Responsable'] = necr
            zoom['Nivel Esperado - Comparador Gerencia'] = necg
    
            zoom['Diferencia Nivel - Valoración Responsable'] = zoom['Valoración Responsable'] - zoom['Nivel Esperado - Comparador Responsable']
            zoom['Diferencia Nivel - Valoración Gerencia'] = zoom['Valoración Gerencia'] - zoom['Nivel Esperado - Comparador Gerencia']
    
            for col in v.columns:
                total= int(zoom[col].sum(axis=0))
                v.loc[0,col]= total
            v = v.reset_index(drop=True)
            zoom = zoom.reset_index(drop=True)
            st.session_state.bs_data = bs
            st.session_state.v_data = v
            st.session_state.zoom_data = zoom
            # Estilos y formato
            def highlight_cells(val):
                if val > 0:
                    color = 'green'
                elif val < 0:
                    color = 'red'
                else:
                    return ''  # No aplicar ningún estilo si es 0
                return f'color: {color}'
    
            def formato_euro(val):
                return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    
            if st.button('Calcular'):
                BS_data = bs.reset_index(drop=True)
                BS_styled = BS_data.style.applymap(highlight_cells, subset=['DIFERENCIA \n DE RETRIBUCIÓN']).format(formato_euro)
    
                # Mostrar las tablas
                st.table(BS_styled)
                st.table(v.reset_index(drop=True))
                st.table(zoom.reset_index(drop=True))
    
                value = bs['Banda \n salarial \n actual'].iloc[0]
                delta = bs['DIFERENCIA \n DE RETRIBUCIÓN'].iloc[0]
                value_f = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + " €"
                delta_f = f"{delta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + " €"
    
                st.metric(label = 'Banda salarial',value = value_f, 
                                 delta =  delta_f)
    
                if st.button('Guardar'):
                    # Guardar los datos modificados
                    if 'bs_data' in st.session_state:
                        uploaded_file = st.session_state.uploaded_file
                        wb = openpyxl.load_workbook(uploaded_file)
                
                        with BytesIO() as output:
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                bs_data = st.session_state.bs_data
                                bs_data.to_excel(writer, sheet_name="Historial2", index=False)
                                writer.save()
    
                            output.seek(0)
                            st.session_state.uploaded_file = output.read()  # Guardar el archivo modificado en session_state
                
                        st.success('Archivo guardado correctamente en "Historial2"')
                    else:
                        st.warning('No hay datos para guardar. Por favor, realiza un cálculo primero.')

                                        
def conectar_db():
    conn = sqlite3.connect('base_de_datos.db')
    return conn

# Función para consultar los datos de la tabla 'trabajadores'
def obtener_trabajadores():
    conn = conectar_db()
    query = "SELECT * FROM trabajadores"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para agregar un trabajador a la base de datos
def agregar_trabajador(nombre, apellido1, apellido2, area, puesto, estado):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trabajadores (nombre, apellido1, apellido2, area, puesto, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido1, apellido2, area, puesto, estado))
    conn.commit()
    conn.close()

# Función para eliminar un trabajador por su nombre
def eliminar_trabajador(nombre):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trabajadores WHERE nombre = ?', (nombre,))
    conn.commit()
    conn.close()

# Función para cambiar el puesto de un trabajador por su nombre
def cambiar_puesto(nombre, nuevo_puesto):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE trabajadores SET puesto = ? WHERE nombre = ?', (nuevo_puesto, nombre))
    conn.commit()
    conn.close()
    
if lat == 'Gestionar empleados':
    st.title('Gestión de empleados')
    
    # Mostrar la tabla de trabajadores
    df_trabajadores = obtener_trabajadores()
    st.subheader('Lista de Trabajadores')
    st.dataframe(df_trabajadores)
    
    # Sección para agregar un trabajador
    st.subheader('Agregar Nuevo Trabajador')
    nombre = st.text_input('Nombre')
    apellido1 = st.text_input('Primer Apellido')
    apellido2 = st.text_input('Segundo Apellido')
    area = st.text_input('Área')
    puesto = st.text_input('Puesto')
    estado = st.selectbox('Estado', ['activo', 'inactivo'])
    
    if st.button('Agregar Trabajador'):
        if nombre and apellido1 and area and puesto and estado:
            agregar_trabajador(nombre, apellido1, apellido2, area, puesto, estado)
            st.success('Trabajador agregado correctamente')
            st.rerun()
        else:
            st.error('Por favor, complete todos los campos')
    
    # Sección para eliminar un trabajador por nombre
    st.subheader('Eliminar Trabajador')
    nombre_a_eliminar = st.text_input('Nombre del Trabajador a Eliminar')
    
    if st.button('Eliminar Trabajador'):
        if nombre_a_eliminar:
            eliminar_trabajador(nombre_a_eliminar)
            st.success(f'Trabajador con nombre "{nombre_a_eliminar}" eliminado correctamente')
            st.rerun()
        else:
            st.error('Por favor, ingrese un nombre válido')
    
    # Sección para cambiar el puesto de un trabajador por nombre
    st.subheader('Cambiar Puesto de un Trabajador')
    nombre_a_cambiar = st.text_input('Nombre del Trabajador a Modificar')
    nuevo_puesto = st.text_input('Nuevo Puesto')
    
    if st.button('Cambiar Puesto'):
        if nombre_a_cambiar and nuevo_puesto:
            cambiar_puesto(nombre_a_cambiar, nuevo_puesto)
            st.success(f'Puesto del trabajador con nombre "{nombre_a_cambiar}" actualizado a "{nuevo_puesto}"')
            st.rerun()
        else:
            st.error('Por favor, ingrese un nombre válido y un nuevo puesto')


if lat == 'Histórico':
    st.title('Historial')
    

    # Verifica si ya se han calculado los datos y si están en session_state
    if 'bs_data' in st.session_state:
        st.write("Historial de cálculos:")
        st.table(st.session_state.bs_data)
    else:
        st.warning("No hay datos calculados aún.")


# In[10]:


def ver_datos():
    conn= sqlite3.connect('base_de_datos.db')
    query = "SELECT * FROM trabajadores"
    
    # Ejecutar la consulta y cargar los resultados en un DataFrame
    df = pd.read_sql(query, conn)
    
    # Mostrar los primeros registros
    print(df.head())
    
    conn.close()


# In[ ]:





# def crear_tablas():
#     conn = conectar_db()
#     cursor = conn.cursor()
#     
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS retribuciones (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             trabajador_id INTEGER NOT NULL,
#             banda_salarial_actual REAL,
#             banda_salarial_responsable REAL,
#             banda_salarial_gerencia REAL,
#             banda_salarial_propuesta REAL,
#             diferencia REAL,
#             fecha_evaluacion DATE NOT NULL,
#             FOREIGN KEY (trabajador_id) REFERENCES trabajadores(id)
#         )
#     ''')
#         
#         
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS valoraciones (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             trabajador_id INTEGER NOT NULL,
#             valoracion_responsable REAL,
#             valoracion_gerencia REAL,
#             nivel_esperado_responsable REAL,
#             nivel_esperado_gerencia REAL,
#             diferencia_responsable REAL,
#             diferencia_gerencia REAL,
#             fecha_evaluacion DATE NOT NULL,
#             FOREIGN KEY (trabajador_id) REFERENCES trabajadores(id)
#         )
#     ''')
#     
#     
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS desglose (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             trabajador_id INTEGER NOT NULL,
#             id_conocimiento INTEGER NOT NULL,
#             conocimiento TEXT NOT NULL,
#             valoracion_responsable REAL,
#             valoracion_gerencia REAL,
#             nivel_esperado_responsable REAL,
#             nivel_esperado_gerencia REAL,
#             diferencia REAL,
#             fecha_evaluacion DATE NOT NULL,
#             FOREIGN KEY (trabajador_id) REFERENCES trabajadores(id)
#         )
#     ''')
# 
#     conn.commit()
#     conn.close()
#     
# 

# In[15]:


def obtener_id_trabajador(nombre, area, puesto):
    conn = sqlite3.connect('base_de_datos.db')
    cursor = conn.cursor()
    
    # Consultar la base de datos para obtener el id del trabajador
    cursor.execute("SELECT id FROM trabajadores WHERE nombre = ? AND puesto = ? AND area = ?", (nombre, puesto, area))
    trabajador_id = cursor.fetchone()  # Devuelve una tupla
    
    conn.close()
    
    # Retornar el id o None si no se encontró
    return trabajador_id[0] if trabajador_id else None



# #Función para crear la tabla de trabajadores
# def crear_tabla_trabajadores():
#     conn = sqlite3.connect('base_de_datos.db')
#     cursor = conn.cursor()
# 
#     # Crear tabla de trabajadores
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS trabajadores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nombre TEXT NOT NULL,
#             apellido1 TEXT NOT NULL,
#             apellido2 TEXT,
#             area TEXT NOT NULL,
#             puesto TEXT NOT NULL,
#             estado TEXT CHECK(estado IN ('activo', 'inactivo')) NOT NULL
#         )
#     ''')
# 
#     conn.commit()
#     conn.close()
#     
# def rellenar_trabajadores(df):
#     conn = conectar_db()
#     df.to_sql('trabajadores', conn, if_exists='append', index=False)
#     conn.close()
# 
# 
# file_path= "VD_HERRAMIENTA POLÍTICA RETRIBUTIVA_GRUPO 3D SOLUTIONS.xlsm"
# t4 = pd.read_excel(file_path, sheet_name='TABLA 4')
# 
# #Crear la tabla en la base de datos
# crear_tabla_trabajadores()
# 
# #Crear un DataFrame vacío con las columnas necesarias
# employees = pd.DataFrame(columns=['nombre', 'apellido1', 'apellido2', 'area', 'puesto', 'estado'])
# 
# #Eliminar filas con valores nulos en la columna 'NOMBRE'
# t4_n = t4.dropna(subset=['NOMBRE'])
# 
# #Rellenar el DataFrame con los datos del CSV
# employees['nombre'] = t4_n['NOMBRE']
# employees['apellido1'] = t4_n['PRIMER APELLIDO']
# employees['apellido2'] = t4_n['SEGUNDO APELLIDO']
# employees['area'] = t4_n['ÁREA']
# employees['puesto'] = t4_n['PUESTO']
# 
# #Asignar el estado 'activo' a todos los empleados
# employees['estado'] = ['activo'] * len(employees)
# 
# #Llamar a la función para insertar los datos en la tabla
# rellenar_trabajadores(employees)
# 

# In[ ]:




