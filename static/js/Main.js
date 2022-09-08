let logout = document.getElementById("logout");
logout.addEventListener("click", () => (location.href = "/logout"));

function checkpagli(usersname) {
  console.log(usersname);
  if (
    username.toLowerCase() == "nandini" ||
    username.toLowerCase() == "nandu"
  ) {
    while (!confirm("Are You Pagal ?")) {
      alert("Welcome Pagli 😝");
    }
  }
}
