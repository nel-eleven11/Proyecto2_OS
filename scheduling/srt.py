def srt(processes):
    import heapq
    n = len(processes)
    processes = sorted(processes, key=lambda x: x['at'])
    ready = []
    gantt = []
    time = 0
    idx = 0
    finished = 0
    remaining = {p['pid']: p['bt'] for p in processes}
    last_proc = None
    start_time = {}
    waiting_times = {p['pid']: 0 for p in processes}
    last_time = 0

    while finished < n:
        while idx < n and processes[idx]['at'] <= time:
            heapq.heappush(ready, (remaining[processes[idx]['pid']], processes[idx]['at'], processes[idx]['pid'], processes[idx]['priority']))
            idx += 1
        if ready:
            rem_bt, at, pid, prio = heapq.heappop(ready)
            if last_proc != pid:
                if last_proc is not None:
                    gantt[-1]['end'] = time
                gantt.append({'pid': pid, 'start': time, 'end': None})
                if pid not in start_time:
                    start_time[pid] = time
            last_proc = pid
            remaining[pid] -= 1
            time += 1
            if remaining[pid] > 0:
                heapq.heappush(ready, (remaining[pid], at, pid, prio))
            else:
                finished += 1
                waiting_times[pid] = time - at - [p for p in processes if p['pid'] == pid][0]['bt']
        else:
            time += 1
    if gantt and gantt[-1]['end'] is None:
        gantt[-1]['end'] = time
    avg_wait = sum(waiting_times.values()) / n
    return gantt, avg_wait
