#importar pandas
import pandas as pd
#importar sqldf para manejar sql
from pandasql import sqldf
archivo_actual='HONORARIOS.xlsx'
archivo_nuevo='HONORARIOS NUEVOS.xlsx'

df_act=pd.read_excel(open(archivo_actual,'rb'), sheet_name='Hoja1')
pysqldf = lambda q: sqldf(q, globals())

writer = pd.ExcelWriter(archivo_nuevo, engine='xlsxwriter')
workbook = writer.book

numero_multas=pysqldf("""SELECT IDENTIFICACION,count(*) as NUM_MULTAS,min(ALTURA_PAGO) as MIN_MORA	FROM df_act group by IDENTIFICACION;""")

base_menor=pysqldf("""SELECT df_act.*	FROM df_act 
						INNER JOIN numero_multas ON 
						numero_multas.IDENTIFICACION = df_act.IDENTIFICACION 
						where numero_multas.NUM_MULTAS=1 and VALOR_INFRACCION<=60;""")

base_faseI=pysqldf("""SELECT df_act.*	FROM df_act 
						INNER JOIN numero_multas ON 
						numero_multas.IDENTIFICACION = df_act.IDENTIFICACION 
						where not(numero_multas.NUM_MULTAS=1 and VALOR_INFRACCION<=60) AND numero_multas.MIN_MORA<=180;""")

base_faseII=pysqldf("""SELECT df_act.*	FROM df_act 
						INNER JOIN numero_multas ON 
						numero_multas.IDENTIFICACION = df_act.IDENTIFICACION 
						where not(numero_multas.NUM_MULTAS=1 and VALOR_INFRACCION<=60) AND numero_multas.MIN_MORA>180;""")

base_total=pysqldf("""SELECT base_menor.*,'MENOR CUANTIA' AS SEGMENTO, 2 as HONORARIO FROM base_menor
					union all 
					SELECT base_faseI.*,'FASE I' AS SEGMENTO, (base_faseI.VALOR_INFRACCION*0.037) as HONORARIO FROM base_faseI
					union all
					SELECT base_faseII.*,'FASE II' AS SEGMENTO,(base_faseII.VALOR_INFRACCION*0.045) as HONORARIO FROM base_faseII
	""")
base_total.to_excel(writer, sheet_name='Base')
worksheet = writer.sheets['Base']
writer.save()