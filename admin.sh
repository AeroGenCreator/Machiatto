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
		
		mkdir -p ./.flet/storage/data/${DB_DIR}
		touch ./.flet/storage/data/${DB_DIR}/${DB_FILE}
		
		echo -e "
		Evaluando en './.flet/storage/data/$DB_DIR/$DB_FILE'
		"

		sqlite3 ./.flet/storage/data/${DB_DIR}/${DB_FILE} -cmd "
		CREATE TABLE IF NOT EXISTS users(
		users_id INTEGER PRIMARY KEY,
		nombre TEXT,
		correo TEXT,
		password TEXT,
		activo INTEGER
		);" .quit

		if ! sqlite3 ./.flet/storage/data/${DB_DIR}/${DB_FILE} -cmd "
			SELECT * 
			FROM users 
			WHERE nombre = '$ADMIN' AND password = '$ADMIN_PASSWORD';" .quit > /dev/null; then
				sqlite3 ./.flet/storage/data/${DB_DIR}/${DB_FILE} -cmd "
				INSERT INTO users(nombre, correo, password, activo) VALUES(
				'$ADMIN', '$ADMIN_EMAIL', '$ADMIN_PASSWORD', 1
				);
				" .quit
		else
			echo -e "
			La base de datos ya existe...
			Las credenciales estan congifuradas correctamente... 🔐"
		fi
		echo -e "Accesos correctos en la base de datos... ✅"
	else
		echo -e "No se pudo construir la base de datos. 
		Si sqlite3 no esta instaldo en su sistema puede instalarlo con 
		'sudo apt update install sqlite3'."
		echo -e "Tambien se recomienda instalar iconos cursor con 
		'sudo apt install adwaita-icon-theme'. Para 'Linux' 🐧. "
	fi
else
	echo -e "No se pudo configurar los accessos. No se encontraron 
	las variables de entorno 'ADMIN', 'ADMIN_PASSWORD', 'ADMIN_EMAIL', 
	'DB_DIR' & 'DB_FILE'. ❌"
# Desactiva la exportación automática
set +o allexport
fi
echo -e "
Machiatto puede ser ejecutado con confianza... ☕
"