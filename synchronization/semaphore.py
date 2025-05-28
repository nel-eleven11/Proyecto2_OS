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

def simulate_semaphore(processes, actions, recurso, contador):
    semaphore = Semaphore(contador)
    events = []
    for action in actions:
        pid, act, rec, cycle = action
        if rec == recurso:
            if semaphore.wait(pid):
                events.append({'pid': pid, 'status': 'ACCESSED', 'cycle': cycle})
                semaphore.signal()
            else:
                events.append({'pid': pid, 'status': 'WAITING', 'cycle': cycle})
    return events
