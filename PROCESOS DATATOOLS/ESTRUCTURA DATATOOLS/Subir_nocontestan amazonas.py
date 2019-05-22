
# coding: utf-8

# In[1]:


import pandas as pd
import MySQLdb
from datetime import datetime,timedelta
import random


# In[2]:
dia_atras='0'

#formato de fecha AAAA-mm-dd  ejmp 2018-04-25
fecha_ini="DATE_FORMAT(DATE_SUB(NOW(), INTERVAL "+dia_atras+" DAY),'%Y/%m/%d 07:00:00')"
fecha_fin="DATE_FORMAT(DATE_SUB(NOW(), INTERVAL "+dia_atras+" DAY),'%Y/%m/%d 21:00:00')"


# In[3]:


corriente="in ('4445')"


# In[4]:


colas=[corriente]


# In[5]:


nombre_colas=['CORRIENTE']


# In[6]:


comentarios=['']


# In[7]:


db = MySQLdb.connect(host="172.18.55.99",    # tu host, usualmente localhost
                     user="comandato",         # tu usuario
                     passwd="comandato123",  # tu password
                     db="call_center")        # el nombre de la base de datos
db2 = MySQLdb.connect(host="172.18.55.6",    # tu host, usualmente localhost
                     user="comandato",         # tu usuario
                     passwd="comandato123",  # tu password
                     db="sistemecuador_amazonas")        # el nombre de la base de datos


# In[8]:


cur2= db2.cursor()
cur= db2.cursor()


# In[9]:


for cola,nombre_cola,comentario in zip(colas,nombre_colas,comentarios):
    consulta="""
        SELECT 
        c.id_campaign,cola.name
        FROM
        calls as c,(SELECT id,name FROM campaign where queue {0}) as cola
        WHERE c.start_time between {1} and {2}
        and c.id_campaign=cola.id GROUP BY c.id_campaign;""".format(cola,fecha_ini,fecha_fin)
    campañas=pd.read_sql(consulta, con=db)
    print(nombre_cola)
    print(campañas)
    id_camp=''
    for row in campañas.itertuples():
        id_camp=id_camp+','+str(row.id_campaign)
    id_camp=id_camp[1:]
    consulta_2="""SELECT
                        valores.valor AS cedula,
                        c.phone AS telefono,
                        c.datetime_originate AS fecha
                    FROM
                        calls c 	LEFT JOIN

                        (SELECT 
                            call_attribute.id_call AS id_call,
                            call_attribute.value AS valor
                        FROM
                            calls, call_attribute
                            WHERE
                        call_attribute.column_number = 2
                        AND calls.id_campaign in ({0})
                        AND calls.id = call_attribute.id_call) AS valores

                        ON valores.id_call = c.id

                    WHERE

                    c.id_campaign in ({0})
                    AND (c.status = 'Success'
                    OR c.status = 'Failure'
                    OR c.status = 'ShortCall'
                    OR c.status = 'NoAnswer'
                    OR c.status = 'Abandoned')
                    AND c.datetime_originate between {1} and {2}
                    ORDER BY uniqueid ASC;""".format(id_camp,fecha_ini,fecha_fin)
    resultado=pd.read_sql(consulta_2, con=db)
    contador_ya_gestion=0
    contador_subidos=0
    for row2 in resultado.itertuples():
        telefono=str(row2.telefono)
        cedula=str(row2.cedula)
        fech_gest=str(row2.fecha)
        busc_querry="""SELECT ID_GESTION 
                FROM sistemecuador_amazonas.gestion
                where ID_CLIENTE='{0}' 
                AND TELEFONO ='{1}' 
                and  FECHA_GESTION 
                between '{2} 07:00:00' and '{2} 20:30:00';""".format(cedula,telefono,fech_gest[:10])
        gestionado=False
        insert=False
        try:
            gestionado=cur2.execute(busc_querry)
            db2.commit()
            if gestionado:
                contador_ya_gestion=contador_ya_gestion+1
            else:
                ini_querry="""INSERT INTO `sistemecuador_amazonas`.`gestion` (`ID_CLIENTE`,`FECHA_GESTION`,
                            `SEG_CALLTYPE`,`CALLTYPE`,`MOTIVO_ATRASO`,`OBSERVACION`,`TELEFONO`,`PRIMER_NIVEL`,`SEGUNDO_NIVEL`,
                            `AGENTE`,`OPERACION`,`RUTA_AUDIO`,`TIEMPO_GESTION`,`TIPO`,`SALDO_TOTAL`,`TOTAL_RECUPERAR`,
                            `FECHA_PROXIMA_GESTION`,`COMPROMISO`,`CIUDAD`)
                            VALUES ('{0}','{1}','NO CONTACTO','NO CONTESTA',
                            'NO QUISO DAR MOTIVO DE NO PAGO','NC','{2}','GESTION TELEFONICA','NO CONTESTA',
                            '4445','000000','','31','TIPO','0',
                            '0','','0','');
                            """.format(cedula,fech_gest,telefono)
                try:
                    insert=cur.execute(ini_querry)
                    db2.commit()
                    contador_subidos=contador_subidos+1
                except:
                    db2.rollback()
        except:
            db2.rollback()
    print("CANTIDAD DE CLIENTES QUE YA FUERON GESTIONADOS : "+str(contador_ya_gestion))
    print("CANTIDAD DE CLIENTES QUE FUERON SUBIDOS : "+str(contador_subidos))

