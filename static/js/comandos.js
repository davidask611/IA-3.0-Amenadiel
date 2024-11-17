window.addEventListener("DOMContentLoaded", () => {
  const fechaHoraElement = document.getElementById("fechaHora");
  const botonEnviar = document.getElementById("botonEnviar");
  const inputMensaje = document.getElementById("inputMensaje");
  const mensajes = document.getElementById("mensajes");

  let esperandoClaveAdmin = false;
  let modoAdministrador = false;
  let nombreUsuario = "";
  let usuarioAdmin = "";
  let archivoSeleccionado = [];
  let listaMostrada = false;
  let esperandoSeleccionArchivo = false;
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
    if (modoAdministrador) {
      modoAdministrador = false;
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
          modoAdministrador = true;
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

      if (mensaje.toLowerCase() === "ver datos" && modoAdministrador) {
        console.log("Solicitando lista de archivos JSON...");
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
              esperandoSeleccionArchivo = true;
            } else {
              agregarMensajeIA(data.respuesta);
            }
          })
          .catch((error) => {
            console.error("Error al contactar con la IA:", error);
          });
        return;
      }

      const numeroSeleccionado = parseInt(mensaje);
      if (
        esperandoSeleccionArchivo &&
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
            esperandoSeleccionArchivo = false;
          })
          .catch((error) => {
            console.error("Error al contactar con el backend:", error);
          });
        return;
      }

      if (esperandoSeleccionArchivo) {
        agregarMensajeIA(
          "Por favor, selecciona un número de archivo para ver su contenido."
        );
      }
    }

    fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        mensaje: mensaje,
        modo_administrador: modoAdministrador,
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
