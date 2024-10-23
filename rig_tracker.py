from flask import Flask, render_template, jsonify
import psutil
import threading
import time

# Prompt the user for the computer name and port number
computer_name = input("Enter the name of the computer: ")
port_number = int(input("Enter the port number to use: "))

app = Flask(__name__)

computer_status = "green"  # Assuming the computer is ON
process_list = []          # Shared global variable for processes
system_memory = {}         # Shared global variable for system memory usage
system_cpu = []            # To store CPU usage over time
system_memory_percent = [] # To store RAM usage over time

N = 20  # Number of processes to display in the table

def update_system_stats():
    global process_list, system_memory, system_cpu, system_memory_percent
    num_cpus = psutil.cpu_count(logical=True)
    while True:
        processes = []
        procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc.cpu_percent(interval=None)
                procs.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        time.sleep(1)
        for proc in procs:
            try:
                cpu_percent = proc.cpu_percent(interval=None) / num_cpus
                memory_percent = proc.memory_percent()
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': cpu_percent,
                    'memory': memory_percent
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        process_list = processes[:N]

        # Update system CPU and memory usage
        cpu_usage = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        mem_usage_percent = mem.percent

        system_cpu.append(cpu_usage)
        system_memory_percent.append(mem_usage_percent)

        # Keep only the latest 60 data points
        MAX_DATA_POINTS = 60
        if len(system_cpu) > MAX_DATA_POINTS:
            system_cpu.pop(0)
            system_memory_percent.pop(0)

        # Update system memory info
        system_memory = {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent
        }

@app.route('/')
def home():
    return render_template(
        'index.html',
        status=computer_status,
        computer_name=computer_name,
        page_title=f"{computer_name} Rig Tracker",
    )

@app.route('/status')
def status_route():
    return jsonify({'status': computer_status, 'computer_name': computer_name})

@app.route('/processes')
def processes_route():
    return jsonify(process_list)


@app.route('/memory')
def memory_route():
    return jsonify(system_memory)

@app.route('/system_usage')
def system_usage_route():
    return jsonify({
        'cpu': system_cpu,
        'memory': system_memory_percent
    })

if __name__ == '__main__':
    threading.Thread(target=update_system_stats, daemon=True).start()
    app.run(host='0.0.0.0', port=port_number)
