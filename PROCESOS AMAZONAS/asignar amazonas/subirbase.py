
import pandas as pd
import MySQLdb
from pandasql import sqldf

#conecion a la BD
db = MySQLdb.connect(host="172.18.55.6",    # tu host, usualmente localhost
                     user="comandato",         # tu usuario
                     passwd="comandato123",  # tu password
                     db="TELEFONICOS_NUMEROS")        # el nombre de la base de datos
cur= db.cursor()
base=pd.read_excel(open('asignar.xlsx','rb'), sheet_name='BASE', dtype={"CEDULA": str})

def ejecutar(querrys):
	try:
		enviar=cur.execute(querrys)
		db.commit()
		resp='ok'
	except Exception as e:
		db.rollback()
		resp='no'
	else:
		pass
	finally:
		pass
	return(resp)

for row in base.itertuples():
	insertar_cedula="""INSERT INTO `SISTEMECUADOR_AMAZONAS`.`INFORMACION CLIENTE`(`CEDULA`) 
					VALUES ('{0}');""".format(row.CEDULA)
	a1=ejecutar(insertar_cedula)
	insertar_operacion="""INSERT INTO `SISTEMECUADOR_AMAZONAS`.`OPERACION` (`id_OPERACION`, `id_CEDULA`) 
					VALUES ('{0}', '{1}');""".format(row.operacion,row.CEDULA)
	a2=ejecutar(insertar_operacion)
	actualizar_cedula="""UPDATE `SISTEMECUADOR_AMAZONAS`.`INFORMACION CLIENTE` 
						SET `NOMBRE`='{0}', `NRO_CLIENTE`='{1}', 
						`OFICIAL`='{2}', `OFICINA`='P', `SALDO_TOTAL`='0', 
						`TOTAL_RECUPERAR`='0' WHERE `CEDULA`='{3}';""".format(row.NOMBRE,row.Cliente,row.oficial,row.CEDULA)
	a3=ejecutar(actualizar_cedula)
	actualizar_operacion="""UPDATE `SISTEMECUADOR_AMAZONAS`.`OPERACION` 
							SET `DESCRIPCION`='{0}', `SALDO_TOTAL`='0', `TOTAL_RECUPERAR`='0', `TIPO`='{0}' 
							WHERE`id_OPERACION`='{1}' and `id_CEDULA`='{2}' ;""".format(row.TIPO,row.operacion,row.CEDULA)
	a4=ejecutar(actualizar_operacion)

	print(a1,' ',a2,' ',a3,' ',a4)
