def round_robin(processes, quantum):
    from collections import deque
    n = len(processes)
    processes = sorted(processes, key=lambda x: x['at'])
    ready = deque()
    gantt = []
    time = 0
    idx = 0
    waiting_times = {p['pid']: 0 for p in processes}
    remaining = {p['pid']: p['bt'] for p in processes}
    last_proc = None

    queue_arrival = []
    complete = 0
    visited = set()

    while complete < n:
        # Añadir procesos que han llegado
        while idx < n and processes[idx]['at'] <= time:
            ready.append(processes[idx])
            visited.add(processes[idx]['pid'])
            idx += 1
        if not ready:
            time += 1
            continue
        proc = ready.popleft()
        pid = proc['pid']
        bt = remaining[pid]
        exec_time = min(quantum, bt)
        if last_proc != pid:
            gantt.append({'pid': pid, 'start': time, 'end': time + exec_time})
        else:
            gantt[-1]['end'] += exec_time
        last_proc = pid
        waiting_times[pid] += time - max(proc['at'], waiting_times.get(pid + "_last", proc['at']))
        waiting_times[pid + "_last"] = time + exec_time
        time += exec_time
        remaining[pid] -= exec_time
        # Agregar nuevos procesos que han llegado durante ejecución
        while idx < n and processes[idx]['at'] <= time:
            ready.append(processes[idx])
            visited.add(processes[idx]['pid'])
            idx += 1
        if remaining[pid] > 0:
            ready.append(proc)
        else:
            complete += 1
    # Calcular tiempo de espera promedio
    waiting = []
    for p in processes:
        turnaround = gantt[[g['pid'] for g in gantt].index(p['pid'])]['end'] - p['at']
        waiting.append(turnaround - p['bt'])
    avg_wait = abs(sum(waiting) / n)
    return gantt, avg_wait
