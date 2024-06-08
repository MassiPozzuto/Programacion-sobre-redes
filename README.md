# Programacion sobre redes

## Chat Cliente-Servidor
El programa es un chat cliente-servidor. Utiliza threading para que varios clientes puedan conectarse en simultaneo. 

    Requisitos y pasos para ejecutar el chat:
        0. Antes que nada hay que tener python instalado en la PC (https://www.python.org/downloads/).
        1. En primer lugar, debemos instalar los requirements necesarios (mysql, mysql-connector-python y plyer) mediante el comando 'pip intall ...'.
        2. En segundo lugar, hay que iniciar el MySQL y el  Apache (aunque este no es necesario realmente) de XAMPP.
        3. En tercer lugar, tenes que crear una BD llamada 'chat' e importar el archivo chat.sql.
        4. En cuarto lugar, debes ejecutar el archivo server.py y, luego, el client.py.

Una vez el chat corriendo tendremos que loguearnos colocando primero un username y luego su contraseña, estos los podremos ver desde '127.0.0.1/phpmyadmin', en la respectiva BD 'chat'. Cuando estemos logueados ya podriamos interactuar en el chat global (que es el default) en donde todos los usuarios podran intercambiar mensajes. Además, podemos tener chats individuales con los usuarios. Los mensajes que se envien durante la ejecución se guardaran en la base de datos, por lo que, luego se mostraran al entrar a el chat correspondiente. En el programa nos vamos a poder manejar a traves de comandos.

    Para manejarse en el programa hay una serie de comandos:
        1. /sendTo <username>: Seleccionar el chat en el que enviaras mensajes, si colocas 'global' iras a un chat con todos los usuarios, sino deberas colocar el username de determinado usuario.
        2. /info: Indica el chat en el que te encuentras en ese momento.
        3. /users: Enseña todos los usuarios conectados en este momento.
        4. /help: Muestra todos los comandos disponibles y sus funciones.
        5. /exit: Cierra la conexión con el servidor.
