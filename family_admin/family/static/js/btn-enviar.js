const btns = Array.from(document.getElementsByClassName("btn-enviar"));

btns.forEach(btn => {
  const old_onclick = btn.onclick;//enviar fomulario

  btn.onclick = () => {
    old_onclick();

    btn.disabled = true;
  }
});
