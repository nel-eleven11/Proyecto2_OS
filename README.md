# Proyecto2_OS
Proyecto 2 de Sistemas Operativos - Simulador

---

# Simulador de Planificación y Sincronización de Procesos

**Autor:**  
Nelson García Bravatti

## Descripción

Este proyecto simula visualmente algoritmos de planificación de procesos y mecanismos de sincronización (Mutex y Semáforo), mostrando animaciones tipo diagrama de Gantt para procesos y recursos.  
Incluye una interfaz visual moderna inspirada en TRON, desarrollada en Python usando [Streamlit](https://streamlit.io/).

---

## Requisitos

- Python 3.8 o superior
- Instalar dependencias:

```bash
pip install -r requirements.txt
```
Dependencias principales:

- streamlit
- pandas
- matplotlib

## Ejecución

Clona el repositorio:

```bash
git clone <https://github.com/nel-eleven11/Proyecto2_OS>
cd <Proyecto2_OS>
```

Ejecuta la aplicación:

```bash
streamlit run main.py
```

## Estructura

```bash
.
├── processes/
│   ├── schedule/    # Archivos de procesos para calendarización
│   └── sync/        # Archivos para sincronización
├── scheduling/      # Algoritmos de calendarización
├── synchronization/ # Algoritmos de sincronización
├── utils/
├── main.py
├── README.md
└── requirements.txt
```

## Formatos de Archivos de Entrada

### A. Calendarización

Solo se requiere un archivo de procesos ubicado en /processes/schedule/.

Formato (una línea por proceso):

```bash
<PID>, <BT>, <AT>, <Priority>
```

- PID: Letra P seguida de un número (ej: P1)
- BT: Burst time (entero positivo)
- AT: Arrival time (entero positivo)
- Priority: Prioridad (entero positivo)

Ejemplo:

```bash
P1, 8, 0, 1
P2, 4, 2, 2
P3, 9, 3, 3
```

### B. Sincronización

Ubica los archivos en /processes/sync/:

1. Procesos (*.txt)

```bash
<PID>, <BT>, <AT>, <Priority>
```

Ejemplo:

```bash
P1, 8, 0, 1
P2, 4, 2, 2
P3, 9, 3, 3
```

2. Recursos (*.txt)

```bash
<NOMBRE RECURSO>, <CONTADOR>
```

- NOMBRE RECURSO: Letra R seguida de un número (ej: R1)
- CONTADOR: entero positivo o cero (cantidad de instancias)

Ejemplo:

```bash
R1, 1
R2, 2
```

3. Acciones (*.txt)

```bash
<PID>, <ACCION>, <RECURSO>, <CICLO>
```

- PID: igual que en Procesos (ej: P1)
- ACCION: READ o WRITE
- RECURSO: igual que en Recursos (ej: R1)
- CICLO: entero positivo o cero

Ejemplo:

```bash
P1, READ, R1, 0
P2, WRITE, R2, 1
```

## Uso de la Interfaz

- Selecciona Calendarización o Sincronización (arriba de la pantalla).

- Carga los archivos requeridos usando los menús desplegables.

- Elige los algoritmos de calendarización o el modo de sincronización.

- Haz clic en "Empezar simulación" para ver el diagrama animado.

- El botón Limpiar reinicia todas las selecciones.