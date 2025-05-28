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

# Simulación de procesos accediendo a un recurso con Mutex
def simulate_mutex(processes, actions, recurso):
    mutex = Mutex()
    events = []
    for action in actions:
        pid, act, rec, cycle = action
        if rec == recurso:
            if act == 'WRITE' or act == 'READ':
                if mutex.acquire():
                    events.append({'pid': pid, 'status': 'ACCESSED', 'cycle': cycle})
                    mutex.release()
                else:
                    events.append({'pid': pid, 'status': 'WAITING', 'cycle': cycle})
    return events
