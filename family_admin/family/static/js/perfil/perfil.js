const cancelarConfigButton = document.getElementById("consfigurationResetButton")

const fotoPerfil = document.getElementById("fotoPerfil");
const fotoPerfilWrapper = document.getElementById("fotoPerfilWrapper");
const cambaiarFotoButtonWrapper = document.getElementById("cambaiarFotoButtonWrapper");
const cambaiarFotoButton = cambaiarFotoButtonWrapper.children[0];


const imagenPerfilInput = document.getElementById("imagenPerfilInput");

const oldImageSrc = fotoPerfil.src;

cancelarConfigButton.onclick = ()=>{
  fotoPerfil.src = oldImageSrc;
}

fotoPerfilWrapper.onmouseenter = () => {
  cambaiarFotoButtonWrapper.classList.remove("d-none");
  cambaiarFotoButtonWrapper.classList.add("d-flex");
}
fotoPerfilWrapper.onmouseleave = () => {
  cambaiarFotoButtonWrapper.classList.remove("d-flex");
  cambaiarFotoButtonWrapper.classList.add("d-none");
}


cambaiarFotoButton.onclick = function () {
  imagenPerfilInput.click();

}

function imgFileToUrl(imgFile) {
  const reader = new FileReader();
  const promise = new Promise((resolve, reject) => {
    reader.addEventListener('load', (event) => {
      const imageUrl = event.target.result;
      resolve(imageUrl);
    });
    reader.onerror = reject;
  });
  reader.readAsDataURL(imgFile);
  return promise;
}

function validateResolution(imageUrl, {min_width = 0, max_width = Infinity, min_height = 0, max_height = Infinity}) {
  const promise = new Promise((resolve, reject) => {
    imageSize(imageUrl).then(dim => {
      if (dim.width < min_width) resolve(false);
      if (dim.width > max_width) resolve(false);
      if (dim.height < min_height) resolve(false);
      if (dim.height > max_height) resolve(false);
      resolve(true);
    }).catch(()=>reject());
  });
  return promise;
}

imagenPerfilInput.onchange = () => {
  const fileList = imagenPerfilInput.files;
  imgFileToUrl(fileList[0]).then(imgUrl => {
    validateResolution(imgUrl, {min_width: 200, min_height: 200}).then(valid => {
      if (valid) fotoPerfil.src = imgUrl;
      else imagenPerfilInput.files = new DataTransfer().files;
    })
  })

}


function imageSize(url) {
  const img = document.createElement("img");

  const promise = new Promise((resolve, reject) => {
    img.onload = () => {
      const width = img.naturalWidth;
      const height = img.naturalHeight;

      resolve({width, height});
    };

    img.onerror = reject;
  });

  img.src = url;

  return promise;
}




