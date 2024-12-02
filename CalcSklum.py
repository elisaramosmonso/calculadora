#!/usr/bin/env python
# coding: utf-8

# In[13]:




# In[23]:
import pandas as pd
import streamlit as st
import sqlite3
from io import BytesIO
import os



# In[25]:


uploaded_file= "VD_HERRAMIENTA POLÍTICA RETRIBUTIVA_GRUPO 3D SOLUTIONS.xlsm"
archivo_valoraciones= "archivo_valoraciones.csv"

# In[27]:


maestroPersonas = pd.read_excel(uploaded_file, sheet_name='Maestro personas')
PuestoPreg = pd.read_excel(uploaded_file, sheet_name='Puesto-Preguntas')
Resuls = pd.read_excel(uploaded_file, sheet_name='Resultados Objetivo')




# In[33]:

diccUsu_Contra = {"A": "fsa8K", "B": "dfg43P", "C": "htr26J", "admin": "lis23PK"}

# Inicializar estado de autenticación
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None  # Almacena el nombre del usuario autenticado

# Función de autenticación
def autenticar_usuario(usuario, contraseña):
    return diccUsu_Contra.get(usuario) == contraseña

# Si está autenticado, continuar con el flujo de la aplicación
if st.session_state.authenticated:
    archivo_valoraciones = "valoraciones.csv"
    df_personas = maestroPersonas
    df_puesto_pregs =PuestoPreg

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
                    pregunta = row["CONOCIMIENTO"]
                    valoracion = st.slider(f"{pregunta}", 1, 5, 3)
                    valoraciones.append({
                        "SUPERVISOR": usuario_autenticado,
                        "NOMBRE": nombre_seleccionado,
                        "ÁREA": area_persona,
                        "PUESTO": puesto_persona,
                        "PREGUNTA": pregunta,
                        "VALORACIÓN": valoracion,
                    })

                if st.button("Guardar valoraciones"):
                    df_nuevas_valoraciones = pd.DataFrame(valoraciones)
                    df_valoraciones_actualizadas = pd.concat([df_valoraciones_existentes, df_nuevas_valoraciones], ignore_index=True)
                    df_valoraciones_actualizadas.to_csv(archivo_valoraciones, index=False)
                    st.success("Valoraciones guardadas correctamente.")
            else:
                st.warning(f"No hay preguntas para el área **{area_persona}** y puesto **{puesto_persona}**.")
        else:
            st.warning("No se encontraron nombres para este supervisor.")

    # Mostrar todas las valoraciones si es administrador
    elif usuario_autenticado == "admin":
        st.write("### Valoraciones completas (solo para administrador):")
        st.table(df_valoraciones_existentes)

    # Cerrar sesión
    if st.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.experimental_rerun()

# Formulario de login si no está autenticado
else:
    st.title("Iniciar Sesión")
    username_input = st.text_input("Nombre de usuario")
    password_input = st.text_input("Contraseña", type="password")

    if st.button("Acceder"):
        if autenticar_usuario(username_input, password_input):
            st.session_state.authenticated = True
            st.session_state.user = username_input
            st.experimental_rerun()  # Recargar para mostrar el contenido protegido
        else:
            st.error("Nombre de usuario o contraseña incorrectos. Intenta de nuevo.")
