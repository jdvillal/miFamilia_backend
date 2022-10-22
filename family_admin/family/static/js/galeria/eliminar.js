const eliminar_imagen = (id, tipo) => {
    console.log(id, tipo)
    document.getElementById(`btn_${id}`).disabled = true

    let req = {
        id: id,
        tipo: tipo,
    }

    fetch('eliminar_galeria_pk', {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(req),
    }).then(res => res.json())
        .then(json => {
            const mess = json.mensaje
            //document.getElementById(`btn_${id}`).disabled = false
            document.getElementById('mess_eliminar_galeria').innerHTML = mess
            $('#exampleModal_galeria_mensaje').modal()

        })
}

const reloadPaage = () => {
    window.location.reload()
}