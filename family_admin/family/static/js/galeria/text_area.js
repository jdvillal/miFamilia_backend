const textAreas = Array.from(document.getElementsByClassName("text-area-galeria"));

textAreas.forEach(ta =>{

  ta.onkeydown = e=>{
    if (e.which == 13){
      return false;
    }
  }
  ta.oninput = e=>{
    const noLineBreaks = ta.value.replace(/(\r\n|\n|\r)/gm,"");
    ta.value = noLineBreaks;
  }

});
