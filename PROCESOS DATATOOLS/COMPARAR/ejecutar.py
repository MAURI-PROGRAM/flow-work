import pandas as pd
import MySQLdb

def agregar_ceros(num):
    ced=num['IDENTIFICACION_DEUDOR']
    if len(ced)==9 or len(ced)==12 :
        if ced.isdigit():
            return '0'+ced
    return ced

leer_archivo_IVR=pd.read_excel(open('IVR1.xlsx','rb'), sheet_name='Hoja1', dtype={"CED": str,"NUMERO":str,"DEMO":str})
leer_demografico=pd.read_excel(open('Sistema de cobro.xlsx','rb'), sheet_name='Demografico', dtype={"IDENTIFICACION_DEUDOR": str,"TELEFONO":str})
leer_demografico=leer_demografico[['IDENTIFICACION_DEUDOR','TELEFONO']]
leer_demografico['IDENTIFICACION_DEUDOR']=leer_demografico.apply(agregar_ceros,axis=1)
leer_demografico['ASIGNADOS']='SI'
leer_demografico = leer_demografico.rename(columns={'IDENTIFICACION_DEUDOR':'CED','TELEFONO':'DEMO'})
verificacion = pd.merge(leer_archivo_IVR,leer_demografico,on=['CED','DEMO'],how='left')
verificacion.drop_duplicates(['NUMERO','CED'], keep='first',inplace=True)
nuevo_archivo='VERIFICADOS.xlsx'
writer = pd.ExcelWriter(nuevo_archivo, engine='xlsxwriter')
verificacion.to_excel(writer, sheet_name='BASE')
worksheet = writer.sheets['BASE']
writer.save()
