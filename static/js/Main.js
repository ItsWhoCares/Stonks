let logout = document.getElementById("logout");
logout.addEventListener("click", () => (location.href = "/logout"));

function updateBalance() {
  fetch("/getData/balance")
    .then((Response) => Response.json())
    .then((res) => {
      document.getElementById("balance").innerHTML = `${res["balance"]}`;
    });
}

async function deleteBookmark(r, symbol) {
  var i = r.parentNode.parentNode.rowIndex;
  table = document.getElementById("bookmarkstable");
  table.deleteRow(i);
  if (table.rows.length - 1 == 0) {
    table.remove();
    document.getElementById("error").style.display = null;
    //location.reload();
  }
  await fetch(`/bookmark/${symbol}`);
}

async function deleteRow(r) {
  var i = r.parentNode.parentNode.rowIndex;
  table = document.getElementById("bookmarkstable");
  table.deleteRow(i);
  if (table.rows.length - 1 == 0) {
    table.remove();
    document.getElementById("error").style.display = null;
    //location.reload();
  }
}
