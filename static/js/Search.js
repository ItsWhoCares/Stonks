function box_focus() {
  document.getElementById("topbar__searchbar").style.boxShadow =
    "rgba(0, 0, 0, 0.1) 0px 0px 30px 30px";
  console.log("focus");
}

function box_blur() {
  document.getElementById("topbar__searchbar").style.boxShadow = "none";
  console.log("blur");
}

// SearchBar = document.getElementById("searchBar");
// SearchBar.addEventListener()
