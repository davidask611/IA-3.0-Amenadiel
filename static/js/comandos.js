window.addEventListener("DOMContentLoaded", () => {
  const fechaHoraElement = document.getElementById("fechaHora");
  const botonEnviar = document.getElementById("botonEnviar");
  const inputMensaje = document.getElementById("inputMensaje");
  const mensajes = document.getElementById("mensajes");
  let modo_administrador = window.modo_administrador || false;
  const maxFileSize = modo_administrador ? Infinity : 5 * 1024 * 1024; // No hay límite para admin, 10 MB para usuarios
  const botonSubirArchivo = document.getElementById("botonSubirArchivo");
  const archivoInput = document.getElementById("archivoInput");

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
      console.log("Modo administrador desactivado");
      agregarMensajeIA("Modo usuario activado");
    }
  });

  function enviarMensaje() {
    const mensaje = inputMensaje.value.trim();

    if (mensaje.length > 300) {
      alert("El mensaje no puede superar los 300 caracteres.");
      return;
    }

    if (mensaje) {
      if (esperandoConfirmacion) {
        manejarConfirmacion(mensaje.toLowerCase());
        return;
      }

      if (!nombreUsuario) {
        nombreUsuario = mensaje;
        agregarMensajeIA(
          `¡Un placer, ${nombreUsuario}! Puedes preguntarme algo o decirme 'activar modo administrador' para ingresar al modo administrador.`
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
              mostrarListaArchivos(data.archivos);
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
              agregarMensajeIA(data.respuesta);
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

      // Si el mensaje no corresponde a "ver datos" ni a una selección, procesarlo como normal
      console.log("Procesando mensaje como interacción normal...");
    }
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
        if (data.solicita_confirmacion) {
          esperandoConfirmacion = true;
          agregarMensajeIA(data.respuesta);
        } else {
          agregarMensajeIA(data.respuesta);
        }
      })
      .catch((error) => {
        console.error("Error al contactar con la IA:", error);
      });
  }
  //
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
    console.log("Archivo seleccionado:", archivo.name, "Tamaño:", archivo.size);

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
  function manejarConfirmacion(respuesta) {
    if (respuesta === "sí") {
      agregarMensajeIA("Confirmación recibida. Continuando...");
    } else if (respuesta === "no") {
      agregarMensajeIA("Confirmación negativa. Acción cancelada.");
    } else {
      agregarMensajeIA(
        "No entendí tu respuesta. Por favor, responde 'sí' o 'no'."
      );
      return;
    }
    esperandoConfirmacion = false;
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
