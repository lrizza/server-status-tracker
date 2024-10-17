const NUM_PROCESSES = 20; 

// Handle Dark Mode Toggle
const darkModeToggle = document.getElementById('dark-mode-toggle');
darkModeToggle.addEventListener('change', function() {
    if (this.checked) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
    }
});

if (localStorage.getItem('darkMode') === 'enabled') {
    darkModeToggle.checked = true;
    document.body.classList.add('dark-mode');
}

let cpuChart, memoryChart;

function setupCharts() {
    const ctxCpu = document.getElementById('cpuChart').getContext('2d');
    const ctxMemory = document.getElementById('memoryChart').getContext('2d');

    cpuChart = new Chart(ctxCpu, {
        type: 'line',
        data: {
            labels: [],  // Time labels
            datasets: [{
                label: 'CPU Usage (%)',
                data: [],
                borderColor: 'rgba(75,192,192,1)',
                backgroundColor: 'rgba(75,192,192,0.2)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: { display: false },
                y: { beginAtZero: true, max: 100 }
            }
        }
    });

    memoryChart = new Chart(ctxMemory, {
        type: 'line',
        data: {
            labels: [],  // Time labels
            datasets: [{
                label: 'RAM Usage (%)',
                data: [],
                borderColor: 'rgba(153,102,255,1)',
                backgroundColor: 'rgba(153,102,255,0.2)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: { display: false },
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
}

function fetchStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            const statusLight = document.getElementById('status-light');
            const statusText = document.getElementById('status-text');
            statusLight.classList.remove('green', 'red');
            statusLight.classList.add(data.status);
            statusText.textContent = data.status === 'green'
                ? `${data.computer_name} is ON`
                : `${data.computer_name} is OFF`;
        })
        .catch(error => console.error('Error fetching status:', error));
}

function fetchMemory() {
    fetch('/memory')
        .then(response => response.json())
        .then(data => {
            const totalMemoryGB = data.total / (1024 ** 3);
            const usedMemoryGB = data.used / (1024 ** 3);
            const freeMemoryGB = data.available / (1024 ** 3);
            document.getElementById('total-memory').textContent = totalMemoryGB.toFixed(2);
            document.getElementById('used-memory').textContent = usedMemoryGB.toFixed(2);
            document.getElementById('free-memory').textContent = freeMemoryGB.toFixed(2);
            document.getElementById('memory-percent').textContent = data.percent.toFixed(1);
        })
        .catch(error => console.error('Error fetching memory:', error));
}

function fetchProcesses() {
    fetch('/processes')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('process-table-body');
            tableBody.innerHTML = '';
            for (let i = 0; i < NUM_PROCESSES; i++) {
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                const cpuCell = document.createElement('td');
                const memoryCell = document.createElement('td');

                if (data[i]) {
                    nameCell.textContent = data[i].name;
                    cpuCell.textContent = data[i].cpu.toFixed(1);
                    memoryCell.textContent = data[i].memory.toFixed(1);
                } else {
                    nameCell.textContent = '';
                    cpuCell.textContent = '';
                    memoryCell.textContent = '';
                }

                row.appendChild(nameCell);
                row.appendChild(cpuCell);
                row.appendChild(memoryCell);
                tableBody.appendChild(row);
            }
        })
        .catch(error => console.error('Error fetching processes:', error));
}

function fetchSystemUsage() {
    fetch('/system_usage')
        .then(response => response.json())
        .then(data => {
            const currentTime = new Date().toLocaleTimeString();

            // Update CPU chart
            cpuChart.data.labels.push(currentTime);
            cpuChart.data.datasets[0].data.push(data.cpu[data.cpu.length - 1]);
            if (cpuChart.data.labels.length > 60) {
                cpuChart.data.labels.shift();
                cpuChart.data.datasets[0].data.shift();
            }
            cpuChart.update();

            // Update Memory chart
            memoryChart.data.labels.push(currentTime);
            memoryChart.data.datasets[0].data.push(data.memory[data.memory.length - 1]);
            if (memoryChart.data.labels.length > 60) {
                memoryChart.data.labels.shift();
                memoryChart.data.datasets[0].data.shift();
            }
            memoryChart.update();
        })
        .catch(error => console.error('Error fetching system usage:', error));
}

// Fetch status, memory, processes, and system usage every 1 second
setInterval(() => {
    fetchStatus();
    fetchMemory();
    fetchProcesses();
    fetchSystemUsage();
}, 1000);

// Initial setup on page load
window.addEventListener('load', () => {
    setupCharts();
    fetchStatus();
    fetchMemory();
    fetchProcesses();
    fetchSystemUsage();
});
