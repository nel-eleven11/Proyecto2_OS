class Semaphore:
    def __init__(self, value):
        self.max_value = value
        self.value = value
        self.queue = []
        self.owners = []
        self.original_priorities = {}

    def wait(self, process):
        if self.value > 0:
            self.value -= 1
            self.owners.append(process['pid'])
            return True
        else:
            # Aplicar herencia de prioridad si es necesario
            for owner in self.owners:
                if process['priority'] > process_map[owner]['priority']:
                    self.original_priorities[owner] = process_map[owner]['priority']
                    process_map[owner]['priority'] = process['priority']
            self.queue.append(process['pid'])
            return False

    def signal(self, process):
        if process['pid'] in self.owners:
            self.owners.remove(process['pid'])
            # Restaurar prioridad si fue modificada
            if process['pid'] in self.original_priorities:
                process_map[process['pid']]['priority'] = self.original_priorities[process['pid']]
                del self.original_priorities[process['pid']]
            
            # Asignar el recurso a procesos en espera (por prioridad)
            if self.queue:
                next_pid = max(self.queue, key=lambda pid: process_map[pid]['priority'])
                self.queue.remove(next_pid)
                self.owners.append(next_pid)
                return next_pid
            else:
                self.value += 1
                if self.value > self.max_value:
                    self.value = self.max_value
        return None

def simulate_semaphore(processes, actions, resources):
    events = []
    global process_map
    process_map = {p['pid']: p.copy() for p in processes}
    
    # Crear semáforos con el count especificado en resources
    semaphores = {}
    for r in resources:
        semaphores[r['resource']] = Semaphore(value=int(r['count']))
    
    process_resources = {p['pid']: [] for p in processes}
    actions = sorted(actions, key=lambda x: (x[3], -process_map[x[0]]['priority']))

    for act in actions:
        pid, action, resource, cycle = act
        proc = process_map[pid]
        sem = semaphores[resource]

        # Verificar si el proceso ya tiene el recurso
        if resource in process_resources[pid]:
            # Liberar el recurso
            released_to = sem.signal(proc)
            process_resources[pid].remove(resource)
            events.append({
                'pid': pid,
                'priority': proc['priority'],
                'cycle': cycle,
                'resource': resource,
                'action': action,
                'status': 'RELEASED'
            })
            
            # Si el release le asignó el recurso a otro proceso
            if released_to:
                process_resources[released_to].append(resource)
                events.append({
                    'pid': released_to,
                    'priority': process_map[released_to]['priority'],
                    'cycle': cycle,
                    'resource': resource,
                    'action': 'AUTO-ASSIGNED',
                    'status': 'ACCESSED'
                })
        else:
            # Intentar adquirir el recurso
            if sem.wait(proc):
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