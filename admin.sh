#!/usr/bin/env bash

echo -e "Configurando accesos administrador... 📦"

# Activa la exportación automática desde el .env
set -o allexport
source .env

if [ -n "$ADMIN" ] && \
	[ -n "$ADMIN_PASSWORD" ] && \
	[ -n "$ADMIN_EMAIL" ] && \
	[ -n "$DB_DIR" ] && \
	[ -n "$DB_FILE" ]; then
	
	if sqlite3 --version 2>&1; then
		
		echo -e "Resolviendo las rutas... 🔦"
		
		mkdir -p ${DB_DIR}
		touch ./${DB_DIR}/${DB_FILE}
		
		echo -e "La base de datos se ha creado en ./$DB_DIR/$DB_FILE"
		
		sqlite3 ./${DB_DIR}/${DB_FILE} -cmd "
CREATE TABLE IF NOT EXISTS users(
	users_id INTEGER PRIMARY KEY,
	nombre TEXT,
	correo TEXT,
	password TEXT,
	activo INTEGER
	);" -cmd "
INSERT INTO users(nombre, correo, password, activo) VALUES(
'$ADMIN', '$ADMIN_EMAIL', '$ADMIN_PASSWORD', 1
);
" .quit
		echo -e "Accesos creados con exito... ✅"
	else
		echo -e "No se pudo construir la base de datos. 
Si sqlite3 no esta instaldo en su sistema puede instalarlo con 
'sudo apt update install sqlite3'."
	fi
else
	echo -e "No se pudo configurar los accessos. No se encontraron 
las variables de entorno 'ADMIN', 'ADMIN_PASSWORD', 'ADMIN_EMAIL', 
'DB_DIR' & 'DB_FILE'. ❌"
# Desactiva la exportación automática
set +o allexport
fi