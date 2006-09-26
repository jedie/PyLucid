function check() {
  if (document.data.pass1.value != document.data.pass2.value) {
    alert("Passwort verfication fail! password 1 != password 2");
    return false;
  }
  if (document.data.pass1.value.length <= 7) {
    alert("For security, min. password length is 8 chars!");
    return false;
  }
  if (document.data.email.value.indexOf("@") == -1) {
    alert("Need a valid eMail adress (for password recovery.)");
    return false;
  }
  return true;
}