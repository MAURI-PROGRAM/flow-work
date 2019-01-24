#importar pandas
import pandas as pd
import MySQLdb

archivo_actual='PAGOS.xlsx'

db = MySQLdb.connect(host="172.18.55.99",    # tu host, usualmente localhost
                     user="comandato",         # tu usuario
                     passwd="comandato123",  # tu password
                     db="SISTEMECUADOR_ATM")        # el nombre de la base de datos
cur = db.cursor()

df_act=pd.read_excel(open(archivo_actual,'rb'), sheet_name='Hoja1')


for row in df_act.itertuples():
	sql_update="""UPDATE `SISTEMECUADOR_ATM`.`MULTAS_MENSUALES` SET `Pago`='{0}', 
		`dia_pago`='{1}', `tipo`='{2}' WHERE `Cedula`='{3}' 
		and`No_multa`='{4}' and`Anio`='{5}' and`Mes`='{6}';
	""".format(row.valor,row.dia,row.tipo,row.ced,row.multa,row.anio,row.mes)
	try:
		update_querry = cur.execute(sql_update)
		db.commit()
		print('ACTUALIZADO EXITOSAMENTE')
	except:
		db.rollback()
		PRINT('SIN ACTUALIZAR NO EXISTE')