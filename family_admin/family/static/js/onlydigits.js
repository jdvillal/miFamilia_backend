const onlyDigitsInputs = Array.from(document.getElementsByClassName("only-digits-input"));


function is_number(char) {{
    return !isNaN(parseInt(char));
}}

onlyDigitsInputs.forEach(odi=>{
  odi.oninput= () =>{
    const value = odi.value;
    if (value.length === 0)return;

    const lastChar = value[value.length-1];
    if (is_number(lastChar))return;
    odi.value = value.substring(0,value.length-1);
    
  }
})
