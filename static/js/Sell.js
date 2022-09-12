function sellStock(symbol, tid) {
  fetch(`/sellStock/${symbol}/${tid}`)
    .then((Response) => Response.json())
    .then((res) => {
      if (res["status"] == "Failure") {
        alert(`Could not sell stock (${symbol})`);
        console.log(res);
      } else {
        updateBalance();
      }
    });
}
