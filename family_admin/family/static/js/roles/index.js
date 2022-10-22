const handleSubmit = (rol) => {
  const table_body = document.querySelector(`#${rol}_table tbody`);
  const table_head = document.querySelector(`#${rol}_table thead tr`);

  let req = {};

  for (let row of table_body.children) {
    const columnas = row.children;
    req[columnas[0].innerText] = {};

    for (let i = 1; i < columnas.length; i++) {
      const col = columnas[i];
      const col_checked =col.getElementsByTagName("input")[0].checked
      const permiso = table_head.children[i].innerText;
      req[columnas[0].innerText][permiso] = col_checked;
    }
  }
  req.rol = rol;
  console.log(req)

  const url = document.getElementById(`${rol}_table`).dataset.saveurl;
  fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  })
    .then((response) => {
      console.log(response);
      return response.json();
    })
    .then((data) => {
      const mess = data.mensaje;
      document.getElementById(`mess_${rol}`).innerHTML = mess;
      $(`#exampleModal_${rol}_mensaje`).modal();
    });
};

const handleDelete = (rol) => {
  const rol_element = document.getElementById(`${rol}_tag`);
  const url = document.getElementById(`${rol}_table`).dataset.deleteurl;
  // console.log(document.getElementById(`${rol}_table`).dataset)
  const request_data = {rol:rol};

  fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request_data),
  })
    .then(response => response.json())
    .then(data => {
      const mess = data.mensaje;
      document.getElementById(`mess_eliminado`).innerHTML = mess;
      $(`#exampleModal_eliminado`).modal();
      if (data.status === 201){
        rol_element.parentNode.removeChild(rol_element);
      }
    });
}
const deleteRolBtns = Array.from(document.getElementsByClassName("btn-eliminar-rol"));


deleteRolBtns.forEach(btn => {
  btn.onclick = e=> {
    e.preventDefault();
    e.stopImmediatePropagation();
    const rol = btn.dataset.rol;
    $(`#modal_eliminar_${rol}`).modal();
    $(`#collapse_${rol}`).collapse('show')
  }
  
})


