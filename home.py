import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static,st_folium
#from car_downloader import baixar_car
from zona_utm import calcular_utm


#Streamlit -> framework de desenvolvimento de dashboards interactivos
#Plotly -> biblioteca de plotagem de gráficos
#Folium -> biblioiteca de confecção de mapas
#Streamlmit folium -> biblioiteca de interaçãço do streamlit com o folium

#Funções de disposiçãço dos elementos na tela
st.header('Análise Dinamizada dos Dados do CAR',divider="gray")
#st.write('Este dashboard permite verificar a existência de sobreposições dos dados declarados no Cadastro Ambiental Rural - CAR com determinado polígono de interesse.')
st.write('')
st.write('')
st.sidebar.title('Menu')

desmatamento = 'date/desmatamento/alerts_mapbiomas.parquet'
aimovel = 'date/area_imovel/area_imovel.parquet'
reslegal = 'date/reserva_legal/reserva_legal.parquet'
apps = 'date/apps/apps.parquet'
hidrografia = 'date/hidrografia/hidrografia.parquet'

#Upload de arquivo
arquivo_subido = st.sidebar.file_uploader(label='Selecione um arquivo a ser analisado: ')

compacto = st.sidebar.checkbox(label='Ativar Modo Compacto')


if arquivo_subido:
   poligono_analise = gpd.read_file(arquivo_subido)

   epsg = calcular_utm(poligono_analise)

#Checagem para saber se o arquivo foi subido:
if arquivo_subido and not compacto:

    #Elemento de seleção da visualização
    elemento = st.sidebar.radio('Selecione o elemento a ser visualizado: ',
                        options=['Mapa','Gráfico','Resumo','Cabeçalho'])


#Leitura de arquivo na forma de geodataframe    
    gdf = poligono_analise

       
   #gdf = gdf.drop(columns=['detected_a','published_','image_afte','image_befo'])
    
    @st.cache_resource
    def abrir_desmatamento():
        gdf_desmat = gpd.read_parquet(desmatamento)
        return gdf_desmat
    
    @st.cache_resource
    def abrir_aimovel():
        gdf_imovel = gpd.read_parquet(aimovel)
        return gdf_imovel
    
    @st.cache_resource
    def abrir_reslegal():
        gdf_rlegal = gpd.read_parquet(reslegal)
        return gdf_rlegal
    
    @st.cache_resource
    def abrir_apps():
        gdf_app = gpd.read_parquet(apps)
        return gdf_app
    
    @st.cache_resource
    def abrir_hidrografia():
        gdf_hidro = gpd.read_parquet(hidrografia)
        return gdf_hidro
    
    gdf_desmat = abrir_desmatamento()

    gdf_imovel = abrir_aimovel()

    gdf_rlegal = abrir_reslegal()

    gdf_app = abrir_apps()

    gdf_hidro = abrir_hidrografia()    

    gdf_desmat = gdf_desmat.drop(columns=['ANODETEC','DATADETEC','DTIMGANT','DTIMGDEP','DTPUBLI'])

   # st.write(gdf.head())

    entrada_desmat = gpd.sjoin(gdf_desmat,gdf,how='inner',predicate='intersects')

    entrada_imovel = gpd.sjoin(gdf_imovel,gdf,how='inner',predicate='intersects')

    entrada_rlegal = gpd.sjoin(gdf_rlegal,gdf,how='inner',predicate='intersects')

    entrada_app = gpd.sjoin(gdf_app,gdf,how='inner',predicate='intersects')

    entrada_hidro = gpd.sjoin(gdf_hidro,gdf,how='inner',predicate='intersects')


    #Conversão do geodataframe em dataframe    
    df_desmat = pd.DataFrame(entrada_desmat).drop(columns=['geometry'])
    
    df_imovel = pd.DataFrame(entrada_imovel).drop(columns=['geometry'])
    
    df_rlegal = pd.DataFrame(entrada_rlegal).drop(columns=['geometry'])
    
    df_app = pd.DataFrame(entrada_app).drop(columns=['geometry'])
    
    df_hidro = pd.DataFrame(entrada_hidro).drop(columns=['geometry']) 
       
      

#Criar funções para separar os elementos
    def resumo():
        #divisão de colunas para melhor visualização
        col1,col2 = st.columns(2)

        with col1:
            st.subheader('Dados de Desmatamento')
            st.dataframe(df_desmat,height=320)
            st.subheader('Dados do Imóvel')
            st.dataframe(df_imovel,height=320)
            st.subheader('Dados de Reserva Legal')
            st.dataframe(df_rlegal,height=320)
            st.subheader('Dados de Apps')
            st.dataframe(df_app,height=320)
            st.subheader('Dados de Hidrografia')
            st.dataframe(df_hidro,height=320)

        with col2:
            st.subheader('')
            st.dataframe(df_desmat.describe(),height=320)
            st.subheader('')
            st.dataframe(df_imovel.describe(),height=320)
            st.subheader('')
            st.dataframe(df_rlegal.describe(),height=320)
            st.subheader('')
            st.dataframe(df_app.describe(),height=320)
            st.subheader('')
            st.dataframe(df_hidro.describe(),height=320)

    def cabecalho(): 
        st.subheader('Dados de Desmatamento')      
        st.dataframe(df_desmat)
        st.subheader('Dados do Imóvel')
        st.dataframe(df_imovel)
        st.subheader('Dados de Reserva Legal')
        st.dataframe(df_rlegal)
        st.subheader('Dados de APPs')
        st.dataframe(df_app)
        st.subheader('Dados de Hidrografia')
        st.dataframe(df_hidro)

    def grafico():  
        col1_gra,col2_gra,col3_gra,col4_gra = st.columns(4)

#Seleção do tipo grafico e um opção padrao (index)
        tema_grafico = col1_gra.selectbox('Selecione o tema do gráfico:',
                        options=['Desmatamento','Área do Imóvel','Reserva Legal','APPs','Hidrografia'],index=1)
        
        if tema_grafico == "Desmatamento":
            df_analisado = df_desmat
        elif tema_grafico == 'Área do Imóvel':
                df_analisado = df_imovel
        elif tema_grafico == 'Reserva Legal':
                df_analisado = df_rlegal
        elif tema_grafico == 'APPs':
            df_analisado = df_app
        elif tema_grafico == 'Hidrografia':
            df_analisado = df_hidro
        

        tipo_grafico = col2_gra.selectbox('Selecione o tipo de gráfico:',
                        options=['box','bar','line','scatter','violin','histogram'],index=5)

#plotagem de função utilizando o plotly express
        plot_func = getattr(px, tipo_grafico)

#Criação de opções dos eixos x e y com uma opção padrão
        x_val = col3_gra.selectbox('Selecione o eixo x:',options=df_analisado.columns,index=1)

        y_val = col4_gra.selectbox('Selecione o eixo y:',options=df_analisado.columns,index=1)

#Criação plotagem do gráfico
        plot = plot_func(df_analisado,x=x_val,y=y_val)
#Faço a plotagem
        st.plotly_chart(plot, use_container_width=True)

    def mapa():
#Crio um mapa e seleciono algumas opções
        m = folium.Map(location=[-7,-38],zoom_start=6,control_scale=True,tiles='Esri World Imagery')

        def style_function_entrada(x): return{
            'fillColor': '#8B008B',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8
        }

        def style_function_desmat(x): return{
            'fillColor': '#FF0000',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }

        def style_function_imovel(x): return{
            'fillColor': '#808080',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8           
        }

        def style_function_rlegal(x): return{
            'fillColor': '#006400',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }

        def style_function_app(x): return{
            'fillColor': '#FFD700',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }

        def style_function_hidro(x): return{
            'fillColor': '#0000FF',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }
        
        
#Plotagem do geodataframe no mapa deforma que qualquer arquivo seja subido
        entrada_imovel_limpo = gpd.GeoDataFrame(entrada_imovel,columns=['geometry'])
        folium.GeoJson(entrada_imovel_limpo,name='Área Imóvel',style_function=style_function_imovel).add_to(m) 
             
        entrada_desmat_limpo = gpd.GeoDataFrame(entrada_desmat,columns=['geometry'])
        folium.GeoJson(entrada_desmat_limpo,name='Desmatamento',style_function=style_function_desmat).add_to(m)    

        entrada_hidro_limpo = gpd.GeoDataFrame(entrada_hidro,columns=['geometry'])
        folium.GeoJson(entrada_hidro_limpo,name='Hidrografia',style_function=style_function_hidro).add_to(m)
        
        entrada_rlegal_limpo = gpd.GeoDataFrame(entrada_rlegal,columns=['geometry'])
        folium.GeoJson(entrada_rlegal_limpo,name='Reserva Legal',style_function=style_function_rlegal).add_to(m)

        entrada_app_limpo = gpd.GeoDataFrame(entrada_app,columns=['geometry'])
        folium.GeoJson(entrada_app_limpo,name='APPs',style_function=style_function_app).add_to(m)
       
        gdf_limpo = gpd.GeoDataFrame(gdf,columns=['geometry'])
        folium.GeoJson(gdf_limpo,name='Área Analisada',style_function=style_function_entrada).add_to(m)
        
   
#Calculo o limite eda geometria 
        bounds = gdf.total_bounds

#ajusto o mapa para os limites da geometria
        m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])

#Adiciono controles de camadas ao mapa
        folium.LayerControl().add_to(m)

#Plotagem do mapa no dashboard
        st_folium(m,width="100%")

    #Condional para mostrar os elementos na tela
    if elemento == 'Cabeçalho':
        cabecalho()
    elif elemento == 'Resumo':
        resumo()
    elif elemento == 'Gráfico':
        grafico()
    elif elemento == 'Mapa':
        mapa()

elif arquivo_subido and compacto:

    #Leitura de arquivo na forma de geodataframe    
    gdf = poligono_analise

       
   #gdf = gdf.drop(columns=['detected_a','published_','image_afte','image_befo'])
    
    @st.cache_resource
    def abrir_desmatamento():
        gdf_desmat = gpd.read_parquet(desmatamento)
        return gdf_desmat
    
    @st.cache_resource
    def abrir_aimovel():
        gdf_imovel = gpd.read_parquet(aimovel)
        return gdf_imovel
    
    @st.cache_resource
    def abrir_reslegal():
        gdf_rlegal = gpd.read_parquet(reslegal)
        return gdf_rlegal
    
    @st.cache_resource
    def abrir_apps():
        gdf_app = gpd.read_parquet(apps)
        return gdf_app
    
    @st.cache_resource
    def abrir_hidrografia():
        gdf_hidro = gpd.read_parquet(hidrografia)
        return gdf_hidro
    
    gdf_desmat = abrir_desmatamento()

    gdf_imovel = abrir_aimovel()

    gdf_rlegal = abrir_reslegal()

    gdf_app = abrir_apps()

    gdf_hidro = abrir_hidrografia()    

    gdf_desmat = gdf_desmat.drop(columns=['ANODETEC','DATADETEC','DTIMGANT','DTIMGDEP','DTPUBLI'])

   # st.write(gdf.head())

    entrada_desmat = gpd.sjoin(gdf_desmat,gdf,how='inner',predicate='intersects')
    entrada_desmat = gpd.overlay(entrada_desmat,gdf,how='intersection')

    entrada_imovel = gpd.sjoin(gdf_imovel,gdf,how='inner',predicate='intersects')
    entrada_imovel = gpd.overlay(entrada_imovel,gdf,how='intersection')

    entrada_rlegal = gpd.sjoin(gdf_rlegal,gdf,how='inner',predicate='intersects')
    entrada_rlegal = gpd.overlay(entrada_rlegal,gdf,how='intersection')

    entrada_app = gpd.sjoin(gdf_app,gdf,how='inner',predicate='intersects')
    entrada_app = gpd.overlay(entrada_app,gdf,how='intersection')

    entrada_hidro = gpd.sjoin(gdf_hidro,gdf,how='inner',predicate='intersects')
    entrada_hidro = gpd.overlay(entrada_hidro,gdf,how='intersection')

    #Conversão do geodataframe em dataframe    
    df_desmat = pd.DataFrame(entrada_desmat).drop(columns=['geometry'])
    
    df_imovel = pd.DataFrame(entrada_imovel).drop(columns=['geometry'])
    
    df_rlegal = pd.DataFrame(entrada_rlegal).drop(columns=['geometry'])
    
    df_app = pd.DataFrame(entrada_app).drop(columns=['geometry'])
    
    df_hidro = pd.DataFrame(entrada_hidro).drop(columns=['geometry'])        
    
    area_desmat = entrada_desmat.dissolve(by=None)
    area_desmat = area_desmat.to_crs(epsg=epsg)
    area_desmat['area'] = area_desmat.area / 10000

    area_imovel = entrada_imovel.dissolve(by=None)
    area_imovel = area_imovel.to_crs(epsg=epsg)
    area_imovel['area'] = area_imovel.area / 10000
    
    area_rlegal = entrada_rlegal.dissolve(by=None)
    area_rlegal = area_rlegal.to_crs(epsg=epsg)
    area_rlegal['area'] = area_rlegal.area / 10000

    area_app = entrada_app.dissolve(by=None)
    area_app = area_app.to_crs(epsg=epsg)
    area_app['area'] = area_app.area / 10000

    area_hidro = entrada_hidro.dissolve(by=None)
    area_hidro = area_hidro.to_crs(epsg=epsg)
    area_hidro['area'] = area_hidro.area / 10000

    card_columns1,card_columns2,card_columns3,card_columns4,card_columns5 = st.columns(5)

    with card_columns1:
        st.subheader('Área Desmatada (ha)')
        if len(area_desmat) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_desmat.loc[0,'area'],3)))
    
    with card_columns2:
        st.subheader('Área Imóvel (ha)')
        if len(area_imovel) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_imovel.loc[0,'area'],3)))

    with card_columns3:
        st.subheader('Área Res. Legal (ha)')
        if len(area_rlegal) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_rlegal.loc[0,'area'],3)))
    
    with card_columns4:
        st.subheader('Área APPs (ha)')
        if len(area_app) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_app.loc[0,'area'],3)))

    with card_columns5:
        st.subheader('Área Hidrografia (ha)')
        if len(area_hidro) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_hidro.loc[0,'area'],3)))

    col1_graf,col2_graf,col3_graf,col4_graf = st.columns(4)
    
    tema_grafico = col1_graf.selectbox('Selecione o tema do gráfico:',
                        options=['Desmatamento','Área do Imóvel','Reserva Legal','APPs','Hidrografia'],index=1)
        
    if tema_grafico == "Desmatamento":
        df_analisado = df_desmat
    elif tema_grafico == 'Área do Imóvel':
        df_analisado = df_imovel
    elif tema_grafico == 'Reserva Legal':
        df_analisado = df_rlegal
    elif tema_grafico == 'APPs':
        df_analisado = df_app
    elif tema_grafico == 'Hidrografia':
        df_analisado = df_hidro

    tipo_grafico = col2_graf.selectbox('Selecione o tipo de gráfico:',
                options=['box','bar','line','scatter','violin','histogram'],index=5)
    
    #plotagem de função utilizando o plotly express
    plot_func = getattr(px, tipo_grafico)

#Criação de opções dos eixos x e y com uma opção padrão
    x_val = col3_graf.selectbox('Selecione o eixo x:',options=df_analisado.columns,index=1)

    y_val = col4_graf.selectbox('Selecione o eixo y:',options=df_analisado.columns,index=1)

#Criação plotagem do gráfico
    plot = plot_func(df_analisado,x=x_val,y=y_val)
#Faço a plotagem
    st.plotly_chart(plot, use_container_width=True)


#Crio um mapa e seleciono algumas opções
    m = folium.Map(location=[-7,-38],zoom_start=6,control_scale=True,tiles='Esri World Imagery')

    def style_function_entrada(x): return{
            'fillColor': '#8B008B',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8
        }

    def style_function_desmat(x): return{
            'fillColor': '#FF0000',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }

    def style_function_imovel(x): return{
            'fillColor': '#808080',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8           
        }

    def style_function_rlegal(x): return{
            'fillColor': '#006400',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }

    def style_function_app(x): return{
            'fillColor': '#FFD700',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }

    def style_function_hidro(x): return{
            'fillColor': '#0000FF',
            'color': 'black',
            'weight': 1,
            'fillOpacity':0.8            
        }
        
        
#Plotagem do geodataframe no mapa deforma que qualquer arquivo seja subido
    entrada_imovel_limpo = gpd.GeoDataFrame(entrada_imovel,columns=['geometry'])
    folium.GeoJson(entrada_imovel_limpo,name='Área Imóvel',style_function=style_function_imovel).add_to(m) 
             
    entrada_desmat_limpo = gpd.GeoDataFrame(entrada_desmat,columns=['geometry'])
    folium.GeoJson(entrada_desmat_limpo,name='Desmatamento',style_function=style_function_desmat).add_to(m)    

    entrada_hidro_limpo = gpd.GeoDataFrame(entrada_hidro,columns=['geometry'])
    folium.GeoJson(entrada_hidro_limpo,name='Hidrografia',style_function=style_function_hidro).add_to(m)
        
    entrada_rlegal_limpo = gpd.GeoDataFrame(entrada_rlegal,columns=['geometry'])
    folium.GeoJson(entrada_rlegal_limpo,name='Reserva Legal',style_function=style_function_rlegal).add_to(m)

    entrada_app_limpo = gpd.GeoDataFrame(entrada_app,columns=['geometry'])
    folium.GeoJson(entrada_app_limpo,name='APPs',style_function=style_function_app).add_to(m)
       
    gdf_limpo = gpd.GeoDataFrame(gdf,columns=['geometry'])
    folium.GeoJson(gdf_limpo,name='Área Analisada',style_function=style_function_entrada).add_to(m)  
  
#Calculo o limite eda geometria 
    bounds = gdf.total_bounds

#ajusto o mapa para os limites da geometria
    m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])

#Adiciono controles de camadas ao mapa
    folium.LayerControl().add_to(m)

#Plotagem do mapa no dashboard
    st_folium(m,width="100%")



        
        

    


else:
    st.warning('Selecione um arquivo para iniciar o dashboard:')




