from flask import Flask, render_template, jsonify
import psutil
import threading
import time

app = Flask(__name__)

vulcanus_status = "green"  
process_list = []          
system_memory = {}         
system_cpu = []            
system_memory_percent = [] 

N = 20  

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
    return render_template('index.html', status=vulcanus_status)

@app.route('/processes')
def processes_route():
    return jsonify(process_list)

@app.route('/status')
def status_route():
    return jsonify({'status': vulcanus_status})

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
    app.run(host='0.0.0.0', port=6062)
