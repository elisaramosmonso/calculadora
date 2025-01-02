#!/usr/bin/env python
# coding: utf-8

# In[13]:




# In[23]:
import pandas as pd
import streamlit as st
import sqlite3
from io import BytesIO
import os
from datetime import datetime



# In[25]:


uploaded_file= "VD_HERRAMIENTA POLÍTICA RETRIBUTIVA_GRUPO 3D SOLUTIONS.xlsm"
archivo_valoraciones= "archivo_valoraciones.csv"

# In[27]:


maestroPersonas= pd.read_excel(uploaded_file, sheet_name='Maestro personas')
PuestoPreg = pd.read_excel(uploaded_file, sheet_name='Puesto-Preguntas')
Resuls = pd.read_excel(uploaded_file, sheet_name='Resultados Objetivo')
archivo_valoraciones= "archivo_valoraciones.csv"
t33 = pd.read_excel(uploaded_file, sheet_name='Tabla3.3')
t4 = pd.read_excel(uploaded_file, sheet_name='TABLA 4')
t22 = pd.read_excel(uploaded_file, sheet_name='tabla 2.2')
t2 = pd.read_excel(uploaded_file, sheet_name='TABLA 2')



# In[33]:
import sqlite3

def vaciar_bd_retribuciones():
    conn = sqlite3.connect('retribuciones.db')
    cursor = conn.cursor()

    # Eliminar todos los registros de la tabla retribuciones
    cursor.execute('DELETE FROM retribuciones')
    cursor.execute('DELETE FROM valoraciones')

    # Confirmar cambios y cerrar la conexión
    conn.commit()
    conn.close()

# Llamar a la función para vaciar la base de datos
#vaciar_bd_retribuciones()

def ver_datos():
    conn= sqlite3.connect('retribuciones.db')
    query = "SELECT * FROM valoraciones"
    dfvaloraciones = pd.read_sql(query, conn)
    conn.close()
    return dfvaloraciones

def ver_datos2():
    conn= sqlite3.connect('retribuciones.db')
    query = "SELECT * FROM retribuciones"
    dfretribuciones = pd.read_sql(query, conn)
    conn.close()
    return dfretribuciones

def conectar_db():
    conn = sqlite3.connect('retribuciones.db')
    return conn
def crear_tablas(): 
    conn = conectar_db() 
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS valoraciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SUPERVISOR TEXT NOT NULL,
            NOMBRE TEXT NOT NULL,
            ÁREA TEXT NOT NULL,
            PUESTO TEXT NOT NULL,
            id_Conocimiento INTEGER NOT NULL,
            PREGUNTA TEXT NOT NULL,
            VALORACIÓN INTEGER NOT NULL,
            fecha_evaluacion TEXT NOT NULL
        )

    ''')
        
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS retribuciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Supervisor TEXT NOT NULL,
    NOMBRE TEXT NOT NULL,
    PUESTO TEXT NOT NULL,
    PROPRET REAL NOT NULL,
    fecha_evaluacion TEXT NOT NULL
)
    ''')
    
    conn.commit()
    conn.close()
crear_tablas()
# Definir diccionario de usuarios y contraseñas
diccUsu_Contra = {"A": "fsa8K", "B": "dfg43P", "C": "htr26J", "admin": "lis23PK"}
def insertar_valoraciones_en_sql(df_valoraciones_actualizadas):
    conn = sqlite3.connect('retribuciones.db')
    cursor = conn.cursor()

    for _, row in df_valoraciones_actualizadas.iterrows():
        cursor.execute('''
            INSERT INTO valoraciones (
                SUPERVISOR,
                NOMBRE,
                ÁREA,
                PUESTO,
                id_Conocimiento,
                PREGUNTA,
                VALORACIÓN,
                fecha_evaluacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['SUPERVISOR'],  
            row['NOMBRE'],
            row['ÁREA'],
            row['PUESTO'],
            row['id_Conocimiento'],
            row['PREGUNTA'],
            row['VALORACIÓN'],
            row['FECHA']
        ))
    conn.commit()
    conn.close()
def insertar_resultados_en_sql(df_resultados):
    conn = sqlite3.connect('retribuciones.db')
    cursor = conn.cursor()

    for _, row in df_resultados.iterrows():
        cursor.execute('''
            INSERT INTO retribuciones (
                Supervisor,
                NOMBRE,
                PUESTO,
                PROPRET,
                fecha_evaluacion
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            row['Supervisor'],  
            row['NOMBRE'],
            row['PUESTO'],
            row['PROPRET'],
            row['FECHA'],
        ))

    conn.commit()
    conn.close()

# Inicializar estado de autenticación
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None  # Almacena el nombre del usuario autenticado

def autenticar_usuario(usuario, contraseña):
    return diccUsu_Contra.get(usuario) == contraseña

# Si está autenticado, continuar con el flujo de la aplicación
if st.session_state.authenticated:
    st.title('CALCULADORA DE RETRIBUCIONES')
    
    df_personas = maestroPersonas
    df_puesto_pregs = PuestoPreg

    # Cargar valoraciones existentes
    if os.path.exists(archivo_valoraciones):
        df_valoraciones_existentes = pd.read_csv(archivo_valoraciones)
    else:
        df_valoraciones_existentes = pd.DataFrame()

    # Obtener el usuario autenticado
    usuario_autenticado = st.session_state.user

    # Filtrar por supervisor o mostrar valoraciones si es administrador
    if usuario_autenticado != "admin":
        df_filtrado = df_personas[df_personas["SUPERVISOR"] == usuario_autenticado]

        if not df_filtrado.empty:
            st.write(f"Nombres a valorar para el supervisor **{usuario_autenticado}**:")

            nombre_seleccionado = st.selectbox("Selecciona una persona a valorar:", df_filtrado["NOMBRE"].unique())

            persona = df_filtrado[df_filtrado["NOMBRE"] == nombre_seleccionado].iloc[0]
            area_persona = persona["ÁREA"]
            puesto_persona = persona["PUESTO"]

            st.write(f"Área: **{area_persona}** | Puesto: **{puesto_persona}**")

            preguntas = df_puesto_pregs[(df_puesto_pregs["ÁREA"] == area_persona) & 
                                        (df_puesto_pregs["PUESTO"] == puesto_persona)]

            if not preguntas.empty:
                st.write("Preguntas a valorar:")

                valoraciones = []
                for _, row in preguntas.iterrows():
                    idcon = row["ID CONOCIMIENTO"]
                    pregunta = row["CONOCIMIENTO"]
                    valoracion = st.slider(f"{pregunta}", 1, 5, 3)
                    valoraciones.append({
                        "SUPERVISOR": usuario_autenticado,
                        "NOMBRE": nombre_seleccionado,
                        "ÁREA": area_persona,
                        "PUESTO": puesto_persona,
                        "id_Conocimiento": idcon,
                        "PREGUNTA": pregunta,
                        "VALORACIÓN": valoracion,
                        "FECHA": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                if st.button("Guardar valoraciones"):
                    
                    # Guardamos las valoraciones nuevas
                    df_nuevas_valoraciones = pd.DataFrame(valoraciones)
                    df_valoraciones_actualizadas = pd.concat([df_valoraciones_existentes, df_nuevas_valoraciones], ignore_index=True)
                    df_valoraciones_actualizadas.to_csv(archivo_valoraciones, index=False)
                    st.success("Valoraciones guardadas correctamente.")
                    df_valoraciones_actualizadas = df_valoraciones_actualizadas.sort_values('FECHA').drop_duplicates(subset=['NOMBRE', 'id_Conocimiento'], keep='last')
                    st.table(df_valoraciones_actualizadas)


                    # Calcular 'propret' para cada persona
                    df_resultados = []
                    
                    tprueb = t2[t2['PUESTO'] == df_valoraciones_actualizadas['PUESTO'].iloc[0]]
                    tprueb2 = tprueb.iloc[:, 5:]
                    tprueb2 = pd.DataFrame(tprueb2)

                    # Definir el orden de los niveles
                    orden = ['N0: Prácticas', 'N1: 6M A 1,5 AÑO', 'N2: 1,5 - 3 AÑO', 'N3: 3 - 5 AÑO',
                             'N1: 5 - 6,5 AÑOS', 'N2: 6,5 - 8 AÑOS', 'N3: 8 - 10 AÑOS',
                             'N1: 10 - 13 AÑOS', 'N2: 13 - 16 AÑOS', 'N3: 16 - 20 AÑOS',
                             'N1: 20 - 24 AÑOS', 'N2: 24 - 30 AÑOS', 'N3: 30 - 38 AÑOS']

                    def find_matching_column(valoracion, df2):
                        for col in tprueb2.columns:
                            if valoracion in tprueb2[col].values:
                                return col
                        return None
                    
                    # nivel
                    df_valoraciones_actualizadas['COINCIDENCIA'] = df_valoraciones_actualizadas['VALORACIÓN'].apply(lambda x: find_matching_column(x, tprueb2))
                    orden_dict = {value: idx for idx, value in enumerate(orden)}
                    df_valoraciones_actualizadas['COINCIDENCIA_ORDEN'] = df_valoraciones_actualizadas['COINCIDENCIA'].map(orden_dict)

                    # Filtrar por el menor nivel de coincidencia para cada persona
                    df_filtrado = df_valoraciones_actualizadas.loc[df_valoraciones_actualizadas.groupby(['SUPERVISOR', 'NOMBRE', 'ÁREA', 'PUESTO', 'FECHA'])['COINCIDENCIA_ORDEN'].idxmin()]

                    for _, row in df_filtrado.iterrows():
                            nivel = row['COINCIDENCIA']
                            nivel_g = nivel
                            puesto = row['PUESTO']  # Asumimos que el puesto está en la fila
                    
                            # t33 para los rangos retributivos
                            bsresp = float(str(t33[(t33['PUESTO'] == puesto) & (t33['Nivel'] == nivel)]['Rango Retributivo'].iloc[0]).replace(',', '.'))
                            bsger = float(str(t33[(t33['PUESTO'] == puesto) & (t33['Nivel'] == nivel_g)]['Rango Retributivo'].iloc[0]).replace(',', '.'))
                            propret = 0.5 * (bsresp + bsger)
                    
                            # Añadir el resultado para esta persona
                            df_resultados.append({
                                'Supervisor': row['SUPERVISOR'],
                                'NOMBRE': row['NOMBRE'],
                                'PUESTO': row['PUESTO'],
                                'PROPRET': propret,
                                "FECHA": row['FECHA']
                            })
                    
                        # Crear DataFrame con los resultados de las retribuciones
                    df_resultados = pd.DataFrame(df_resultados)
                    df_resultados = df_resultados.sort_values('FECHA').drop_duplicates(subset=['NOMBRE'], keep='last')

                    st.table(df_resultados)
                    
                    insertar_valoraciones_en_sql(df_valoraciones_actualizadas)
                    insertar_resultados_en_sql(df_resultados)
                    df_valoraciones_actualizadas = df_valoraciones_actualizadas.sort_values('FECHA').drop_duplicates(subset=['NOMBRE', 'id_Conocimiento'], keep='last')
                    df_resultados = df_resultados.sort_values('FECHA').drop_duplicates(subset=['NOMBRE'], keep='last')
                    df_valoraciones_actualizadas=ver_datos()
                    df_resultados=ver_datos2()
                    st.write("### Valoraciones completas (solo para administrador):")
                    if 'df_valoraciones_actualizadas' in locals() and not df_valoraciones_actualizadas.empty:
                        st.subheader("Valoraciones Actualizadas")
                        st.table(df_valoraciones_actualizadas)
                    else:
                        st.warning("No hay valoraciones actualizadas para mostrar.")
                    
                    # Mostrar resultados
                    if 'df_resultados' in locals() and not df_resultados.empty:
                        st.subheader("Resultados de Retribución")
                        st.table(df_resultados)
                    else:
                        st.warning("No hay resultados de retribución para mostrar.")
            else:
                st.warning(f"No hay preguntas para el área **{area_persona}** y puesto **{puesto_persona}**.")
        else:
            st.warning("No se encontraron nombres para este supervisor.")

    elif usuario_autenticado == "admin":
        df_valoraciones_actualizadas=ver_datos()
        df_resultados=ver_datos2()
        st.write("### Valoraciones completas (solo para administrador):")
        if 'df_valoraciones_actualizadas' in locals() and not df_valoraciones_actualizadas.empty:
            st.subheader("Valoraciones Actualizadas")
            st.table(df_valoraciones_actualizadas)
        else:
            st.warning("No hay valoraciones actualizadas para mostrar.")
        
        # Mostrar resultados
        if 'df_resultados' in locals() and not df_resultados.empty:
            st.subheader("Resultados de Retribución")
            st.table(df_resultados)
        else:
            st.warning("No hay resultados de retribución para mostrar.")
    
    if st.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

else:
    st.title("Iniciar Sesión")
    username_input = st.text_input("Nombre de usuario")
    password_input = st.text_input("Contraseña", type="password")

    if st.button("Acceder"):
        if autenticar_usuario(username_input, password_input):
            st.session_state.authenticated = True
            st.session_state.user = username_input
            st.rerun()  # Recargar para mostrar el contenido protegido
        else:
            st.error("Nombre de usuario o contraseña incorrectos. Intenta de nuevo.")
