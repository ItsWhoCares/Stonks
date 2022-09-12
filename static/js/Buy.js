async function buyConfirm(symbol) {
  quantity = Math.floor(document.getElementById("buy_input").value);
  if (quantity == 0) {
    document.getElementById("buy_input").style.border =
      "1px solid rgb(244, 84, 133)";
    return;
  } else {
    document.getElementById("buy_input").style = null;
  }

  let stockPrice = 0;
  await fetch(`/latest_price/${symbol}`)
    .then((response) => response.json())
    .then((data) => (stockPrice = parseFloat(data)));
  value = Math.round(stockPrice * quantity * 100) / 100;

  document.getElementById("confirmbox").innerHTML = `<h3>
  Are you sure you want to buy ${quantity} shares of ${symbol} for
  <span style="font-weight: bold" id="confirmboxvalue">${value}</span> dollars
  </h3>
  <div>
    <button class="stockPage__buy-button" onclick="buyStock(${quantity},'${symbol}')">CONFIRM</button>
    <button class="stockPage__buy-button cancel" onclick="blackbg.style = 'display: none';
    confirmbox.style = 'display: none';">CANCEL</button>
  </div>`;
  document.getElementById("blackbg").style = null;
  document.getElementById("confirmbox").style = null;
}

function buyStock(quantity, symbol) {
  //quantity = Math.floor(document.getElementById("buy_input").value);
  // console.log(symbol);
  // console.log(quantity);

  fetch(`/buyStock/${symbol}/${quantity}`)
    .then((Response) => Response.json())
    .then((res) => {
      if (res["status"] == "Failure") {
        confirmbox.innerHTML = `<h3><span style="font-weight: bold">${res["errorMsg"]}</span></h3>
      <div>
        <button class="stockPage__buy-button cancel" onclick="blackbg.style = 'display: none';
        confirmbox.style = 'display: none';">CLOSE</button>
      </div>`;
      } else {
        blackbg.style = "display: none";
        confirmbox.style = "display: none";
        updateBalance();
      }
    });
}
