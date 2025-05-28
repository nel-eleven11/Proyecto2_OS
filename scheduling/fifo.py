def fifo(processes):
    processes = sorted(processes, key=lambda x: x['at'])
    time = 0
    gantt = []
    waiting_times = []
    for proc in processes:
        start = max(time, proc['at'])
        wait = start - proc['at']
        waiting_times.append(wait)
        gantt.append({'pid': proc['pid'], 'start': start, 'end': start + proc['bt']})
        time = start + proc['bt']
    avg_wait = sum(waiting_times) / len(waiting_times)
    return gantt, avg_wait
