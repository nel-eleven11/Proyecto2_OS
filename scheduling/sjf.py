def sjf(processes):
    processes = sorted(processes, key=lambda x: (x['at'], x['bt']))
    time = 0
    gantt = []
    waiting_times = []
    ready = []
    idx = 0
    n = len(processes)
    completed = 0
    in_queue = set()
    while completed < n:
        # Agrega procesos listos
        while idx < n and processes[idx]['at'] <= time:
            ready.append(processes[idx])
            in_queue.add(processes[idx]['pid'])
            idx += 1
        if ready:
            # Selecciona el de menor burst time
            ready.sort(key=lambda x: x['bt'])
            proc = ready.pop(0)
            start = max(time, proc['at'])
            wait = start - proc['at']
            waiting_times.append(wait)
            gantt.append({'pid': proc['pid'], 'start': start, 'end': start + proc['bt']})
            time = start + proc['bt']
            completed += 1
        else:
            time += 1
    avg_wait = sum(waiting_times) / n
    return gantt, avg_wait
