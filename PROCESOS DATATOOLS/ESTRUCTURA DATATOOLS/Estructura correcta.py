
# coding: utf-8

# In[1]:


#importar pandas
import pandas as pd
import MySQLdb
import pandas as pd
from datetime import datetime,timedelta
import random


# In[2]:


import numpy as np


# In[3]:


db = MySQLdb.connect(host="172.18.55.6",    # tu host, usualmente localhost
                     user="comandato",         # tu usuario
                     passwd="comandato123",  # tu password
                     db="SISTEMECUADOR_ATM")        # el nombre de la base de datos


# In[4]:


day='5'
day2='XX'


# In[5]:


multas=""" SELECT Cedula,Segmento   FROM SISTEMECUADOR_ATM.MULTAS_MENSUALES where Mes=3 group by Cedula"""
resultado_multas=pd.read_sql(multas, con=db)


# In[6]:


resultado_multas['NRO_IDENTIFICACION_CLIENTE']='0'+resultado_multas['Cedula']


# In[7]:


consulta=""" SELECT
    COD_AGENTE,
    if(RESPUESTA_OBTENIDA in ('ACUERDO DE PAGO','ACUERDO DE CONVENIO'),2,1) as TIPO_GESTION,
    NRO_IDENTIFICACION_CLIENTE,
    CASA_COBRANZA,
    '' AS USUARIO_SAC,
    DATE_FORMAT(FECHA_GESTION, '%d/%m/%Y %H:%i:%s') as FECHA_GESTION,
    ACCION_REALIZADA,
    RESPUESTA_OBTENIDA,
    CONTACTO_GESTIONO,
    COMENTARIOS_GESTIONO,
    NUMERO_GESTION,
    MOTIVO_NO_PAGO as MOTIVO_NO_PAGO,
    DATE_FORMAT(FECHA_PROXIMA_GESTION,'%d/%m/%Y %H:%i:%s') AS FECHA_PROXIMA_GESTION,
    if(TIEMPO_GESTION<45,ROUND(rand()*60+45),TIEMPO_GESTION) as tiempo_gestion,
    if(RESPUESTA_OBTENIDA in ('ACUERDO DE PAGO','ACUERDO DE CONVENIO'),SUBSTRING(NRO_CUENTA_PROMESA,1,length(NRO_CUENTA_PROMESA)-1),'') as multa,
    if(RESPUESTA_OBTENIDA in ('ACUERDO DE PAGO','ACUERDO DE CONVENIO'),if(CAST(ROUND(VALOR_PROMESA) AS CHAR)<100,100,CAST(ROUND(VALOR_PROMESA) AS CHAR)),'') as valor,
    if(RESPUESTA_OBTENIDA in ('ACUERDO DE PAGO','ACUERDO DE CONVENIO'),DATE_FORMAT(FECHA_PAGO_PROMESA, '%d/%m/%Y'),'') AS FECHA_PAGO,
    DIRECCION_VISITA,
    '' as FASE,
    CANAL_GESTION
FROM
    SISTEMECUADOR_ATM.GESTION
WHERE     NRO_IDENTIFICACION_CLIENTE!='' and RESPUESTA_OBTENIDA!='' and NUMERO_GESTION!=''
    and 
"""


# In[8]:


consulta1=consulta+" FECHA_GESTION BETWEEN DATE_FORMAT(DATE_SUB(NOW(), INTERVAL "+day+" DAY),'%Y/%m/%d 07:00:00') AND DATE_FORMAT(DATE_SUB(NOW(), INTERVAL "+day+" DAY),'%Y/%m/%d 14:00:00') ORDER BY FECHA_GESTION ASC "
consulta2=consulta+"FECHA_GESTION BETWEEN DATE_FORMAT(DATE_SUB(NOW(), INTERVAL "+day+" DAY),'%Y/%m/%d 14:00:00') AND DATE_FORMAT(DATE_SUB(NOW(), INTERVAL "+day+" DAY),'%Y/%m/%d 21:00:00') ORDER BY FECHA_GESTION ASC "


# In[9]:


resultado1=pd.read_sql(consulta1, con=db)
resultado2=pd.read_sql(consulta2, con=db)


# In[10]:


usuario=pd.read_excel(open('USUARIO.xlsx','rb'), sheet_name='Hoja1')


# In[11]:


result3 = pd.merge(resultado1,usuario,on='COD_AGENTE',how='left')
result4 = pd.merge(resultado2,usuario,on='COD_AGENTE',how='left')


# In[12]:


result5 = pd.merge(result3,resultado_multas,on='NRO_IDENTIFICACION_CLIENTE',how='left')
result6 = pd.merge(result4,resultado_multas,on='NRO_IDENTIFICACION_CLIENTE',how='left')


# In[13]:


result5['Segmento'].replace(np.nan, "4. VENCIDA FASE I", inplace = True)
result6['Segmento'].replace(np.nan, "4. VENCIDA FASE I", inplace = True)


# In[14]:


result5['FASE']=result5['Segmento']
result5['USUARIO_SAC']=result5['CODIGO']
result6['FASE']=result6['Segmento']
result6['USUARIO_SAC']=result6['CODIGO']


# In[15]:


result5.drop(['COD_AGENTE','CODIGO','Cedula','Segmento'], axis=1, inplace=True)
result6.drop(['COD_AGENTE','CODIGO','Cedula','Segmento'], axis=1, inplace=True)


# In[16]:


def quitar_espacio(base):
    comentario=base['COMENTARIOS_GESTIONO']
    if comentario[0]==' ':
        return comentario[1:]
    return comentario    


# In[17]:


result5['COMENTARIOS_GESTIONO']=result5.apply(quitar_espacio,axis=1)


# In[18]:


try:
    result6['COMENTARIOS_GESTIONO']=result6.apply(quitar_espacio,axis=1)
except:
    pass


# In[19]:


result5.sort_values(by='USUARIO_SAC',ascending=False,inplace=True)
result6.sort_values(by='USUARIO_SAC',ascending=False,inplace=True)


# In[20]:


nombre_1=result5['USUARIO_SAC'].value_counts().reset_index()
nombre_1['tipo']='MAÑANA'


# In[21]:


nombre_2=result6['USUARIO_SAC'].value_counts().reset_index()
nombre_2['tipo']='NOCHE'


# In[22]:


total=pd.concat([nombre_1,nombre_2])


# In[23]:


total_gestion=pd.concat([result5,result6])


# In[24]:


# total_gestion.TIPO_GESTION.count()


# In[25]:


# estructura=total_gestion


# In[26]:


# estructura=total_gestion[total_gestion['CONTACTO_GESTIONO']!='NO CONTACTO']
# estructura=estructura[estructura['CONTACTO_GESTIONO']!='TERC. NO VALIDO']


# In[27]:


demo_equivocados=total_gestion[total_gestion['RESPUESTA_OBTENIDA']=='AQUI NO VIVE / TRABAJA']


# In[28]:


equivocados=demo_equivocados[['NRO_IDENTIFICACION_CLIENTE','NUMERO_GESTION','RESPUESTA_OBTENIDA','FECHA_GESTION']]


# In[29]:


equivocados.drop_duplicates(['NRO_IDENTIFICACION_CLIENTE','NUMERO_GESTION'], keep='first',inplace=True)


# In[30]:


writer = pd.ExcelWriter('ESTRUCTURA DE GESTION Y MASIVOS AL '+day2+' DE MAYO.xlsx', engine='xlsxwriter')


# In[31]:


result5.to_excel(writer,  index = False,sheet_name='GESTION1')
worksheet = writer.sheets['GESTION1']
result6.to_excel(writer,  index = False,sheet_name='GESTION2')
worksheet = writer.sheets['GESTION2']
total.to_excel(writer,  index = False,sheet_name='USUARIO')
worksheet = writer.sheets['USUARIO']
equivocados.to_excel(writer,  index = False,sheet_name='EQUIVOCADOS')
worksheet = writer.sheets['EQUIVOCADOS']
writer.save()

