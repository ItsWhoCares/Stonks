let input = document.getElementById("searchBar");
let UL = document.getElementById("results");

function box_focus() {
  document.getElementById("topbar__searchbar").style.boxShadow =
    "rgba(0, 0, 0, 0.1) 0px 0px 30px 30px";
  console.log("focus");
}

function box_blur() {
  document.getElementById("topbar__searchbar").style.boxShadow = "none";
  console.log("blur");
}

async function fetch_res(symbol) {
  f;
}

function search() {
  if (input.value == "") {
    UL.style.display = "none";
    return;
  }
  UL.style.display = "flex";
  fetch(`/search/${input.value}`)
    .then((response) => response.json())
    .then((data) => {
      UL.innerHTML = "";
      for (let i = 0; i < data.length; i++) {
        UL.innerHTML += `<li><a href="/stocks/${data[i]["symbol"]}"><h4>${data[i]["symbol"]}</h4><h6>${data[i]["name"]}</h6></a></li>`;
      }
    });
}
let SearchBar = document.getElementById("searchBar");
SearchBar.addEventListener("input", search);
