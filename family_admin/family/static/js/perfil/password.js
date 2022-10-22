const submiitChangPass = document.getElementById("sendChangePass")

const inputPassUserConf = document.getElementById("password");
const inputPass2UserConf = document.getElementById("password2");

const validations = {
  password: true,
};

submiitChangPass.ableToSend = () => {
  return validations.password;
}


inputPassUserConf.onkeyup = () => {
  const pass1 = inputPassUserConf.value;
  const pass2 = inputPass2UserConf.value;
  console.log(pass1, pass2)
  if (pass1 !== pass2) validations.password = false;
  else if (pass1.length < 10) validations.password = false;
  else validations.password = true;

  submiitChangPass.disabled = !submiitChangPass.ableToSend()
}

inputPass2UserConf.onkeyup = inputPassUserConf.onkeyup
