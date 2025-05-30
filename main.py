import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import time

from utils.loader import validate_schedule_file, validate_sync_files
import scheduling.fifo as fifo
import scheduling.sjf as sjf
import scheduling.srt as srt
import scheduling.round_robin as rr
import scheduling.priority as priority
import synchronization.mutex as mutex_mod
import synchronization.semaphore as sem_mod

# ----------- COLOR PALETTES
TRON_BLUE = "#00FFF7"   # Neon blue Tron
TRON_ORANGE = "#FF9900" # Neon orange
BG_BLACK = "#181818"    # Deep black

# ----------- FONT ----------- #
def inject_css(mode):
    color = TRON_BLUE if mode == "Calendarización" else TRON_ORANGE
    font_url = "https://fonts.googleapis.com/css?family=Orbitron:wght@700&display=swap"
    st.markdown(f'<link href="{font_url}" rel="stylesheet">', unsafe_allow_html=True)
    css = f"""
    <style>
    html, body, [class*="css"], .stApp, .block-container, .stTextInput, .stNumberInput, .stDataFrame, .stButton, .stRadio, .stSelectbox,
    .stMarkdown, .stSlider, .stHeader, .stSubheader, .stTitle, .stCaption, .stExpander, .stTable, .stTabs, .stCheckbox, .stForm, .stTextArea,
    .stColumn, .stFileUploader, .stMetric, .stAlert, .stSidebar, .stPopover {{
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
        letter-spacing: 2px;
        color: #fff !important;
    }}
    body {{
        background-color: {BG_BLACK} !important;
        color: #fff !important;
    }}
    .stApp, .block-container {{
        background-color: {BG_BLACK};
        color: #fff;
    }}
    .css-1v0mbdj, .css-1dp5vir, .block-container {{
        background-color: {BG_BLACK} !important;
        color: #fff !important;
    }}
    .stButton>button {{
        background-color: {color} !important;
        color: #181818 !important;
        border: 2px solid #fff !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
        font-weight: bold !important;
        font-size: 1.18rem !important;
        box-shadow: 0 0 16px 2px {color};
        letter-spacing: 2px;
    }}
    .stButton>button:hover {{
        background: #fff !important;
        color: {color} !important;
        border: 2px solid {color} !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .stRadio>div>label, .stSelectbox label, .stTextInput label, .stNumberInput label {{
        color: {color} !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .stDataFrame, .css-1ov1ktq {{
        background-color: #222 !important;
        color: #fff !important;
        border-radius: 12px !important;
        border: 1.5px solid {color} !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .stDataFrame table tbody tr {{
        background-color: #222 !important;
        color: #fff !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .stDataFrame table thead tr th {{
        color: {color} !important;
        background: #111 !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .stSelectbox>div>div>div>div>div {{
        background: #111 !important;
        color: #fff !important;
        border: 1.5px solid {color} !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .stNumberInput>div>input {{
        background: #222 !important;
        color: {color} !important;
        border: 1.5px solid {color} !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
    }}
    .css-1v4eu6x, .css-1d391kg, .css-1i3b5e8 {{
        color: {color} !important;
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {color} !important;
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
        text-shadow: 0 0 18px {color}, 0 0 2px #fff;
        letter-spacing: 2.5px;
    }}
    .tron-selected {{
        color: {TRON_BLUE};
        font-family: 'Orbitron', 'Arial', 'Helvetica', sans-serif !important;
        text-shadow: 0 0 16px {TRON_BLUE};
        font-size: 1.08rem;
        letter-spacing: 2px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Simulador de Mecanismos de Sincronización y Algoritmos de Calendarización", layout="wide")
st.markdown("<style>div.block-container{{padding-top:2rem;}}</style>", unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES PARA LEER LOS ARCHIVOS
def get_files_from_dir(path, ext=".txt"):
    try:
        files = [f for f in os.listdir(path) if f.endswith(ext)]
        return files
    except Exception as e:
        return []

def load_process_file(filepath):
    try:
        data = []
        with open(filepath, "r") as f:
            for line in f:
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) == 4:
                    data.append(parts)
        df = pd.DataFrame(data, columns=["PID", "BT", "AT", "Priority"])
        return df
    except Exception:
        return pd.DataFrame(columns=["PID", "BT", "AT", "Priority"])

def load_actions_file(filepath):
    try:
        data = []
        with open(filepath, "r") as f:
            for line in f:
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) == 4:
                    data.append(parts)
        df = pd.DataFrame(data, columns=["PID", "ACTION", "RESOURCE", "CYCLE"])
        return df
    except Exception:
        return pd.DataFrame(columns=["PID", "ACTION", "RESOURCE", "CYCLE"])

def load_resources_file(filepath):
    try:
        data = []
        with open(filepath, "r") as f:
            for line in f:
                parts = [x.strip() for x in line.strip().split(",")]
                if len(parts) == 2:
                    data.append(parts)
        df = pd.DataFrame(data, columns=["RESOURCE", "COUNT"])
        return df
    except Exception:
        return pd.DataFrame(columns=["RESOURCE", "COUNT"])

# --- ESTADOS GLOBALES
if "simulation_type" not in st.session_state:
    st.session_state.simulation_type = "Calendarización"
if "selected_algorithms" not in st.session_state:
    st.session_state.selected_algorithms = []
if "quantum" not in st.session_state:
    st.session_state.quantum = 2
if "selected_process_file" not in st.session_state:
    st.session_state.selected_process_file = ""
if "sync_mode" not in st.session_state:
    st.session_state.sync_mode = "Mutex"
if "sync_process_file" not in st.session_state:
    st.session_state.sync_process_file = ""
if "sync_actions_file" not in st.session_state:
    st.session_state.sync_actions_file = ""
if "sync_resources_file" not in st.session_state:
    st.session_state.sync_resources_file = ""

# --- FUNCIONES DE RESET
def reset_all():
    st.session_state.simulation_type = "Calendarización"
    st.session_state.selected_algorithms = []
    st.session_state.quantum = 2
    st.session_state.selected_process_file = ""
    st.session_state.sync_mode = "Mutex"
    st.session_state.sync_process_file = ""
    st.session_state.sync_actions_file = ""
    st.session_state.sync_resources_file = ""

# --- CABECERA Y SELECCIÓN DE TIPO DE SIMULACIÓN

st.title("Simulador de Mecanismos de Sincronización y  Algoritmos de Calendarización")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    if st.button("Calendarización", type="primary"):
        st.session_state.simulation_type = "Calendarización"
with col2:
    if st.button("Sincronización", type="primary"):
        st.session_state.simulation_type = "Sincronización"
with col3:
    if st.button("Limpiar", type="secondary"):
        reset_all()
        st.rerun()

inject_css(st.session_state.simulation_type)


st.markdown("---")

# --------- VISTA DE CALENDARIZACIÓN ---------
if st.session_state.simulation_type == "Calendarización":
    st.subheader("Simulación de Algoritmos de Calendarización")
    algorithms = ["FIFO", "SJF", "SRT", "Round Robin", "Priority"]

    # Algoritmos: visual cards
    st.markdown("**Selecciona algoritmos:**")
    selected = st.session_state.selected_algorithms if "selected_algorithms" in st.session_state else []
    algo_cols = st.columns(len(algorithms))
    for i, alg in enumerate(algorithms):
        key = f"alg_card_{alg}"
        if alg in selected:
            if algo_cols[i].button(f"{alg} ✔", key=key, help="Click para quitar", args=(alg,)):
                selected.remove(alg)
        else:
            if algo_cols[i].button(alg, key=key, help="Click para seleccionar", args=(alg,)):
                selected.append(alg)
    st.session_state.selected_algorithms = selected

    if "Round Robin" in selected:
        quantum = st.number_input("Quantum para Round Robin:", min_value=1, max_value=20, value=st.session_state.quantum, step=1)
        st.session_state.quantum = quantum

    schedule_files = get_files_from_dir("./processes/schedule")
    st.markdown("**Selecciona archivo de procesos:**")
    process_file = st.selectbox("Archivo", options=[""] + schedule_files, index=0 if not st.session_state.selected_process_file else schedule_files.index(st.session_state.selected_process_file) + 1)
    if process_file:
        st.session_state.selected_process_file = process_file
        df_proc = load_process_file(f"./processes/schedule/{process_file}")
    else:
        df_proc = pd.DataFrame(columns=["PID", "BT", "AT", "Priority"])

    st.markdown("**Procesos cargados:**")
    st.dataframe(df_proc, hide_index=True, use_container_width=True)

    run_simulation = st.button("Empezar simulación", disabled=not(selected and process_file))

    sim_outputs = []
    error = None
    if run_simulation:
        filepath = f"./processes/schedule/{process_file}"
        processes, error = validate_schedule_file(filepath)
        if error:
            st.error(f"Error en archivo de procesos: {error}")
        else:
            algos_map = {
                "FIFO": fifo.fifo,
                "SJF": sjf.sjf,
                "SRT": srt.srt,
                "Round Robin": lambda procs: rr.round_robin(procs, st.session_state.quantum),
                "Priority": priority.priority_scheduling,
            }
            for alg in selected:
                output, avg_wait = algos_map[alg](processes)
                sim_outputs.append((alg, output, avg_wait))

    # Mostrar Gantt y métricas
    if sim_outputs:
        for alg, output, avg_wait in sim_outputs:
            st.markdown(f"### {alg}")
            max_end = max([x['end'] for x in output])
            gantt_placeholder = st.empty()
            for t in range(0, max_end+1):
                fig, ax = plt.subplots(figsize=(12, 1.7))
                colors = plt.cm.get_cmap('tab20')
                seen = {}
                for idx, seg in enumerate(output):
                    if seg['start'] <= t:
                        if seg['pid'] not in seen:
                            seen[seg['pid']] = len(seen)
                        colidx = seen[seg['pid']]
                        draw_end = min(t, seg['end'])
                        if draw_end > seg['start']:
                            ax.barh(0, draw_end-seg['start'], left=seg['start'], color=colors(colidx%20), edgecolor='black', height=0.7)
                            ax.text(seg['start'] + (draw_end-seg['start'])/2, 0, seg['pid'], color="#222", fontsize=12, fontweight='bold', ha='center', va='center')
                ax.set_xlim(0, max_end + 1)
                ax.set_yticks([])
                ax.set_xlabel("Ciclos")
                for xc in range(0, max_end + 1):
                    ax.axvline(x=xc, color="#222", linestyle=':', alpha=0.2)
                ax.set_title(f"Gantt - {alg}")
                gantt_placeholder.pyplot(fig)
                time.sleep(0.4)
            st.markdown(f"**Avg Waiting Time:** `{avg_wait:.2f}` ciclos")
    elif run_simulation and not error:
        st.info("No hay resultados para mostrar.")

    # Mostrar algoritmos seleccionados con fuente y color TRON
    st.markdown('<div class="tron-selected">Algoritmos seleccionados actualmente: ' +
                (", ".join(selected) if selected else "Ninguno") + '</div>', unsafe_allow_html=True)

# --------- VISTA DE SINCRONIZACIÓN ---------
elif st.session_state.simulation_type == "Sincronización":
    st.subheader("Simulación de Mecanismos de Sincronización")
    st.markdown("**Selecciona modo de sincronización:**")
    # Botones estilo toggle para Mutex/Semáforo
    sync_mode = st.session_state.sync_mode
    
    # Crear columnas para el layout
    mode_col1, mode_col2, indicator_col = st.columns([2, 2, 3])
    
    with mode_col1:
        if st.button("Mutex 🔒", key="mutex_btn", help="Simulación con Mutex"):
            st.session_state.sync_mode = "Mutex"
            st.rerun()
    
    with mode_col2:
        if st.button("Semáforo 🚦", key="semaforo_btn", help="Simulación con Semáforo"):
            st.session_state.sync_mode = "Semáforo"
            st.rerun()
    
    with indicator_col:
        # Estilo CSS para el indicador
        st.markdown("""
        <style>
        .sync-indicator {
            border: 2px solid #00FFF7;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            background-color: #181818;
            box-shadow: 0 0 10px #00FFF7;
            margin-top: 10px;
        }
        .sync-indicator h3 {
            color: #00FFF7;
            margin: 0;
            font-family: 'Orbitron', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar el indicador
        st.markdown(f"""
        <div class="sync-indicator">
            <h3>Algoritmo seleccionado: {sync_mode}</h3>
        </div>
        """, unsafe_allow_html=True)

    sync_proc_files = get_files_from_dir("./processes/sync")
    sync_actions_files = get_files_from_dir("./processes/sync")
    sync_resources_files = get_files_from_dir("./processes/sync")

    st.markdown("**Selecciona archivos a cargar:**")
    colp, cola, colr = st.columns(3)
    with colp:
        sync_proc_file = st.selectbox("Procesos", options=[""] + sync_proc_files, index=0 if not st.session_state.sync_process_file else sync_proc_files.index(st.session_state.sync_process_file) + 1)
    with cola:
        sync_actions_file = st.selectbox("Acciones", options=[""] + sync_actions_files, index=0 if not st.session_state.sync_actions_file else sync_actions_files.index(st.session_state.sync_actions_file) + 1)
    with colr:
        sync_resources_file = st.selectbox("Recursos", options=[""] + sync_resources_files, index=0 if not st.session_state.sync_resources_file else sync_resources_files.index(st.session_state.sync_resources_file) + 1)

    st.session_state.sync_process_file = sync_proc_file
    st.session_state.sync_actions_file = sync_actions_file
    st.session_state.sync_resources_file = sync_resources_file

    st.markdown("**Procesos:**")
    df_sync_proc = load_process_file(f"./processes/sync/{sync_proc_file}") if sync_proc_file else pd.DataFrame(columns=["PID", "BT", "AT", "Priority"])
    st.dataframe(df_sync_proc, hide_index=True, use_container_width=True)
    st.markdown("**Acciones:**")
    df_sync_act = load_actions_file(f"./processes/sync/{sync_actions_file}") if sync_actions_file else pd.DataFrame(columns=["PID", "ACTION", "RESOURCE", "CYCLE"])
    st.dataframe(df_sync_act, hide_index=True, use_container_width=True)
    st.markdown("**Recursos:**")
    df_sync_res = load_resources_file(f"./processes/sync/{sync_resources_file}") if sync_resources_file else pd.DataFrame(columns=["RESOURCE", "COUNT"])
    st.dataframe(df_sync_res, hide_index=True, use_container_width=True)

    run_sync_sim = st.button("Empezar simulación", disabled=not(sync_proc_file and sync_actions_file and sync_resources_file))
    sync_result = None
    sync_error = None
    if run_sync_sim:
        proc_path = f"./processes/sync/{sync_proc_file}"
        actions_path = f"./processes/sync/{sync_actions_file}"
        resources_path = f"./processes/sync/{sync_resources_file}"
        procs, acts, res, sync_error = validate_sync_files(proc_path, actions_path, resources_path)
        if sync_error:
            st.error(f"Error en archivos: {sync_error}")
        else:
            actions_fmt = []
            for a in acts:
                actions_fmt.append([a['pid'], a['action'], a['resource'], int(a['cycle'])])
            if sync_mode == "Mutex":
                events = mutex_mod.simulate_mutex(procs, actions_fmt, res)
            else:
                events = sem_mod.simulate_semaphore(procs, actions_fmt, res)
            if events:
                st.markdown("### Diagrama animado de acceso a recursos (Herencia de Prioridad)")
                process_list = sorted({e['pid'] for e in events}, key=lambda pid: -next(p['priority'] for p in procs if p['pid'] == pid))
                process_idx = {pid: i for i, pid in enumerate(process_list)}
                max_cycle = max(e['cycle'] for e in events)
                gantt_placeholder = st.empty()
                
                for t in range(0, max_cycle + 1):
                    fig, ax = plt.subplots(figsize=(14, max(1.7, len(process_list)*0.7)))
                    for ev in events:
                        if ev['cycle'] <= t:
                            y = process_idx[ev['pid']]
                            # Definir colores de fondo según estado
                            if ev['status'] == "ACCESSED":
                                color = "#30ff87"  # Verde para acceso
                            elif ev['status'] == "RELEASED":
                                color = "#ff3030"  # Rojo para liberación
                            else:
                                color = TRON_ORANGE  # Naranja para espera
                            
                            # Dibujar la barra
                            ax.barh(y, 1, left=ev['cycle'], color=color, edgecolor='#111', height=0.65)
                            
                            # Texto siempre en negro con fondo blanco para mejor legibilidad
                            ax.text(ev['cycle']+0.5, y, 
                                f"{ev['resource']} {ev['action']} ({ev['status']})", 
                                color='black',  # Texto siempre negro
                                fontsize=6, 
                                ha='center', 
                                va='center', 
                                weight='bold',
                                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
                    
                    ax.set_yticks(range(len(process_list)))
                    ax.set_yticklabels(process_list)
                    ax.set_xlabel("Ciclos")
                    ax.set_xlim(0, max_cycle+2)
                    
                    # Líneas verticales de guía
                    for xc in range(0, max_cycle+2):
                        ax.axvline(x=xc, color="#222", linestyle=':', alpha=0.13)
                    
                    ax.set_title("Procesos ordenados por prioridad (mayor arriba)")
                    gantt_placeholder.pyplot(fig)
                    time.sleep(0.4)
    elif run_sync_sim and not sync_error:
        st.info("No hay resultados para mostrar.")
