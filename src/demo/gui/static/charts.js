document.addEventListener("DOMContentLoaded", () => {
  const MAX_POINTS = 20;

  const timesEl = document.getElementById("timesChart");
  const bwEl = document.getElementById("bandwidthChart");

  if (!timesEl || !bwEl) {
    console.error("Canvas elements not found. Check IDs in index.html.");
    return;
  }

  const timesChart = new Chart(timesEl.getContext("2d"), {
    type: "line",
    data: { labels: [], datasets: [
      { label: "Transcoder (s)", data: [], borderColor: "red", fill: false },
      { label: "Decoder (s)", data: [], borderColor: "blue", fill: false },
    ]},
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });

  const bandwidthChart = new Chart(bwEl.getContext("2d"), {
    type: "bar",
    data: { labels: [], datasets: [
      { label: "Segment size (Mbit)", data: [], borderColor: "green", fill: true },
    ]},
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });

    let history = [];

    socket.on("update_data", (data) => {
    const label = new Date().toLocaleTimeString();
    const bwMbps = (data.bandwidth || 0) * 8 / 1024 ** 2;

    // Append sample
    history.push({
        label,
        t_transcode: data.t_transcode ?? 0,
        t_decode: data.t_decode ?? 0,
        bandwidth: bwMbps
    });

    // Trim to MAX_POINTS
    if (history.length > MAX_POINTS) {
        history = history.slice(-MAX_POINTS);
    }

    // Rebuild timesChart
    timesChart.data.labels = history.map(d => d.label);
    timesChart.data.datasets[0].data = history.map(d => d.t_transcode);
    timesChart.data.datasets[1].data = history.map(d => d.t_decode);
    timesChart.update("none");

    // Rebuild bandwidthChart
    bandwidthChart.data.labels = history.map(d => d.label);
    bandwidthChart.data.datasets[0].data = history.map(d => d.bandwidth);
    bandwidthChart.update("none");
    });

});