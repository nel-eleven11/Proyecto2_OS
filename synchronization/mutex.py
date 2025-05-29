class Mutex:
    def __init__(self):
        self.locked = False

    def acquire(self):
        if not self.locked:
            self.locked = True
            return True
        return False

    def release(self):
        self.locked = False

def simulate_mutex(processes, actions, recursos):
    # recursos: lista de {'resource': nombre, 'count': int}  (el count es ignorado para mutex)
    resource_mutexes = {r['resource']: Mutex() for r in recursos}
    timeline = []  # [ {'pid', 'resource', 'cycle', 'status'} ... ]
    actions_sorted = sorted(actions, key=lambda x: int(x[3]))  # sort by cycle

    for a in actions_sorted:
        pid, act, rec, cycle = a
        mutex = resource_mutexes[rec]
        # Simula solo para ese ciclo
        if mutex.acquire():
            timeline.append({'pid': pid, 'resource': rec, 'cycle': int(cycle), 'status': 'ACCESSED'})
            mutex.release()
        else:
            timeline.append({'pid': pid, 'resource': rec, 'cycle': int(cycle), 'status': 'WAITING'})
    return timeline
