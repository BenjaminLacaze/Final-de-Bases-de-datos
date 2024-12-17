
import streamlit as st  
import mysql.connector  
from dotenv import load_dotenv  
import pandas as pd  
import plotly.express as px  
import os  

# Configurar la página de Streamlit
st.set_page_config(
    layout='wide'  
)

# Cargar las credenciales del archivo .env
load_dotenv()

# Obtener las credenciales desde las variables de entorno
db_host = os.getenv('DB_HOST')  
db_user = os.getenv('DB_USER')  
db_password = os.getenv('DB_PASSWORD')  
db_name = os.getenv('DB_NAME')  

# Función para conectar a la base de datos
def conectar_mysql():
    try:
        # Intenta establecer una conexión con los datos proporcionados.
        conexion = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return conexion  # Retorna la conexión si es exitosa.
    except mysql.connector.Error as e:
        # Muestra un mensaje de error en la barra lateral si la conexión falla.
        st.sidebar.error(f"Error de conexión: {e}")
        return None  

# Título de la aplicación en la página principal.
st.title("Ventas de Juegos (1977-2020)")

# Establecer la conexión con la base de datos.
conexion = conectar_mysql()

# Función para ejecutar la primera consulta SQL y devolver los resultados.
def obtener_datos_query1(conexion):
    if conexion is not None:  # Verifica que la conexión esté activa.
        query = """
                SELECT
                    ranking_juego, 
                    nombre_juego, 
                    puntaje_critica, 
                    puntaje_usuario, 
                    total_distribuido, 
                    año_juego, 
                    nombre_plataforma,
                    nombre_editor, 
                    nombre_desarrollador
                FROM juego
                JOIN desarrollador ON desarrollador_juego = ID_desarrollador
                JOIN Plataforma ON plataforma_juego = id_plataforma
                JOIN editor ON editor_juego = id_editor
                ORDER BY juego.ID_juego
        """  # Consulta para obtener ventas y datos relacionados.
        df = pd.read_sql(query, conexion)  # Convierte los resultados en un DataFrame.
        return df
    else:
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay conexión.

#------------------------------------------------------------------------------------------------------------------------------------------------------------#

if conexion:
    data_ventas = obtener_datos_query1(conexion)
    conexion.close()
    
    # Sección de filtros en la barra lateral
    st.sidebar.header("Filtros de juego")  

    filtro_juego = st.sidebar.multiselect("Seleccionar Juego", sorted(data_ventas['nombre_juego'].unique()))
    
    filtro_editor = st.sidebar.multiselect("Seleccionar Editor", sorted(data_ventas['nombre_editor'].unique()))
    
    filtro_desarrollador = st.sidebar.multiselect("Seleccionar Desarrollador", sorted(data_ventas['nombre_desarrollador'].unique()))
    
    filtro_plataforma = st.sidebar.multiselect("Seleccionar plataforma", sorted(data_ventas ["nombre_plataforma"].unique()))

    filtro_año = st.sidebar.multiselect("Seleccionar año", sorted(data_ventas ["año_juego"].unique()))


    # Aplicar los filtros seleccionados
    if filtro_juego:  # Filtra por los juegos seleccionados.
        data_ventas = data_ventas[data_ventas['nombre_juego'].isin(filtro_juego)]
    if filtro_editor:  # Filtra por editores seleccionados.
        data_ventas = data_ventas[data_ventas['nombre_editor'].isin(filtro_editor)]
    if filtro_desarrollador:  # Filtra por desarrolladores seleccionados.
        data_ventas = data_ventas[data_ventas['nombre_desarrollador'].isin(filtro_desarrollador)]
    if filtro_plataforma:  # Filtra por plataformas seleccionadas.
        data_ventas = data_ventas[data_ventas['nombre_plataforma'].isin(filtro_plataforma)]
    if filtro_año: # Filtrar por años seleccionados.
        data_ventas = data_ventas[data_ventas["año_juego"].isin(filtro_año)]

    st.write (data_ventas)

#--------------------------------------------------------------------------------------------------------------------------------------#

    st.write("## indicadores claves de desempeño_(KPIs)_")
    total_venta = data_ventas["total_distribuido"].sum()
    promedio_critica = data_ventas["puntaje_critica"].mean()
    promedio_usuarios = data_ventas["puntaje_usuario"].mean()

    # Divide la página en tres columnas para mostrar los KPIs.
    _col_ventas, _col_puntuacion_critica, _col_puntuacion_usuarios = st.columns([4, 2, 2])

    # Define el estilo CSS para los cuadros de KPIs.
    st.markdown(
        """
        <style>
        .custom-box {
            color: white; /* Color del texto */   
            font-size: 1.3em; /* Tamaño de la letra */
            padding: 0.3em; /* Espacio interno */
            border-radius: 0.3em 0.3em 0em 0em;
            margin-bottom:0.2em;
            font-weight: bold;
        }
        .valor {
            font-size:4em;
            text-align: center;
            border-top: 0.01em solid #A9A9A9;
            border-bottom: 0.01em solid #A9A9A9;
        }
        .general {
            margin: 1em;                
        }
        </style>
        """,
        unsafe_allow_html=True  
    )

#----------------------------------------------------------------------------------------------------------------#

    with _col_ventas:
        cadena_ventas = f"""
            <div class="general">
                <div class = "custom-box", style= "background-color:rgb(193, 0, 0)">
                    Juegos Vendidos:
                </div>
                <div class = "valor">
                {round(total_venta, 2)}M
                </div>
            </div>
        """
        st.markdown(cadena_ventas, unsafe_allow_html=True)

    with _col_puntuacion_critica:
        cadena_ingresos = f"""
            <div class="general">
                <div class = "custom-box", style= "background-color:rgb(0, 104, 26)">
                    Nota promedio de la Critica:
                </div>
                <div class = "valor">
                {round(promedio_critica, 2)}
                </div>
            </div>
        """
        st.markdown(cadena_ingresos, unsafe_allow_html=True)

    with _col_puntuacion_usuarios:
        cadena_promedio = f"""
            <div class="general">
                <div class = "custom-box", style= "background-color:rgb(0, 143, 131)">
                    Nota Promedio de los Usuarios:
                </div>
                <div class = "valor">
                {round(promedio_usuarios,2)}
                </div>
            </div>
        """
        st.markdown(cadena_promedio, unsafe_allow_html=True)


###------------------------------------------------------------------------------------------------------------------


    st.write("## Visualización de Datos")

    # Gráfico 1
    dic_juegos = data_ventas.groupby('nombre_plataforma')['total_distribuido'].sum().to_dict()  
    
    fig1 = px.bar(
            x=dic_juegos.keys(),
            y=dic_juegos.values(),
            title='Ventas por Plataforma',
            color=dic_juegos.values(),
            color_continuous_scale=px.colors.diverging.Geyser,  
            labels={'x': 'Plataforma', 'y': 'Ventas', 'color': 'Cantidad'}
        )
    st.plotly_chart(fig1)  

    #Grafico 2
    dic_juegos2 = data_ventas.groupby('nombre_editor')['total_distribuido'].sum().to_dict()
    
    fig2 = px.bar(
            x=dic_juegos2.keys(),
            y=dic_juegos2.values(),
            title='Ventas por Editor',
            color=dic_juegos2.values(),
            color_continuous_scale=px.colors.diverging.balance_r,  
            labels={'x': 'Editor', 'y': 'Ventas', 'color': 'Cantidad'}
        )
    st.plotly_chart(fig2)
    
    #Grafico 3
    fig3 = px.pie(
            data_ventas,
            names='nombre_editor',
            title='Proporción de juegos por editor'
        )
    st.plotly_chart(fig3)
    
    #Grafico 4
    dic_desarrollador = data_ventas['puntaje_critica'].value_counts().to_dict()
    
    fig4 = px.bar(
            x=(dic_desarrollador.keys()),
            y=dic_desarrollador.values(),
            title = "notas del desarrollador",
            color_continuous_scale=px.colors.diverging.balance,  
            labels={'x': 'Nota', 'y': 'juegos', 'color': 'Cantidad'}
        )
    st.plotly_chart(fig4)



