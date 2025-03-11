import requests
import pandas as pd
import streamlit as st
import zipfile
import io
import os

# descarga de un id (específicamente id600 con filtrado geo_ids=3)
def download_esios_id(id, fecha_ini, fecha_fin, agrupacion):
                       
    cab = dict()
    cab ['x-api-key'] = st.secrets['ESIOS_API_KEY']
    url_id = 'https://api.esios.ree.es/indicators'
    url = f'{url_id}/{id}?geo_ids[]=3&start_date={fecha_ini}T00:00:00&end_date={fecha_fin}T23:59:59&time_trunc={agrupacion}'
    print(url)
    datos_origen = requests.get(url, headers = cab).json()
    
    #arreglamos los datos origen    
    datos =pd.DataFrame(datos_origen['indicator']['values'])
    datos = (datos
        .assign(datetime=lambda vh_: pd #formateamos campo fecha, desde un str con diferencia horaria a un naive
            .to_datetime(vh_['datetime'],utc=True)  # con la fecha local
            .dt
            .tz_convert('Europe/Madrid')
            .dt
            .tz_localize(None)
        )   
        .loc[:,['datetime','value']]
    )
    datos['fecha'] = datos['datetime'].dt.date
    datos['fecha'] = pd.to_datetime(datos['fecha'], format = '%d/%m/%Y')
    datos['año'] = datos['datetime'].dt.year
    datos['mes'] = datos['datetime'].dt.month
    datos['dia'] = datos['datetime'].dt.day
    datos['hora'] = datos['datetime'].dt.hour
    meses_español = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
        7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    datos.rename(columns={'value':'spot'}, inplace=True)
    datos['mes_nombre'] = datos['mes'].map(meses_español)
    #datos = datos['fecha', 'año', 'mes', 'mes_nombre', 'dia', 'hora', 'spot' ]
    datos.set_index('datetime', inplace = True)
    
    return datos

# %%
# 793: RRTT PBF RT3
# 794: RRTT Tiempo Real RT6
# 798: Banda Secundaria BS3
# 799: Desvíos medidos EXD
# 800: Saldo de desvíos DSV
# 802: Saldo P.O.14.6 IN7
# 1285: Control Factor de Potencia CFP
# 1366: Incumplimiento energía de balance BALX
 
# 803: No usado
# 797: No usado
# 1276 SI - No usado



# %%
# descarga de multi-ids (en este caso los ssaa)
def download_esios_ids(indicadores, fecha_inicio, fecha_fin, time_trunc = 'hour'):
      
    # preparamos la cabecera a insertar en la llamada. Vease la necesidad de disponer el token de esios
    cab = dict()
    cab ['x-api-key'] = st.secrets['ESIOS_API_KEY']
    # preparamos la url básica a la que se le añadiran los campos necesarios 
    end_point = 'https://api.esios.ree.es/indicators'
    
    # El procedimiento es sencillo: 
    # a) por cada uno de los indicadores configuraremos la url, según las indicaciones de la documentación.
    # b) Hacemos la llamada y recogemos los datos en formato json.
    # c) Añadimos la información a una lista
    
    lista=[]

    for indicador in indicadores:
        url = f'{end_point}/{indicador}?start_date={fecha_inicio}T00:00:00&end_date={fecha_fin}T23:59:59&time_trunc={time_trunc}'
        print (url)
        response = requests.get(url, headers=cab).json()
        lista.append(pd.json_normalize(data=response['indicator'], record_path=['values'], meta=['id','name','short_name'], errors='ignore'))

    # Devolvemos como salida de la función un df fruto de la concatenación de los elemenos de la lista
    # Este procedimiento, con una sola concatenación al final, es mucho más eficiente que hacer múltiples 
    # concatenaciones.
    
    return pd.concat(lista, ignore_index=True )

def generar_datos(fecha_ini, fecha_fin):
    
    # descargamos el spot
    df_datos_spot = download_esios_id('600', fecha_ini, fecha_fin, 'hour')
    # leemos el fichero de periodos horarios
    df_periodos = pd.read_excel('periodos_horarios.xlsx', parse_dates = ['fecha'])
    df_periodos['fecha'] = pd.to_datetime(df_periodos['fecha'], format = '%d/%m/%Y', errors = 'coerce')
    # combinamos añadiendo dh3p y dh6p
    df_datos = df_datos_spot.copy()
    df_datos = df_datos.merge(df_periodos[['fecha', 'hora', 'dh_3p', 'dh_6p']], on = ['fecha', 'hora'], how = 'left')
    orden_col = ['fecha', 'año', 'mes', 'mes_nombre', 'dia', 'hora', 'dh_3p', 'dh_6p', 'spot']
    df_datos = df_datos[orden_col]
    # descargamos los ssaa
    ids_ssaa = [793, 794, 798, 799, 800, 802, 1285, 1366]
    df_ssaa_origen = download_esios_ids(ids_ssaa, fecha_ini, fecha_fin, 'hour' )

    if not df_ssaa_origen.empty:
        df_ssaa = (df_ssaa_origen
            .assign(datetime=lambda vh_: pd #formateamos campo fecha, desde un str con diferencia horaria a un naive
                .to_datetime(vh_['datetime'],utc=True)  # con la fecha local
                .dt
                .tz_convert('Europe/Madrid')
                .dt
                .tz_localize(None)
            )   
            .loc[:,['datetime','value', 'id']]
        )
        df_ssaa['fecha'] = df_ssaa['datetime'].dt.date
        df_ssaa['fecha'] = pd.to_datetime(df_ssaa['fecha'], format = '%d/%m/%Y')
        df_ssaa['hora'] = df_ssaa['datetime'].dt.hour
        # combinamos con el df de datos añadiendo los ssaa
        df_ssaa = df_ssaa.copy()
        df_ssaa = df_ssaa.groupby(['fecha', 'hora'], as_index=False)['value'].sum()
        print('df_ssaa cuando hay datos')
        print(df_ssaa)
        # Reemplazar NaN con 0 después de agrupar
        #df_ssaa['value'] = df_ssaa['value'].fillna(0).round(2)
    else:
        # Generar un DataFrame con fechas y horas del rango solicitado
        fecha_rango = pd.date_range(start=fecha_ini, end=fecha_fin, freq='H')  # Rango horario
        df_ssaa = pd.DataFrame({
            'fecha': fecha_rango.date,
            'hora': fecha_rango.hour,
            'value': 0  # Todos los valores en cero
        })
        df_ssaa['fecha'] = pd.to_datetime(df_ssaa['fecha'])
        print('df_ssaa cuando NO hay datos')
        print(df_ssaa)
    #fechas = pd.date_range(start=fecha_ini, end=fecha_fin, freq='D')
    #horas = range(24)
    #df_completo = pd.DataFrame([(f, h) for f in fechas for h in horas], columns=['fecha', 'hora', 'ssaa'])
    #df_ssaa = df_completo.merge(df_ssaa, on=['fecha', 'hora', 'ssaa'], how='left')
    #df_datos['ssaa'] = df_datos['ssaa'].fillna(0).round(2)
    df_datos['fecha'] = pd.to_datetime(df_datos['fecha'])

    df_ssaa.rename(columns = {'value' : 'ssaa'}, inplace = True)
    df_datos = df_datos.merge(df_ssaa[['fecha', 'hora', 'ssaa']], on = ['fecha', 'hora'], how = 'left')
    df_datos['ssaa'] = df_datos['ssaa'].fillna(0).round(2)

    df_datos = df_datos.copy()

    # Cargar todas las tablas del archivo (incluyendo nombres de tablas definidas en Excel)
    file_path = "004 LUZ componentes regulados.xlsx"
    # Cargar todas las hojas
    sheets_dict = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")

    # Crear un diccionario con todas las tablas identificadas
    tablas = {sheet_name: df for sheet_name, df in sheets_dict.items()}

    # Acceder a cualquier tabla por su nombre de hoja
    df_ppcc = tablas["PPCC"]
    df_osom = tablas['OSOM']
    df_perdidas_boe = tablas['PERDIDAS']
    df_pycs_energia = tablas['PYC_E']
    df_datos['ppcc_2.0'] = None
    for _, row in df_ppcc.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"]) & (df_datos["dh_3p"] == row["periodo"])
        df_datos.loc[mask, "ppcc_2.0"] = row["2.0TD"]
    df_datos['ppcc_3.0'] = None
    for _, row in df_ppcc.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"]) & (df_datos["dh_6p"] == row["periodo"])
        df_datos.loc[mask, "ppcc_3.0"] = row["3.0TD"]
    df_datos['ppcc_6.1'] = None    
    for _, row in df_ppcc.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"]) & (df_datos["dh_6p"] == row["periodo"])
        df_datos.loc[mask, "ppcc_6.1"] = row["6.1TD"]  
    df_datos[['ppcc_2.0', 'ppcc_3.0', 'ppcc_6.1']] *= 1000
    df_datos = df_datos.copy()
    df_datos['osom'] = None
    for _, row in df_osom.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"])
        df_datos.loc[mask, "osom"] = row["osom"]
    df_datos['otros'] = 3.7
    # Asignar la columna perd_2.0_boe a df_datos según el periodo dh_3p
    df_datos["perd_2.0_boe"] = df_datos["dh_3p"].map(df_perdidas_boe.set_index("periodo")["2.0TD"])
    df_datos["perd_3.0_boe"] = df_datos["dh_6p"].map(df_perdidas_boe.set_index("periodo")["3.0TD"])
    df_datos["perd_6.1_boe"] = df_datos["dh_6p"].map(df_perdidas_boe.set_index("periodo")["6.1TD"])

    #COEFICIENTES COEFK-----------------------
    extract_folder_coefk = "coef_kest_data"
    # Listar los archivos `.xls` en la carpeta
    xls_files = [f for f in os.listdir(extract_folder_coefk) if f.endswith(".xls")]
    # Lista para almacenar los DataFrames
    df_list = []
    # Leer cada archivo y almacenarlo en la lista
    for file in xls_files:
        file_path = os.path.join(extract_folder_coefk, file)
        # Leer el archivo Excel
        df = pd.read_excel(file_path, skiprows=4)  # Cargar todas las hojas
        # Eliminar las filas vacías al final
        df = df.dropna(how='all')
        # Eliminar las columnas: primera, tercera y cuarta (índices 0, 2, 3)
        df = df.drop(df.columns[[0, 2, 3]], axis=1)
        # Asegurar que no haya columnas extra manteniendo solo las primeras 25 (1 de fecha + 24 de horas)
        if df.shape[1] > 25:
            df = df.iloc[:, :25]
        # Renombrar columnas
        df.columns = ['fecha'] + list(range(24))
        df_list.append(df)

    # Concatenar todos los archivos en un solo DataFrame
    df_coefk = pd.concat(df_list, ignore_index = True)
    df_coefk['fecha'] = pd.to_datetime(df_coefk['fecha'], dayfirst=True)

    # Opcional: Guardar en CSV
    df_coefk.to_csv("COEF_KEST_MM_Combinado.csv", index = False, sep = ";")
    print("📁 Archivo guardado: COEF_KEST_MM_Combinado.csv")
    df_datos = df_datos.copy()
    df_coefk.columns = df_coefk.columns.astype(str)
    df_datos = df_datos.merge(df_coefk, on='fecha', how='left')
    # Extraer el coeficiente correspondiente a la columna de la hora
    df_datos['coef_k'] = df_datos.apply(lambda row: row[str(row['hora'])], axis=1)
    columnas_horas = [str(h) for h in range(24)]  # Generamos la lista de nombres de columnas de horas
    df_datos.drop(columns = columnas_horas, inplace = True)

    df_datos = df_datos.copy()
    df_datos['perd_2.0'] = df_datos['perd_2.0_boe'] * df_datos['coef_k']
    df_datos['perd_3.0'] = df_datos['perd_3.0_boe'] * df_datos['coef_k']
    df_datos['perd_6.1'] = df_datos['perd_6.1_boe'] * df_datos['coef_k']
    df_datos['coste_2.0'] = (df_datos['spot'] + df_datos['ssaa'] + df_datos['osom'] + df_datos['ppcc_2.0'] + df_datos['otros']) * 1.015 * (1 + df_datos['perd_2.0'])
    df_datos['coste_3.0'] = (df_datos['spot'] + df_datos['ssaa'] + df_datos['osom'] + df_datos['ppcc_3.0'] + df_datos['otros']) * 1.015 * (1 + df_datos['perd_3.0'])
    df_datos['coste_6.1'] = (df_datos['spot'] + df_datos['ssaa'] + df_datos['osom'] + df_datos['ppcc_6.1'] + df_datos['otros']) * 1.015 * (1 + df_datos['perd_6.1'])

    df_datos['pyc_2.0'] = None
    for _, row in df_pycs_energia.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"]) & (df_datos["dh_3p"] == row["periodo"])
        df_datos.loc[mask, "pyc_2.0"] = row["2.0TD"]
    df_datos['pyc_3.0'] = None
    for _, row in df_pycs_energia.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"]) & (df_datos["dh_6p"] == row["periodo"])
        df_datos.loc[mask, "pyc_3.0"] = row["3.0TD"]
    df_datos['pyc_6.1'] = None    
    for _, row in df_pycs_energia.iterrows():
        mask = (df_datos["fecha"] >= row["fecha_inicio"]) & (df_datos["fecha"] <= row["fecha_final"]) & (df_datos["dh_6p"] == row["periodo"])
        df_datos.loc[mask, "pyc_6.1"] = row["6.1TD"]  
    df_datos[['pyc_2.0', 'pyc_3.0', 'pyc_6.1']] *= 1000

    df_datos['precio_2.0'] = df_datos['coste_2.0'] + df_datos['pyc_2.0']
    df_datos['precio_3.0'] = df_datos['coste_3.0'] + df_datos['pyc_3.0']
    df_datos['precio_6.1'] = df_datos['coste_6.1'] + df_datos['pyc_6.1']

    return df_datos

# %%



