import re

def validate_schedule_file(filepath):
    """
    Valida archivo de calendarización.
    Devuelve (processes, None) si está OK o (None, mensaje_error).
    """
    processes = []
    try:
        p_regex = re.compile(r'^P[1-9][0-9]*$')
        with open(filepath, "r") as f:
            line_num = 0
            for line in f:
                line_num += 1
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) != 4:
                    return None, f"Línea {line_num}: Deben ser 4 elementos por línea."
                pid, bt, at, priority = parts
                if not p_regex.match(pid):
                    return None, f"Línea {line_num}: PID '{pid}' inválido. Debe ser 'P' seguido de entero positivo."
                for val, name in zip([bt, at, priority], ["BT", "AT", "Priority"]):
                    try:
                        v = int(val)
                        if v < 0 or (name != "AT" and v == 0):  # BT/Priority > 0, AT >= 0
                            raise ValueError
                    except Exception:
                        return None, f"Línea {line_num}: {name} '{val}' debe ser entero positivo."
                processes.append({'pid': pid, 'bt': int(bt), 'at': int(at), 'priority': int(priority)})
        if not processes:
            return None, "El archivo está vacío."
    except Exception as e:
        return None, f"Error leyendo archivo: {e}"
    return processes, None


def validate_sync_files(proc_path, actions_path, resources_path):
    """
    Valida los tres archivos de sincronización.
    Devuelve (processes, actions, resources, None) si todo está bien,
    o (None, None, None, mensaje_error) si hay error.
    """
    p_regex = re.compile(r'^P[1-9][0-9]*$')
    r_regex = re.compile(r'^R[1-9][0-9]*$')

    # Procesos
    processes = []
    try:
        with open(proc_path, "r") as f:
            pids = set()
            line_num = 0
            for line in f:
                line_num += 1
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) != 4:
                    return None, None, None, f"Procesos, línea {line_num}: Deben ser 4 elementos."
                pid, bt, at, priority = parts
                if not p_regex.match(pid):
                    return None, None, None, f"Procesos, línea {line_num}: PID '{pid}' inválido."
                try:
                    bt, at, priority = int(bt), int(at), int(priority)
                    if bt <= 0 or at < 0 or priority <= 0:
                        raise ValueError
                except Exception:
                    return None, None, None, f"Procesos, línea {line_num}: BT, AT o Priority no válido."
                pids.add(pid)
                processes.append({'pid': pid, 'bt': bt, 'at': at, 'priority': priority})
        if not processes:
            return None, None, None, "Archivo de procesos vacío."
    except Exception as e:
        return None, None, None, f"Procesos: error al leer archivo: {e}"

    # Recursos
    resources = []
    recursos_set = set()
    try:
        with open(resources_path, "r") as f:
            line_num = 0
            for line in f:
                line_num += 1
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) != 2:
                    return None, None, None, f"Recursos, línea {line_num}: Deben ser 2 elementos."
                rname, count = parts
                if not r_regex.match(rname):
                    return None, None, None, f"Recursos, línea {line_num}: Recurso '{rname}' inválido."
                try:
                    count = int(count)
                    if count < 0:
                        raise ValueError
                except Exception:
                    return None, None, None, f"Recursos, línea {line_num}: COUNT '{count}' debe ser >=0."
                recursos_set.add(rname)
                resources.append({'resource': rname, 'count': count})
        if not resources:
            return None, None, None, "Archivo de recursos vacío."
    except Exception as e:
        return None, None, None, f"Recursos: error al leer archivo: {e}"

    # Acciones
    actions = []
    try:
        with open(actions_path, "r") as f:
            line_num = 0
            for line in f:
                line_num += 1
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) != 4:
                    return None, None, None, f"Acciones, línea {line_num}: Deben ser 4 elementos."
                pid, action, recurso, ciclo = parts
                if not p_regex.match(pid):
                    return None, None, None, f"Acciones, línea {line_num}: PID '{pid}' inválido."
                if pid not in pids:
                    return None, None, None, f"Acciones, línea {line_num}: PID '{pid}' no existe en procesos."
                if action not in ("READ", "WRITE"):
                    return None, None, None, f"Acciones, línea {line_num}: Acción '{action}' inválida."
                if not r_regex.match(recurso):
                    return None, None, None, f"Acciones, línea {line_num}: Recurso '{recurso}' inválido."
                if recurso not in recursos_set:
                    return None, None, None, f"Acciones, línea {line_num}: Recurso '{recurso}' no existe en recursos."
                try:
                    ciclo = int(ciclo)
                    if ciclo < 0:
                        raise ValueError
                except Exception:
                    return None, None, None, f"Acciones, línea {line_num}: Ciclo '{ciclo}' inválido."
                actions.append({'pid': pid, 'action': action, 'resource': recurso, 'cycle': ciclo})
        if not actions:
            return None, None, None, "Archivo de acciones vacío."
    except Exception as e:
        return None, None, None, f"Acciones: error al leer archivo: {e}"

    return processes, actions, resources, None
