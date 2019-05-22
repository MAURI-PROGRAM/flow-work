
# coding: utf-8

# In[1]:


# This is a cell to hide code snippets from displaying 
# This must be at first cell! 
from IPython.display import HTML 
hide_me =''
HTML('''<script> code_show=true; function code_toggle() { if (code_show) { $('div.input').each(function(id) { el = $(this).find('.cm-variable:first'); if (id == 0 || el.text() == 'hide_me') { $(this).hide(); } }); $('div.output_prompt').css('opacity', 0); } else { $('div.input').each(function(id) { $(this).show(); }); $('div.output_prompt').css('opacity', 1); } code_show = !code_show } $( document ).ready(code_toggle); </script> <form action="javascript:code_toggle()"><input style="opacity:0" type="submit" value="Click here to toggle on/off the raw code."></form>''')


# In[2]:


#hide_me
import pandas as pd
import MySQLdb


# In[3]:


#hide_me
fecha_ini='2019-04-01 00:00:00'
fecha_fin='2019-04-31 21:00:00'


# In[4]:


#hide_me
db = MySQLdb.connect(host="172.18.55.6",    # tu host, usualmente localhost
                     user="comandato",         # tu usuario
                     passwd="comandato123",  # tu password
                     db="SISTEMECUADOR_ATM")        # el nombre de la base de datos


# In[5]:


#hide_me
consulta="""
SELECT 
    NRO_IDENTIFICACION_CLIENTE, COD_AGENTE,
    CASE CONTACTO_GESTIONO
                WHEN 'CLIENTE' THEN 1
                WHEN 'TITULAR' THEN 1
                WHEN 'TERC. VALIDO' THEN 2
                WHEN 'TERC. NO VALIDO' THEN 3
                WHEN 'NO CONTACTO' THEN 4
                ELSE 5
            END AS CONTACTO,
    CASE RESPUESTA_OBTENIDA
                WHEN 'ACUERDO DE PAGO' THEN 1
                WHEN 'ACUERDO DE CONVENIO' THEN 2
                WHEN 'LOCALIZADO SIN ACUERDO' THEN 3
                WHEN 'AQUI NO VIVE / TRABAJA' THEN 4
                ELSE 5
            END AS TIPO_ACUERDO
FROM
    sistemecuador_atm.gestion
WHERE
    ACCION_REALIZADA = 'HACER LLAMADA'
AND
FECHA_GESTION BETWEEN '{0}' AND '{1}';
""".format(fecha_ini,fecha_fin)


# In[6]:


#hide_me
resultado=pd.read_sql(consulta, con=db)


# In[7]:


contactabilidad=resultado.groupby('NRO_IDENTIFICACION_CLIENTE').agg({'CONTACTO':'min','TIPO_ACUERDO':'min'})


# In[8]:


contactabilidad['CONTACTO'].replace(to_replace=[1,2,3,4,5],value=['TITULAR','TERCERO','EQUIVOCADO','NO CONTACTO','SIN GESTION'],inplace=True)


# In[9]:


contactabilidad['TIPO_ACUERDO'].replace(to_replace=[1,2,3,4,5],value=['AC. PAGO','AC. CONVENIO','LOCALIZADO','EQUIVOCADO','OTROS'],inplace=True)


# In[10]:


contactabilidad.head()


# In[11]:


writer = pd.ExcelWriter('CONTACTABILIDAD MARZO25.xlsx', engine='xlsxwriter')
contactabilidad.to_excel(writer, sheet_name='CORRIENTE')
worksheet = writer.sheets['CORRIENTE']
writer.save()

