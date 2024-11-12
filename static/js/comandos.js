window.addEventListener("DOMContentLoaded", () => {
  const fechaHoraElement = document.getElementById("fechaHora");
  const botonEnviar = document.getElementById("botonEnviar");
  const inputMensaje = document.getElementById("inputMensaje");
  const mensajes = document.getElementById("mensajes");

  let esperandoClaveAdmin = false; // Variable para controlar si se está esperando la clave de admin
  let modoAdministrador = false; // Estado del modo administrador
  let nombreUsuario = ""; // Nombre del usuario
  let usuarioAdmin = ""; // Almacenará el usuario ingresado para admin
  let archivoSeleccionado = []; // Para almacenar la lista de archivos JSON
  let listaMostrada = false; // Bandera para verificar si ya se mostró la lista de archivos
  let esperandoSeleccionArchivo = false; // Indica si se está esperando la selección de un archivo

  // Función para mostrar la hora y fecha
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
  setInterval(actualizarFechaHora, 60000); // Actualizar la hora cada minuto

  // Saludo de bienvenida cuando se carga la página
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
          agregarMensajeIA(
            "Usuario o clave incorrectos. Intenta nuevamente."
          );
          console.log("Usuario o clave incorrectos");
          esperandoClaveAdmin = true;
        }
        usuarioAdmin = "";
        return;
      }

      // Lógica para ver los archivos JSON cuando el modo admin está activado
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
              console.log("Archivos JSON recibidos:", data.archivos);
              archivoSeleccionado = data.archivos; // Guardamos la lista de archivos
              mostrarListaArchivos(data.archivos); // Muestra la lista
              listaMostrada = true; // Marcamos que ya se mostró la lista
              esperandoSeleccionArchivo = true; // Ahora esperamos que se seleccione un archivo
            } else {
              agregarMensajeIA(data.respuesta);
              console.log("Error al recibir los archivos JSON:", data.respuesta);
            }
          })
          .catch((error) => {
            console.error("Error al contactar con la IA:", error);
          });
        return;
      }

      // Verifica si el mensaje es un número válido y lo usa para seleccionar un archivo
      const numeroSeleccionado = parseInt(mensaje);
      if (
        esperandoSeleccionArchivo &&
        archivoSeleccionado &&
        !isNaN(numeroSeleccionado) &&
        numeroSeleccionado > 0 &&
        numeroSeleccionado <= archivoSeleccionado.length
      ) {
        const archivo = archivoSeleccionado[numeroSeleccionado - 1]; // Restar 1 para índice basado en cero
        console.log(`Archivo seleccionado: ${archivo}`);

        // Solicita el contenido del archivo
        fetch("/ver_contenido", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ archivo: archivo }),
        })
          .then((response) => response.json())
          .then((data) => {
            agregarMensajeIA(data.respuesta); // Muestra el contenido del archivo
            esperandoSeleccionArchivo = false; // Después de mostrar el contenido, deshabilitamos la espera
          })
          .catch((error) => {
            console.error("Error al contactar con el backend:", error);
          });
        return;
      }

      // Si no se ha seleccionado un archivo o no se reconoce el número, responde al usuario
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
        es_administrador: modoAdministrador,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        agregarMensajeIA(data.respuesta);
      })
      .catch((error) => {
        console.error("Error al contactar con la IA:", error);
      });
  }

  // Función para agregar el mensaje del usuario al chat
  function agregarMensajeUsuario(mensaje) {
    const mensajeElemento = document.createElement("div");
    mensajeElemento.innerHTML = `[${nombreUsuario}]:<br><br>${mensaje}`;
    mensajeElemento.classList.add("mensaje-usuario");
    mensajes.appendChild(mensajeElemento);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  // Función para agregar la respuesta de la IA al chat
  function agregarMensajeIA(respuesta) {
    const mensajeElemento = document.createElement("div");
    mensajeElemento.innerHTML = `[Clark]:<br><br>${respuesta}`;
    mensajeElemento.classList.add("mensaje-ia");
    mensajes.appendChild(mensajeElemento);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  // Mostrar lista de archivos JSON numerados
  function mostrarListaArchivos(archivos) {
    let listaHTML = "<ul>";
    archivos.forEach((archivo, index) => {
      listaHTML += `<li>${index + 1}. ${archivo}</li>`; // Mostrar número y archivo
    });
    listaHTML += "</ul>";
    agregarMensajeIA("Selecciona un número de archivo para ver su contenido:\n" + listaHTML);
  }

});
