#!/usr/bin/env bash

echo -e "Configurando accesos administrador... 📦"

# Activa la exportación automática desde el .env
set -o allexport
source .env

# Asegurarse de que todas las variables de entorno minimas esten declaradas.
if [ -n "$ADMIN" ] && \
	[ -n "$ADMIN_PASSWORD" ] && \
	[ -n "$ADMIN_EMAIL" ] && \
	[ -n "$DB_DIR" ] && \
	[ -n "$DB_FILE" ] && \
    [ -n "$FLET_APP_STORAGE_DATA" ]; then
	
	if sqlite3 --version 2>&1; then
		
		echo -e "Resolviendo las rutas... 🔦"
		
		mkdir -p ./${DB_DIR}
		touch ./${DB_DIR}/${DB_FILE}
		
		echo -e "
		Evaluando en './$DB_DIR/$DB_FILE'
		"
        
		sqlite3 ./${DB_DIR}/${DB_FILE} -cmd "
		CREATE TABLE IF NOT EXISTS users(
		users_id INTEGER PRIMARY KEY,
		nombre TEXT,
		correo TEXT,
		password TEXT,
		activo INTEGER
		);" .quit

        USER_EXISTS=$(sqlite3 ./${DB_DIR}/${DB_FILE} "SELECT * FROM users WHERE nombre = '$ADMIN' AND password = '$ADMIN_PASSWORD';" .quit)

        if [ -z "$USER_EXISTS" ]; then
            echo "El usuario no existe, insertando credenciales..."
            
            sqlite3 ./${DB_DIR}/${DB_FILE} "
            INSERT INTO users(nombre, correo, password, activo) 
            VALUES('$ADMIN', '$ADMIN_EMAIL', '$ADMIN_PASSWORD', 1);
            " .quit
		else
			echo -e "
			La base de datos ya existe...
			Las credenciales estan congifuradas correctamente... 🔐"
		fi
		echo -e "Accesos correctos en la base de datos... ✅"
        echo -e "
        Machiatto puede ser ejecutado con confianza... ☕
        "
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
	'DB_DIR', 'DB_FILE' 'FLET_APP_STORAGE_DATA'. ❌"
fi
# Desactiva la exportación automática
set +o allexport