function changeURL(title, OldurlPath, NewurlPath) {
  NewurlPath = OldurlPath.split("/trends")[0] + "/trends" + NewurlPath;
  // console.log(NewurlPath);
  document.title = title;
  window.history.pushState(
    { html: "topLosers", pageTitle: title },
    "",
    NewurlPath
  );
}

function topGainers() {
  fetch("/getData/topGainers")
    .then((response) => response.json())
    .then((topgainers) => {
      list = document.getElementById("stocks");
      list.innerHTML = "";
      for (let i in topgainers) {
        list.innerHTML += `<li>
        <a href="/stocks/${topgainers[i]["Symbol"]}"
          ><span class="panel__fullname"
          style="width: 20%;"
            ><h4>${topgainers[i]["Symbol"]}</h4>
            <h6 class="panel__name">${topgainers[i]["CompanyName"]}</h6></span
          >
          <div class="panel__list-change">
            <canvas
              id="stock_chart_${topgainers[i]["Symbol"]}"
              class="chartjs-render-monitor"
              height="33px"
              width="200px"
            ></canvas>
          </div>
          
          <div class="panel__list-change" style="width: 45px;">
            <h4>$${topgainers[i]["LatestPrice"]}</h4>
            
            <h5
              id="${topgainers[i]["Symbol"]}_changeNegative"
              style="
                color: rgb(244, 84, 133);
                margin: 5px 0px 0px;
                text-shadow: rgba(244, 84, 133, 0.5) 0px 0px
                  7px;
              "
            >
              ${topgainers[i]["Change"]}%
            </h5>
            
            <h5 id="${topgainers[i]["Symbol"]}_changePositive" style="display: none;color: rgb(102, 249, 218); margin: 5px 0px 0px; text-shadow: rgba(102, 249, 218, 0.5) 0px 0px 7px;">+${topgainers[i]["Change"]}%</h5>
            
          </div>
          <div class="panel__list-change"  style="width: 45px; margin-right: 50px">
            <h4 style="color: rgb(102, 249, 218); margin: 5px 0px 0px; text-shadow: rgba(102, 249, 218, 0.5) 0px 0px 7px;">$${topgainers[i]["52 Week High"]}</h4>
          </div><div class="panel__list-change"  style="width: 45px; padding-right: 40px;">
            <h4 style="
            color: rgb(244, 84, 133);
            margin: 5px 0px 0px;
            text-shadow: rgba(244, 84, 133, 0.5) 0px 0px
              7px;
          ">$${topgainers[i]["52 Week Low"]}</h4>
          </div>

          </a
        >
      </li>`;
        if (topgainers[i]["Change"] > 0) {
          document.getElementById(
            `${topgainers[i]["Symbol"]}_changeNegative`
          ).style.display = "none";
          document.getElementById(
            `${topgainers[i]["Symbol"]}_changePositive`
          ).style.display = null;
        }
      }
      changeURL("Top Gainers", window.location.href, "/topGainers");
      document.getElementById("Losers").classList.remove("active");
      document.getElementById("Gainers").classList.add("active");
      document.getElementById("Volume").classList.remove("active");
    });
}

function topLosers() {
  fetch("/getData/topLosers")
    .then((response) => response.json())
    .then((toplosers) => {
      list = document.getElementById("stocks");
      list.innerHTML = "";
      for (let i in toplosers) {
        list.innerHTML += `<li>
        <a href="/stocks/${toplosers[i]["Symbol"]}"
          ><span class="panel__fullname"
          style="width: 20%;"
            ><h4>${toplosers[i]["Symbol"]}</h4>
            <h6 class="panel__name">${toplosers[i]["CompanyName"]}</h6></span
          >
          <div class="panel__list-change">
            <canvas
              id="stock_chart_${toplosers[i]["Symbol"]}"
              class="chartjs-render-monitor"
              height="33px"
              width="200px"
            ></canvas>
          </div>
          
          <div class="panel__list-change" style="width: 45px;">
            <h4>$${toplosers[i]["LatestPrice"]}</h4>
            
            <h5
              id="${toplosers[i]["Symbol"]}_changeNegative"
              style="
                color: rgb(244, 84, 133);
                margin: 5px 0px 0px;
                text-shadow: rgba(244, 84, 133, 0.5) 0px 0px
                  7px;
              "
            >
              ${toplosers[i]["Change"]}%
            </h5>
            
            <h5 id="${toplosers[i]["Symbol"]}_changePositive" style="display: none;color: rgb(102, 249, 218); margin: 5px 0px 0px; text-shadow: rgba(102, 249, 218, 0.5) 0px 0px 7px;">+${toplosers[i]["Change"]}%</h5>
            
          </div>
          <div class="panel__list-change"  style="width: 45px; margin-right: 50px">
            <h4 style="color: rgb(102, 249, 218); margin: 5px 0px 0px; text-shadow: rgba(102, 249, 218, 0.5) 0px 0px 7px;">$${toplosers[i]["52 Week High"]}</h4>
          </div><div class="panel__list-change"  style="width: 45px; padding-right: 40px;">
            <h4 style="
            color: rgb(244, 84, 133);
            margin: 5px 0px 0px;
            text-shadow: rgba(244, 84, 133, 0.5) 0px 0px
              7px;
          ">$${toplosers[i]["52 Week Low"]}</h4>
          </div>

          </a
        >
      </li>`;
        if (toplosers[i]["Change"] > 0) {
          document.getElementById(
            `${toplosers[i]["Symbol"]}_changeNegative`
          ).style.display = "none";
          document.getElementById(
            `${toplosers[i]["Symbol"]}_changePositive`
          ).style.display = null;
        }
      }
      changeURL("Top Losers", window.location.href, "/topLosers");
      document.getElementById("Gainers").classList.remove("active");
      document.getElementById("Losers").classList.add("active");
      document.getElementById("Volume").classList.remove("active");
    });
}

function topVolume() {
  fetch("/getData/topVolume")
    .then((response) => response.json())
    .then((topVolume) => {
      list = document.getElementById("stocks");
      list.innerHTML = "";
      for (let i in topVolume) {
        list.innerHTML += `<li>
        <a href="/stocks/${topVolume[i]["Symbol"]}"
          ><span class="panel__fullname"
          style="width: 20%;"
            ><h4>${topVolume[i]["Symbol"]}</h4>
            <h6 class="panel__name">${topVolume[i]["CompanyName"]}</h6></span
          >
          <div class="panel__list-change">
            <canvas
              id="stock_chart_${topVolume[i]["Symbol"]}"
              class="chartjs-render-monitor"
              height="33px"
              width="200px"
            ></canvas>
          </div>
          
          <div class="panel__list-change" style="width: 45px;">
            <h4>$${topVolume[i]["LatestPrice"]}</h4>
            
            <h5
              id="${topVolume[i]["Symbol"]}_changeNegative"
              style="
                color: rgb(244, 84, 133);
                margin: 5px 0px 0px;
                text-shadow: rgba(244, 84, 133, 0.5) 0px 0px
                  7px;
              "
            >
              ${topVolume[i]["Change"]}%
            </h5>
            
            <h5 id="${topVolume[i]["Symbol"]}_changePositive" style="display: none;color: rgb(102, 249, 218); margin: 5px 0px 0px; text-shadow: rgba(102, 249, 218, 0.5) 0px 0px 7px;">+${topVolume[i]["Change"]}%</h5>
            
          </div>
          <div class="panel__list-change"  style="width: 45px; margin-right: 50px">
            <h4 style="color: rgb(102, 249, 218); margin: 5px 0px 0px; text-shadow: rgba(102, 249, 218, 0.5) 0px 0px 7px;">$${topVolume[i]["52 Week High"]}</h4>
          </div><div class="panel__list-change"  style="width: 45px; padding-right: 40px;">
            <h4 style="
            color: rgb(244, 84, 133);
            margin: 5px 0px 0px;
            text-shadow: rgba(244, 84, 133, 0.5) 0px 0px
              7px;
          ">$${topVolume[i]["52 Week Low"]}</h4>
          </div>

          </a
        >
      </li>`;
        if (topVolume[i]["Change"] > 0) {
          document.getElementById(
            `${topVolume[i]["Symbol"]}_changeNegative`
          ).style.display = "none";
          document.getElementById(
            `${topVolume[i]["Symbol"]}_changePositive`
          ).style.display = null;
        }
      }
      changeURL("Top By Volume", window.location.href, "/topVolume");
      document.getElementById("Losers").classList.remove("active");
      document.getElementById("Gainers").classList.remove("active");
      document.getElementById("Volume").classList.add("active");
    });
}
