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

# Definir diccionario de usuarios y contraseñas
diccUsu_Contra = {"A": "fsa8K", "B": "dfg43P", "C": "htr26J", "admin": "lis23PK"}

# Inicializar estado de autenticación
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None  # Almacena el nombre del usuario autenticado

def autenticar_usuario(usuario, contraseña):
    return diccUsu_Contra.get(usuario) == contraseña

# Si está autenticado, continuar con el flujo de la aplicación
if st.session_state.authenticated:
    st.title('CALCULADORA DE RETRIBUCIONES')
    archivo_valoraciones = "valoraciones.csv"
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

                # Aquí entra el código que calculó 'propret' con la lógica que mencionaste
                if st.button("Guardar valoraciones"):
                    # Guardamos las valoraciones nuevas
                    df_nuevas_valoraciones = pd.DataFrame(valoraciones)
                    df_valoraciones_actualizadas = pd.concat([df_valoraciones_existentes, df_nuevas_valoraciones], ignore_index=True)
                    df_valoraciones_actualizadas.to_csv(archivo_valoraciones, index=False)
                    st.success("Valoraciones guardadas correctamente.")

                    # Calcular 'propret' para cada persona
                    df_resultados = []
                    
                    # Cargar DataFrame 't2' que se necesita para encontrar las columnas relacionadas con las valoraciones
                    tprueb = t2[t2['PUESTO'] == df_valoraciones_actualizadas['PUESTO'].iloc[0]]
                    tprueb2 = tprueb.iloc[:, 5:]
                    tprueb2 = pd.DataFrame(tprueb2)

                    # Definir el orden de los niveles
                    orden = ['N0: Prácticas', 'N1: 6M A 1,5 AÑO', 'N2: 1,5 - 3 AÑO', 'N3: 3 - 5 AÑO',
                             'N1: 5 - 6,5 AÑOS', 'N2: 6,5 - 8 AÑOS', 'N3: 8 - 10 AÑOS',
                             'N1: 10 - 13 AÑOS', 'N2: 13 - 16 AÑOS', 'N3: 16 - 20 AÑOS',
                             'N1: 20 - 24 AÑOS', 'N2: 24 - 30 AÑOS', 'N3: 30 - 38 AÑOS']

                    # Función para encontrar la columna que coincida con el valor de la valoración
                    def find_matching_column(valoracion, df2):
                        for col in tprueb2.columns:
                            if valoracion in tprueb2[col].values:
                                return col
                        return None
                    
                    # Buscar la coincidencia de nivel
                    df_valoraciones_actualizadas['COINCIDENCIA'] = df_valoraciones_actualizadas['VALORACIÓN'].apply(lambda x: find_matching_column(x, tprueb2))
                    orden_dict = {value: idx for idx, value in enumerate(orden)}
                    df_valoraciones_actualizadas['COINCIDENCIA_ORDEN'] = df_valoraciones_actualizadas['COINCIDENCIA'].map(orden_dict)

                    # Filtrar por el menor nivel de coincidencia para cada persona
                    df_filtrado = df_valoraciones_actualizadas.loc[df_valoraciones_actualizadas.groupby(['SUPERVISOR', 'NOMBRE', 'ÁREA', 'PUESTO'])['COINCIDENCIA_ORDEN'].idxmin()]
                    nivel = df_filtrado['COINCIDENCIA'].values[0]
                    nivel_g = nivel
                    puesto = "T.IMPRESIÓN_3D"  # Suponemos que es este el puesto que queremos calcular

                    # Cargar DataFrame t33 para los rangos retributivos
                    bsresp = float(str(t33[(t33['PUESTO'] == puesto) & (t33['Nivel'] == nivel)]['Rango Retributivo'].iloc[0]).replace(',', '.'))
                    bsger = float(str(t33[(t33['PUESTO'] == puesto) & (t33['Nivel'] == nivel_g)]['Rango Retributivo'].iloc[0]).replace(',', '.'))
                    propret = 0.5 * (bsresp + bsger)

                    # Añadir el resultado al DataFrame de resultados
                    df_resultados.append({
                        'NOMBRE': df_filtrado['NOMBRE'].values[0],
                        'PUESTO': puesto,
                        'PROPRET': propret
                    })

                    # Crear DataFrame con los resultados de las retribuciones
                    df_resultados = pd.DataFrame(df_resultados)
                    st.write("### Resultados de la retribución calculada:")
                    st.table(df_resultados)

            else:
                st.warning(f"No hay preguntas para el área **{area_persona}** y puesto **{puesto_persona}**.")
        else:
            st.warning("No se encontraron nombres para este supervisor.")

    # Mostrar todas las valoraciones si es administrador
    elif usuario_autenticado == "admin":
        st.write("### Valoraciones completas (solo para administrador):")
        st.table(df_valoraciones_existentes)

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
