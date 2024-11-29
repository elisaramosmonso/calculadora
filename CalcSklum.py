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
df_personas = maestroPersonas
df_puesto_pregs = PuestoPreg



# In[33]:

# Filtrar por supervisor
if os.path.exists(archivo_valoraciones):
    df_valoraciones_existentes = pd.read_csv(archivo_valoraciones)
else:
    df_valoraciones_existentes = pd.DataFrame()

# Autenticación del supervisor
supervisor_autenticado = st.text_input("Introduce tu nombre de supervisor:", "")

# Autenticación del administrador
admin_autenticado = st.text_input("Introduce tu nombre de administrador (si eres administrador):", "")

# Filtrar por supervisor
if supervisor_autenticado:
    df_filtrado = df_personas[df_personas["SUPERVISOR"] == supervisor_autenticado]
    
    if not df_filtrado.empty:
        st.write(f"Nombres a valorar para el supervisor **{supervisor_autenticado}**:")
        
        # Selección de persona
        nombre_seleccionado = st.selectbox("Selecciona una persona a valorar:", df_filtrado["NOMBRE"].unique())
        
        # Obtener área y puesto de la persona seleccionada
        persona = df_filtrado[df_filtrado["NOMBRE"] == nombre_seleccionado].iloc[0]
        area_persona = persona["ÁREA"]
        puesto_persona = persona["PUESTO"]
        
        st.write(f"Área: **{area_persona}** | Puesto: **{puesto_persona}**")
        
        # Filtrar preguntas según área y puesto
        preguntas = df_puesto_pregs[
            (df_puesto_pregs["ÁREA"] == area_persona) & 
            (df_puesto_pregs["PUESTO"] == puesto_persona)
        ]
        
        if not preguntas.empty:
            st.write("Preguntas a valorar:")
            
            valoraciones = []
            
            # Mostrar cada pregunta con un slider para valorarla
            for _, row in preguntas.iterrows():
                pregunta = row["CONOCIMIENTO"]
                valoracion = st.slider(f"{pregunta}", 1, 5, 3)
                valoraciones.append({
                    "SUPERVISOR": supervisor_autenticado,
                    "NOMBRE": nombre_seleccionado,
                    "ÁREA": area_persona,
                    "PUESTO": puesto_persona,
                    "PREGUNTA": pregunta,
                    "VALORACIÓN": valoracion,
                })
                
            # Botón para guardar valoraciones
            if st.button("Guardar valoraciones"):
                # Convertir las valoraciones a un DataFrame
                df_nuevas_valoraciones = pd.DataFrame(valoraciones)
                
                # Concatenar las nuevas valoraciones con las anteriores
                df_valoraciones_actualizadas = pd.concat([df_valoraciones_existentes, df_nuevas_valoraciones], ignore_index=True)
                
                # Guardar el DataFrame actualizado en el archivo CSV
                df_valoraciones_actualizadas.to_csv(archivo_valoraciones, index=False)
                st.success("Valoraciones guardadas correctamente.")
                
        else:
            st.warning(f"No hay preguntas para el área **{area_persona}** y puesto **{puesto_persona}**.")
    else:
        st.warning("No se encontraron nombres para este supervisor.")

# Solo el administrador puede ver las valoraciones
if admin_autenticado == "admin":  # Aquí pones el nombre del administrador que quieres autenticar
    st.write("### Valoraciones completas (solo para administrador):")
    st.table(df_valoraciones_actualizadas)  # Aquí se muestran las valoraciones completas
else:
    st.warning("No tienes permisos para ver las valoraciones.")
