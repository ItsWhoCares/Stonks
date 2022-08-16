var ctx = document.getElementById("stock_chart").getContext("2d");
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

let symbol;
let stock_labels = [];
let stock_data = [];

const params = new URLSearchParams(window.location.search);
symbol = params.get("q");
async function getOneDayChart() {
  return new Promise(async function (resolve) {
    var response = await fetch(`/OneDayChart?symbol=${symbol}`);
    var res_data = await response.json();
    stock_labels = res_data["labels"];
    stock_data = res_data["data"];
    // console.log(data["labels"]);
    resolve();
  });
}

function drawchart() {
  var stock_chart = new Chart(ctx, {
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
          left: 25,
        },
      },
      tooltips: {
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
            gridLines: {
              color: "rgba(0, 0, 0, 0)",
            },
            fontStyle: "bold",

            ticks: {
              callback(value) {
                return "$" + value.toFixed(2);
              },
              autoSkipPadding: 5,
            },
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

getOneDayChart().then(function () {
  drawchart();
});

// console.log(stock_data);

// setTimeout(() => {
//   , 5000);
// function printhehe() {
//   console.log("Resized");
// }
window.addEventListener("resize", drawchart);
