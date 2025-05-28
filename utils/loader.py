def load_processes(filename):
    processes = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) != 4:
                    continue  # skip malformed line
                pid = parts[0].strip()
                try:
                    bt = int(parts[1].strip())
                    at = int(parts[2].strip())
                    prio = int(parts[3].strip())
                except ValueError:
                    continue  # skip line if conversion fails
                processes.append({'pid': pid, 'bt': bt, 'at': at, 'priority': prio})
        if not processes:
            raise Exception("No processes loaded. Check file format.")
    except Exception as e:
        return None, str(e)
    return processes, None
