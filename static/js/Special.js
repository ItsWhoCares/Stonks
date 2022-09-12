function addCredit() {
  fetch("/addCredits")
    .then((Response) => Response.json())
    .then((res) => {
      if (res["msg"] != "Error") {
        alert(res["msg"]);
      }
      updateBalance();
    });
}
