window.addEventListener("DOMContentLoaded", () => {
  const fechaHoraElement = document.getElementById("fechaHora");
  const botonEnviar = document.getElementById("botonEnviar");
  const inputMensaje = document.getElementById("inputMensaje");
  const mensajes = document.getElementById("mensajes");
  let modo_administrador = window.modo_administrador || false;
  const maxFileSize = modo_administrador ? Infinity : 5 * 1024 * 1024; // No hay límite para admin, 10 MB para usuarios
  const botonSubirArchivo = document.getElementById("botonSubirArchivo");
  const archivoInput = document.getElementById("archivoInput");
  //funcion registrar acciones
  function registrarAccion(accion) {
    fetch("/registrar_accion", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ accion: accion }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.respuesta) {
          console.log("Registro de acción:", data.respuesta);
        }
      })
      .catch((error) => {
        console.error("Error al registrar la acción:", error);
      });
  }

  // Verifica si el elemento archivoInput está disponible
  if (!archivoInput) {
    console.error("Elemento de archivo no encontrado.");
    return;
  }

  let esperandoClaveAdmin = false;
  let nombreUsuario = "";
  let usuarioAdmin = "";
  let esperandoSeleccionArchivo = false;
  let archivoSeleccionado = [];
  let esperandoConfirmacion = false;
  let listaMostrada = false;

  function actualizarFechaHora() {
    const fecha = new Date();
    const dia = fecha.getDate().toString().padStart(2, "0");
    const mes = (fecha.getMonth() + 1).toString().padStart(2, "0");
    const año = fecha.getFullYear();
    const horas = fecha.getHours().toString().padStart(2, "0");
    const minutos = fecha.getMinutes().toString().padStart(2, "0");
    fechaHoraElement.textContent = `${dia}/${mes}/${año}, ${horas}:${minutos}`;
  }

  actualizarFechaHora();
  setInterval(actualizarFechaHora, 60000);

  setTimeout(() => {
    agregarMensajeIA("¡Hola! Me llamo Clark. ¿Cuál es tu nombre?");
  }, 500);

  botonEnviar.addEventListener("click", enviarMensaje);
  inputMensaje.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      enviarMensaje();
    }
  });

  const botonUsuario = document.querySelector(".boton-usuario");

  botonUsuario.addEventListener("click", () => {
    if (modo_administrador) {
      modo_administrador = false;
      registrarAccion("Modo administrador desactivado");
      console.log("Modo administrador desactivado");
      agregarMensajeIA("Modo usuario activado");
      registrarAccion(`Modo usuario activado: ${modo_administrador}`);
    }
  });

  function enviarMensaje() {
    const mensaje = inputMensaje.value.trim();

    if (mensaje.length > 300) {
      alert("El mensaje no puede superar los 300 caracteres.");
      return;
    }

    if (mensaje) {
      // Si estamos esperando una confirmación
      if (esperandoConfirmacion) {
        manejarConfirmacion(mensaje.toLowerCase()); // Manejar como confirmación
        inputMensaje.value = ""; // Limpiar el campo de texto
        return;
      }

      if (!nombreUsuario) {
        nombreUsuario = mensaje;
        agregarMensajeIA(
          `¡Un placer, ${nombreUsuario}! Puedes preguntarme algo e intentare ayudarte.`
        );
        inputMensaje.value = "";
        return;
      }

      agregarMensajeUsuario(mensaje);
      inputMensaje.value = "";

      if (mensaje.toLowerCase() === "activar modo administrador") {
        esperandoClaveAdmin = true;
        agregarMensajeIA(
          "Por favor, ingresa el nombre de usuario para activar el modo administrador."
        );
        console.log("Esperando nombre de usuario para admin...");
        return;
      }

      if (esperandoClaveAdmin && !usuarioAdmin) {
        usuarioAdmin = mensaje;
        agregarMensajeIA("¡Usuario ingresado! Ahora ingresa la clave.");
        console.log("Usuario ingresado para admin: " + usuarioAdmin);
        return;
      }

      if (esperandoClaveAdmin) {
        const claveAdminCorrecta = "silvestre";
        if (mensaje === claveAdminCorrecta && usuarioAdmin === "abuelo") {
          modo_administrador = true;
          esperandoClaveAdmin = false;
          registrarAccion(`Modo Administrador activado: ${modo_administrador}`);
          console.log("Modo administrador activado");
          agregarMensajeIA("¡Modo administrador activado!");
        } else {
          agregarMensajeIA("Usuario o clave incorrectos. Intenta nuevamente.");
          console.log("Usuario o clave incorrectos");
          esperandoClaveAdmin = true;
        }
        usuarioAdmin = "";
        return;
      }
      // Ver datos
      if (mensaje.toLowerCase() === "ver datos") {
        if (!modo_administrador) {
          console.log("Error: Usuario no tiene permisos de administrador.");
          agregarMensajeIA("No tienes acceso para ver los datos.");
          return;
        }

        console.log(
          "Modo administrador activado. Mostrando lista de archivos..."
        );
        fetch("/ver_datos", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ mensaje: mensaje }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.archivos) {
              archivoSeleccionado = data.archivos;
              mostrarListaArchivos(data.archivos); // Muestra la lista en la interfaz
              listaMostrada = true;
              esperandoSeleccionArchivo = true; // Bloquear cualquier otro flujo
              agregarMensajeIA(
                "Por favor, selecciona un número de archivo para ver su contenido."
              );
              console.log("Lista de archivos mostrada. Esperando selección...");
            } else {
              agregarMensajeIA(data.respuesta);
              console.log(
                "Error al obtener lista de archivos:",
                data.respuesta
              );
            }
          })
          .catch((error) => {
            console.error("Error al contactar con el backend:", error);
          });
        return;
      }

      // Verificar si se está esperando una selección de archivo
      if (esperandoSeleccionArchivo) {
        const numeroSeleccionado = parseInt(mensaje);
        if (
          archivoSeleccionado &&
          !isNaN(numeroSeleccionado) &&
          numeroSeleccionado > 0 &&
          numeroSeleccionado <= archivoSeleccionado.length
        ) {
          const archivo = archivoSeleccionado[numeroSeleccionado - 1];
          console.log(`Archivo seleccionado: ${archivo}`);
          fetch("/ver_contenido", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ archivo: archivo }),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.contenido) {
                // Mostrar el contenido del archivo si está disponible
                agregarMensajeIA(
                  `Contenido del archivo ${archivo}:\n` +
                    JSON.stringify(data.contenido, null, 2) // Formatea el JSON
                );
              } else {
                agregarMensajeIA(data.respuesta); // Mensaje de error si algo falla
              }
              esperandoSeleccionArchivo = false; // Desbloquear flujo
              console.log(
                "Contenido del archivo mostrado. Listo para nuevas interacciones."
              );
            })
            .catch((error) => {
              console.error("Error al contactar con el backend:", error);
            });
        } else {
          agregarMensajeIA(
            "Por favor, selecciona un número válido de la lista para continuar."
          );
          console.log("Selección inválida:", mensaje);
        }
        return;
      }
    }
    // Código ajustado para confirmar o rechazar respuestas
    fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        mensaje: mensaje,
        modo_administrador: modo_administrador,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        registrarAccion("Respuesta recibida del servidor.");
        console.log("Respuesta recibida del servidor:", data);

        // Verificar si la respuesta requiere confirmación
        if (data.solicita_confirmacion === true) {
          esperandoConfirmacion = true; // Bloquear flujo hasta confirmación
          registrarAccion("Se requiere confirmación del usuario.");

          // Guardar datos relevantes
          datosEsperandoConfirmacion = data.datos_confirmacion;
          registrarAccion(
            `Datos de confirmación almacenados: ${JSON.stringify(
              datosEsperandoConfirmacion
            )}`
          );

          // Agregar mensaje para la interacción del usuario
          agregarMensajeIA(
            "¿Tiene coherencia mi respuesta? Responde con 'sí' para confirmar o 'no' para rechazar."
          );
          registrarAccion(
            "Mensaje enviado al usuario solicitando confirmación."
          );
        } else {
          // Enviar la respuesta de la IA al usuario
          agregarMensajeIA(data.respuesta);
          registrarAccion(`Respuesta enviada al usuario: ${data.respuesta}`);
        }
      })
      .catch((error) => {
        console.error("Error al contactar con la IA:", error);
        registrarAccion(`Error al contactar con la IA: ${error.message}`);
        agregarMensajeIA(
          "Hubo un problema al procesar tu solicitud. Intenta de nuevo."
        );
      });

    // Función para manejar la confirmación del usuario
    function manejarConfirmacion(respuesta) {
      registrarAccion(
        `Modo confirmación activado. Respuesta del usuario: ${respuesta}`
      );
      console.log(
        "Modo confirmación: Respuesta del usuario recibida:",
        respuesta
      );

      if (respuesta.toLowerCase() === "sí") {
        const categoria = prompt(
          "Escribe la categoría donde deseas guardar la respuesta:"
        );
        if (categoria) {
          fetch("/confirmar_respuesta", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              categoria: categoria.trim(),
            }),
          })
            .then((response) => response.json())
            .then((data) => {
              agregarMensajeIA(data.respuesta);
              registrarAccion("Respuesta confirmada y procesada.");
              esperandoConfirmacion = false; // Salir de modo de confirmación
            })
            .catch((error) => {
              console.error("Error al confirmar la respuesta:", error);
              registrarAccion(
                `Error al confirmar la respuesta: ${error.message}`
              );
              agregarMensajeIA("Hubo un error al confirmar la respuesta.");
            });
        } else {
          agregarMensajeIA(
            "Por favor, escribe una categoría válida para guardar la respuesta."
          );
          registrarAccion("El usuario no proporcionó una categoría.");
        }
      } else if (respuesta.toLowerCase() === "no") {
        fetch("/rechazar_respuesta", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            agregarMensajeIA(data.respuesta);
            registrarAccion("Respuesta rechazada correctamente.");
            esperandoConfirmacion = false; // Finalizar el proceso
          })
          .catch((error) => {
            console.error("Error al rechazar la respuesta:", error);
            registrarAccion(`Error al rechazar la respuesta: ${error.message}`);
            agregarMensajeIA("Hubo un error al rechazar la respuesta.");
          });
      } else {
        agregarMensajeIA(
          "Por favor, responde con 'sí' para confirmar o 'no' para rechazar."
        );
        registrarAccion("El usuario proporcionó una respuesta inválida.");
      }
    }

    // funcion subir archivo
    botonSubirArchivo.addEventListener("click", async function () {
      const archivo = archivoInput.files[0]; // Aquí intentamos capturar el archivo

      // Validación: Si no hay un archivo seleccionado, mostrar mensaje de error.
      if (!archivo) {
        console.error("No se seleccionó ningún archivo.");
        alert("Por favor, selecciona un archivo.");
        return;
      }

      // Depuración: Confirmar los datos del archivo después de validarlo
      console.log(
        "Archivo seleccionado:",
        archivo.name,
        "Tamaño:",
        archivo.size
      );

      // Verificar tamaño del archivo dinámicamente según el modo actual
      const esAdministrador = window.modo_administrador || modo_administrador; // Validación para el modo administrador
      const limiteTamano = esAdministrador ? Infinity : 5 * 1024 * 1024;

      if (archivo.size > limiteTamano) {
        alert(
          `El archivo es demasiado grande. ${
            esAdministrador
              ? "No deberías estar viendo esto. Contacta al administrador."
              : "Máximo permitido: 5 MB para usuarios."
          }`
        );
        return; // Detener el proceso de carga
      }

      // Proceso de subida
      const formData = new FormData();
      formData.append("archivo", archivo);

      try {
        const response = await fetch("/subir_archivo", {
          method: "POST",
          body: formData,
        });
        const data = await response.json();

        let contenido = data.respuesta || "No se pudo leer el contenido.";
        if (typeof contenido === "object") {
          contenido = JSON.stringify(contenido, null, 2);
        }
        agregarMensajeIA(
          `Archivo subido [${archivo.name}]:<br><br> ${contenido}`
        );
      } catch (error) {
        console.error("Error al subir el archivo:", error);
      }
    });
    //
    // Código para manejar la confirmación o rechazo de respuestas generadas por la IA
    // - Este código permite al usuario responder con "sí" o "no" para confirmar o rechazar respuestas.
    // - Si se confirma, se envía una solicitud al servidor para guardar la respuesta en la categoría correspondiente.
    // - Si se rechaza, se reitera la solicitud o se solicita corrección manual tras varios intentos.

    let datosEsperandoConfirmacion = null; // Guarda datos para la confirmación actual

    // Si estamos en proceso de confirmación
    if (esperandoConfirmacion) {
      manejarConfirmacion(mensaje.toLowerCase());
      return;
    }

    // Función para manejar confirmación de respuestas
    function manejarConfirmacion(respuesta) {
      if (respuesta === "sí") {
        // Enviar confirmación positiva al servidor
        fetch("/confirmar_respuesta", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(datosEsperandoConfirmacion),
        })
          .then((response) => response.json())
          .then((data) => {
            agregarMensajeIA(data.mensaje);
            esperandoConfirmacion = false; // Finalizar el proceso de confirmación
            datosEsperandoConfirmacion = null;
          })
          .catch((error) => {
            console.error("Error al confirmar la respuesta:", error);
          });
      } else if (respuesta === "no") {
        // Notificar rechazo y pedir corrección o más intentos
        fetch("/rechazar_respuesta", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(datosEsperandoConfirmacion),
        })
          .then((response) => response.json())
          .then((data) => {
            agregarMensajeIA(data.mensaje);
            esperandoConfirmacion = data.intentos_pendientes > 0; // Continuar si quedan intentos
            if (!esperandoConfirmacion) datosEsperandoConfirmacion = null;
          })
          .catch((error) => {
            console.error("Error al rechazar la respuesta:", error);
          });
      } else {
        agregarMensajeIA(
          "Por favor, responde con 'sí' para confirmar o 'no' para rechazar."
        );
      }
    }
  }

  function agregarMensajeUsuario(mensaje) {
    const mensajeElemento = document.createElement("div");
    mensajeElemento.innerHTML = `<span style="color: blue;">[${nombreUsuario}]:</span><br><br>${mensaje}`;
    mensajeElemento.classList.add("mensaje-usuario");
    mensajes.appendChild(mensajeElemento);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  function agregarMensajeIA(respuesta) {
    const mensajeElemento = document.createElement("div");
    mensajeElemento.innerHTML = `<span style="color: #FF00AB;">[Clark]:</span><br><br>${respuesta}`;
    mensajeElemento.classList.add("mensaje-ia");
    mensajes.appendChild(mensajeElemento);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  function mostrarListaArchivos(archivos) {
    let listaHTML = "<ul>";
    archivos.forEach((archivo, index) => {
      listaHTML += `<li>${index + 1}. ${archivo}</li>`;
    });
    listaHTML += "</ul>";
    agregarMensajeIA(
      "Selecciona un número de archivo para ver su contenido:\n" + listaHTML
    );
  }
});
