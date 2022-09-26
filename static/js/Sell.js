function sellStock(symbol, tid, r) {
  fetch(`/sellStock/${symbol}/${tid}`)
    .then((Response) => Response.json())
    .then((res) => {
      if (res["status"] == "Failure") {
        errorPopup.style = null;
      } else {
        updateBalance();
        deleteRow(r);
      }
    });
}
