const update_imagen = (id, titulo, descripcion, imgSrc) => {
  $('#collapseCardExampleEditarImagen').collapse('show')
  document.getElementById("titulo_imagen").value = titulo;
  document.getElementById("descripcion_imagen").value = descripcion;
  document.getElementById("id").value = id;
  const image = document.getElementById("imagenGaleriaMostrar");
  image.src = imgSrc;
  console.log(imgSrc)

  const imageInput = document.getElementById("imagen");
  imageInput.onchange = () => {

    const fileList = imageInput.files;
    imgFileToUrl(fileList[0]).then(imgUrl => {
      validateResolution(imgUrl, {min_width: 800, min_height: 800}).then(valid => {
        if (valid) image.src = imgUrl;
        else imageInput.files = new DataTransfer().files;
      })
    })

  }
}

const update_video = (id, titulo, descripcion, fecha) => {
  $('#collapseCardExampleEditarVideo').collapse('show');
  document.getElementById("titulo_video").value = titulo;
  document.getElementById("descripcion_video").value = descripcion;
  document.getElementById("id_video").value = id;
}
