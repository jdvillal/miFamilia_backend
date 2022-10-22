window.addEventListener("load", () => {
  $("#exampleModal_usuario_rol_mensaje").modal();
});

const deleteBtns = Array.from(document.getElementsByClassName("btn-eliminar-usuario"));


deleteBtns.forEach(btn => {
  btn.onclick = e => {
    e.preventDefault();
    e.stopImmediatePropagation();
    const usuario = btn.dataset.usuario;
    $(`#modal_eliminar_${usuario}`).modal();
    $(`#collapse_${usuario}`).collapse('show')
  }

})


const senddeleteBtns = Array.from(document.getElementsByClassName("btn-send-eliminar-usuario"));
senddeleteBtns.forEach(btn => {
  btn.onclick = e => {
    const eliminarurl = btn.dataset.eliminarurl
    const usuario = btn.dataset.usuario
    const tarjeta_usuario = document.getElementById(`tarjeta-${usuario}`);
    // hacer el requerimineto
    fetch(eliminarurl, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      body: JSON.stringify({})
      }
    })
    .then(res=>res.json())
    .then(res=>{
      console.log(res.status, res.mess);

      tarjeta_usuario.parentNode.removeChild(tarjeta_usuario);
      document.getElementById("mess_eliminar_usuario").innerText = res.mess;
      $("#modalEliminarUsuarioMensaje").modal()
    })
    // mostrar el resultados
    // eliminar el objeto del html
  }
})
