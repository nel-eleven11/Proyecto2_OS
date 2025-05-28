import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Simulador de Planificación y Sincronización", layout="wide")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES PARA LEER LOS ARCHIVOS

def get_files_from_dir(path, ext=".txt"):
    """Devuelve una lista de archivos de un directorio con la extensión deseada."""
    try:
        files = [f for f in os.listdir(path) if f.endswith(ext)]
        return files
    except Exception as e:
        return []

def load_process_file(filepath):
    """Carga archivo de procesos y devuelve DataFrame."""
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
st.title("Simulador de Planificación y Sincronización de Procesos")
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
        st.experimental_rerun()

st.markdown("---")

# --- VISTA DE CALENDARIZACIÓN
if st.session_state.simulation_type == "Calendarización":
    st.subheader("Simulación de Algoritmos de Calendarización")
    # Selección de algoritmos
    algorithms = ["FIFO", "SJF", "SRT", "Round Robin", "Priority"]
    st.markdown("**Selecciona algoritmos:**")
    selected = st.multiselect("Algoritmos", algorithms, default=st.session_state.selected_algorithms, key="algos_select")
    st.session_state.selected_algorithms = selected

    # Quantum
    if "Round Robin" in selected:
        quantum = st.number_input("Quantum para Round Robin:", min_value=1, max_value=20, value=st.session_state.quantum, step=1)
        st.session_state.quantum = quantum

    # Archivos de procesos
    schedule_files = get_files_from_dir("./processes/schedule")
    st.markdown("**Selecciona archivo de procesos:**")
    process_file = st.selectbox("Archivo", options=[""] + schedule_files, index=0 if not st.session_state.selected_process_file else schedule_files.index(st.session_state.selected_process_file) + 1)
    if process_file:
        st.session_state.selected_process_file = process_file
        df_proc = load_process_file(f"./processes/schedule/{process_file}")
    else:
        df_proc = pd.DataFrame(columns=["PID", "BT", "AT", "Priority"])

    # Tabla de procesos
    st.markdown("**Procesos cargados:**")
    st.dataframe(df_proc, hide_index=True, use_container_width=True)

    # Botón de empezar simulación
    st.button("Empezar simulación", disabled=True)

    # Diagrama de Gantt (placeholder en blanco)
    st.markdown("**Visualización de ejecución (Gantt):**")
    fig, ax = plt.subplots(figsize=(10, 1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.set_title("Gantt: ejecución pendiente")
    st.pyplot(fig)

    # Métricas (placeholder)
    st.markdown("**Métricas:**")
    st.info("Aquí aparecerán las métricas de eficiencia cuando la simulación esté implementada.")

    # Algoritmos seleccionados actualmente
    st.markdown(f"**Algoritmos seleccionados actualmente:** {', '.join(selected) if selected else 'Ninguno'}")


# --- VISTA DE SINCRONIZACIÓN
elif st.session_state.simulation_type == "Sincronización":
    st.subheader("Simulación de Mecanismos de Sincronización")
    # Selección de modo
    st.markdown("**Selecciona modo de sincronización:**")
    sync_modes = ["Mutex", "Semáforo"]
    sync_mode = st.radio("Modo", options=sync_modes, index=sync_modes.index(st.session_state.sync_mode), horizontal=True, key="sync_mode_radio")
    st.session_state.sync_mode = sync_mode

    # Archivos de procesos, recursos y acciones
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

    # Mostrar tablas de cada archivo
    st.markdown("**Procesos:**")
    df_sync_proc = load_process_file(f"./processes/sync/{sync_proc_file}") if sync_proc_file else pd.DataFrame(columns=["PID", "BT", "AT", "Priority"])
    st.dataframe(df_sync_proc, hide_index=True, use_container_width=True)

    st.markdown("**Acciones:**")
    df_sync_act = load_actions_file(f"./processes/sync/{sync_actions_file}") if sync_actions_file else pd.DataFrame(columns=["PID", "ACTION", "RESOURCE", "CYCLE"])
    st.dataframe(df_sync_act, hide_index=True, use_container_width=True)

    st.markdown("**Recursos:**")
    df_sync_res = load_resources_file(f"./processes/sync/{sync_resources_file}") if sync_resources_file else pd.DataFrame(columns=["RESOURCE", "COUNT"])
    st.dataframe(df_sync_res, hide_index=True, use_container_width=True)

    # Botón de empezar simulación
    st.button("Empezar simulación", disabled=True)

    # Diagrama de timeline (placeholder en blanco)
    st.markdown("**Visualización dinámica de acceso a recursos:**")
    fig, ax = plt.subplots(figsize=(10, 1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.set_title("Acceso a recursos: ejecución pendiente")
    st.pyplot(fig)

    st.info("Aquí aparecerán los eventos y el estado de los recursos cuando la simulación esté implementada.")

