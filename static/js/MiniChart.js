async function createChart(symbol) {
  var ctx = document.getElementById(`stock_chart_${symbol}`).getContext("2d");
  const gradient = ctx.createLinearGradient(0, 0, 600, 10);
  gradient.addColorStop(0, "#7c83ff");
  gradient.addColorStop(1, "#7cf4ff");
  let gradientFill = ctx.createLinearGradient(0, 0, 0, 100);
  gradientFill.addColorStop(0, "rgba(124, 131, 255,.3)");
  gradientFill.addColorStop(0.2, "rgba(124, 244, 255,.15)");
  gradientFill.addColorStop(1, "rgba(255, 255, 255, 0)");
  ctx.shadowBlur = 5;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 4;

  getOneDayChart(symbol).then(function () {
    drawchart(ctx, gradient, gradientFill);
  });
}

function fetchTopGainersChart() {
  fetch("/getData/topGainers")
    .then((response) => response.json())
    .then((stocks) => {
      for (var i = 0; i < stocks.length; i++) {
        if (stocks[i] != null) {
          createChart(stocks[i]["Symbol"]);
        }
      }
    });
}

function fetchTopLosersChart() {
  fetch("/getData/topLosers")
    .then((response) => response.json())
    .then((stocks) => {
      for (var i = 0; i < stocks.length; i++) {
        if (stocks[i] != null) {
          createChart(stocks[i]["Symbol"]);
        }
      }
    });
}

function fetchTopVolumeChart() {
  fetch("/getData/topVolume")
    .then((response) => response.json())
    .then((stocks) => {
      for (var i = 0; i < stocks.length; i++) {
        if (stocks[i] != null) {
          createChart(stocks[i]["Symbol"]);
        }
      }
    });
}

fetchTopGainersChart();

// var ctx = document.getElementById("stock_chart").getContext("2d");
// const gradient = ctx.createLinearGradient(0, 0, 600, 10);
// gradient.addColorStop(0, "#7c83ff");
// gradient.addColorStop(1, "#7cf4ff");
// let gradientFill = ctx.createLinearGradient(0, 0, 0, 100);
// gradientFill.addColorStop(0, "rgba(124, 131, 255,.3)");
// gradientFill.addColorStop(0.2, "rgba(124, 244, 255,.15)");
// gradientFill.addColorStop(1, "rgba(255, 255, 255, 0)");
// ctx.shadowBlur = 5;
// ctx.shadowOffsetX = 0;
// ctx.shadowOffsetY = 4;

// let symbol;
let stock_labels = [];
let stock_data = [];
var chart;
// const params = new URLSearchParams(window.location.search);
// console.log(params);
// symbol = "aapl";
async function getOneDayChart(symbol) {
  return new Promise(async function (resolve) {
    var response = await fetch(`/OneDayChart/${symbol}`);
    try {
      var res_data = await response.json();
      stock_labels = res_data["labels"];
      stock_data = res_data["data"];
      resolve();
    } catch (e) {
      stock_labels = [];
      stock_data = [];
      resolve();
    }
  });
}

function drawchart(ctx, gradient, gradientFill) {
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: stock_labels,
      datasets: [
        {
          lineTension: 0.1,
          label: "",
          pointBorderWidth: 0,
          pointHoverRadius: 0,
          borderColor: gradient,
          backgroundColor: gradientFill,
          pointBackgroundColor: gradient,
          fill: true,
          borderWidth: 2,
          data: stock_data,
        },
      ],
    },
    options: {
      layout: {
        padding: {
          right: 25,
          left: 0, //left paddin of chart
        },
      },
      tooltips: {
        enabled: false,
        mode: "index",
        intersect: false,
        callbacks: {
          label(tooltipItems, data) {
            return `$${tooltipItems.yLabel}`;
          },
        },
        displayColors: false,
      },
      hover: {
        mode: "index",
        intersect: false,
        mode: null,
      },
      maintainAspectRatio: false,
      responsive: true,
      legend: {
        display: false,
      },
      scales: {
        xAxes: [
          {
            display: false,
          },
        ],
        fontStyle: "bold",
        yAxes: [
          {
            display: false,
          },
        ],
      },
      elements: {
        point: {
          radius: 0,
        },
        line: {
          borderCapStyle: "round",
          borderJoinStyle: "round",
        },
      },
    },
  });
}

// getOneDayChart().then(function () {
//   drawchart();
// });
