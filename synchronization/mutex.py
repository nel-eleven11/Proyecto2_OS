class Mutex:
    def __init__(self, count=1):
        self.max_count = count
        self.current_count = count
        self.owners = []
        self.waiting_queue = []
        self.original_priorities = {}

    def acquire(self, process):
        if self.current_count > 0:
            self.current_count -= 1
            self.owners.append(process['pid'])
            return True
        else:
            # Aplicar herencia de prioridad si es necesario
            for owner in self.owners:
                if process['priority'] > process_map[owner]['priority']:
                    self.original_priorities[owner] = process_map[owner]['priority']
                    process_map[owner]['priority'] = process['priority']
            self.waiting_queue.append(process['pid'])
            return False

    def release(self, process):
        if process['pid'] in self.owners:
            self.owners.remove(process['pid'])
            # Restaurar prioridad si fue modificada
            if process['pid'] in self.original_priorities:
                process_map[process['pid']]['priority'] = self.original_priorities[process['pid']]
                del self.original_priorities[process['pid']]
            
            self.current_count += 1
            # Asignar el recurso a procesos en espera (por prioridad)
            if self.waiting_queue:
                next_pid = max(self.waiting_queue, key=lambda pid: process_map[pid]['priority'])
                self.waiting_queue.remove(next_pid)
                self.owners.append(next_pid)
                self.current_count -= 1
                return next_pid
        return None

def simulate_mutex(processes, actions, resources):
    events = []
    global process_map
    process_map = {p['pid']: p.copy() for p in processes}
    
    # Crear mutexes con el count especificado en resources
    mutexes = {}
    for r in resources:
        mutexes[r['resource']] = Mutex(count=int(r['count']))
    
    process_resources = {p['pid']: [] for p in processes}
    actions = sorted(actions, key=lambda x: (x[3], -process_map[x[0]]['priority']))

    for act in actions:
        pid, action, resource, cycle = act
        proc = process_map[pid]
        mtx = mutexes[resource]

        # Verificar si el proceso ya tiene el recurso
        if resource in process_resources[pid]:
            # Liberar el recurso
            mtx.release(proc)
            process_resources[pid].remove(resource)
            events.append({
                'pid': pid,
                'priority': proc['priority'],
                'cycle': cycle,
                'resource': resource,
                'action': action,
                'status': 'RELEASED'
            })
        else:
            # Intentar adquirir el recurso
            if mtx.acquire(proc):
                process_resources[pid].append(resource)
                events.append({
                    'pid': pid,
                    'priority': proc['priority'],
                    'cycle': cycle,
                    'resource': resource,
                    'action': action,
                    'status': 'ACCESSED'
                })
            else:
                events.append({
                    'pid': pid,
                    'priority': proc['priority'],
                    'cycle': cycle,
                    'resource': resource,
                    'action': action,
                    'status': 'WAITING'
                })

    return events