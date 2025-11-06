Una empresa de logistica desea implementar una plataforma distribuida para gestionar su operacion. Se requiere crear una arquitectura basada en
microservicios que cumpla con los siguientes puntos/

1 Mricroservicios de Autenticacion (Login)

implementar un servicio en Node.js que permita autenticar usuarios mediante en metodo POST. El servicio debe consultar la tabla usuarios en 
MySQL y devolver un token JWT al cliente.
La tabla de usuarios contiene:

id: identificador unico del usuario
correo: correo electronico
password: contrasenia del usuario

2 Microservicio de Vehiculos

Crear un servicio con metodos estandar REST para gestionar vehiculos (crear, listar, actualizar, eliminar).
Este servicio debe estar protegido por JWT y utilizar MongoDB como base de datos.

id: Identificador unico del vehiculo
placa: Numero de placa
tipo: Tipo de vehiculo (camion, furgon, moto)
capacidad: Capacidad de carga en kg
estado: Estado actual (disponible, en ruta, mantenimiento)

3 Microservicio de Envios

Implementar un servicio utilizando GraphQL para gestionar envios, con base de datos MySQL.
La tabla envios debe incluir.

id: identificador unico de envios
usuario_id: Usuario que solicite envios
vehiculo_id: Vehivulo asignado
origen: Direccion de origen
destino: Direccion de destino
fecha_envio: Fecha programada
estado: Estado del envio(pendiente, en transito, entregado)

4 Comunicacion entre microservicios con gRPC

El microservicio de Envios debe comunicarse con el microservicio de Vehiculos mediante gRPC par verificar deisponibilidad antes de asignar
un vehiculo

5 Infraestructura y despliegue

Instalar Nginx como servidor proxy inverso para que todas las llamdas se relaicen por el puerto 80 y se redirijan a los mocroservicios correspo
ndientes.
Generar documentacion Swagger para el microserviio de Vehiculos.
Dockerzar todos los microservicios y configurar un entorno deonde el proxy inverso permita acceder a todos por el puerto 80.