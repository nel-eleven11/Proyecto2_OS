class Semaphore:
    def __init__(self, value):
        self.value = value
        self.queue = []

    def wait(self, pid):
        if self.value > 0:
            self.value -= 1
            return True
        else:
            self.queue.append(pid)
            return False

    def signal(self):
        if self.queue:
            self.queue.pop(0)
        else:
            self.value += 1

def simulate_semaphore(processes, actions, recursos):
    resource_semaphores = {r['resource']: Semaphore(r['count']) for r in recursos}
    timeline = []
    actions_sorted = sorted(actions, key=lambda x: int(x[3]))
    for a in actions_sorted:
        pid, act, rec, cycle = a
        sem = resource_semaphores[rec]
        if sem.wait(pid):
            timeline.append({'pid': pid, 'resource': rec, 'cycle': int(cycle), 'status': 'ACCESSED'})
            sem.signal()
        else:
            timeline.append({'pid': pid, 'resource': rec, 'cycle': int(cycle), 'status': 'WAITING'})
    return timeline
