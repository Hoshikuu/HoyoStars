from discord.ext import commands

# Modulos para gestionar JSON
from json import load, dump
from os.path import isfile

# Modulo de funciones
from func.terminal import printr

# Variable que se usa globalmente para poder acceder al contenido del archivo de configuracion del bot
configJson = None

# TODO: Que se pueda cambiar dinamicamente el nombre del archivo de configuracion
# Carga el archivo de configuracion en la variable global, Se puede llamar en ejecucion para recargar el archivo de configuracion
def ChargeConfig():
    # Crea el fichero si no existe
    if not isfile("botconfig.json"):
        printr(f"Fichero de configuración no esta creado.", 4)
        with open("botconfig.json", "w", encoding="utf-8") as file:
            file.write("{}") # Para que lo pille como json vacio
            printr(f"Fichero de configuración creado.", 1)
        
    global configJson # Para poder modificar la variable

    # Lee el contenido del json y lo carga a la variable
    with open("botconfig.json", "r", encoding="utf-8") as file:
        configJson = load(file)
        printr(f"Cargando fichero de configuración", 1)

# Obtener el prefijo del servidor en la cual se esta enviando el mensaje a travez de la variable global
def GetPrefix(bot, message):
    guildID = str(message.guild.id)
    prefix = configJson[guildID]["prefix"]
    return prefix

# Devuelve true si el usuario tiene los roles indicados en la configuracion del servidor
def IsSU():
    async def predicate(ctx):
        guildID = str(ctx.guild.id)
        suRoles = configJson[guildID]["su"]

        # Verificar por IDs de roles (recomendado)
        if any(role.id in suRoles for role in ctx.author.roles):
            return True

        # (Opcional) Verificar por nombres de roles si los guardas como texto
        if any(role.name in suRoles for role in ctx.author.roles):
            return True

        raise commands.MissingAnyRole(suRoles)

    return commands.check(predicate)

# Se llama a esta funcion cuando un servidor no esta registrado en el json
#! Esta funcion recarga la variable de configuracion ya que añade un servidor nuevo
# Por defecto el setup esta en falso para que el usuario tenga que ejecutar el comando
def DefaultServerConfig(guild):
    # Cnfiguracion por defecto
    configJson[guild] = {
        "setup": 0,
        "prefix": "hs$",
        "su": []
    }
    with open("botconfig.json", "w") as file:
        dump(configJson, file, indent=4)

    printr(f"Configuración por defecto creada para el servidor.", 1)
    ChargeConfig() # Recarga la configuración

# Comprobar que se haya ejecutado el comando setup en el servidor
def CheckSetUp(ctx):
    # Principalmente la razon de esto, es para prevenir el uso de comandos cuando el bot aun no esta configurado
    # Las funciones de contar mensajes y demas que no requieran ejecutar ningun comando seguiran funcionando
    if not bool(configJson[str(ctx.guild.id)]["setup"]):
        return True