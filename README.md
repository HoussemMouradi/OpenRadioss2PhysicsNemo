# OpenRadioss2PhysicsNeMo

This repository provides a full pipeline for generating crash simulation datasets using [OpenRadioss](https://github.com/OpenRadioss/OpenRadioss) and formatting them to train AI models within the [PhysicsNeMo framework](https://github.com/NVIDIA/physicsnemo/tree/main/examples/structural_mechanics/crash).

Using the [OpenRadioss Bumper Beam example](http://openradioss.atlassian.net/wiki/spaces/OPENRADIOSS/pages/11075585/Bumper+Beam) as a baseline, the pipeline generates a dataset by iteratively modifying the shell thickness and rigid pole impact position across successive simulation runs. The OpenRadioss ANIM output files are then converted to d3plot format using [Vortex-Radioss](https://github.com/Vortex-CAE/Vortex-Radioss), enabling compatibility with the d3plot reader in the PhysicsNeMo crash example.

<p align="center">
<img src="https://github.com/user-attachments/assets/1f0b2f79-35be-4fba-9907-7601a698716e" width="700">

> **Just want the dataset?** The pre-generated training dataset is available on Hugging Face:
> [AIRBORNEPANDA/BumperBeamCrashExample](https://huggingface.co/datasets/AIRBORNEPANDA/BumperBeamCrashExample)

---

## Repository Structure

```
OpenRadioss2PhysicsNeMo/
├── OpenRadioss2PhysicsNeMo_Notebooks/
│   ├── OpenRadioss2PhysicsNEMO_windows.ipynb   # Notebook for Windows
│   └── OpenRadioss_PhysicsNEMO_linux.ipynb     # Notebook for Linux / Google Colab
├── vortex_radioss/
│   └── animtod3plot/                            # Vortex-Radioss ANIM→d3plot converter
├── Bumper_Beam_AP_meshed_0000.rad               # Radioss starter file (input deck)
├── Bumper_Beam_AP_meshed_0001.rad               # Radioss engine file (solver settings)
├── radioss_generate_d3plot_dataset.py           # Main simulation script (standalone)
├── generate_global_features_json.py             # Global features JSON extractor (standalone)
├── runradioss.bat                               # Windows run script for OpenRadioss
└── requirements.txt                             # Python dependencies
```

---

## Prerequisites

### 1. OpenRadioss

Download the pre-built binaries for your platform from the official releases page:

- **Windows:** [OpenRadioss releases](https://github.com/OpenRadioss/OpenRadioss/releases) → download `OpenRadioss_win64.zip`

Extract the archive so that the `OpenRadioss/` folder sits alongside this repository (or adjust the path in the scripts).

### 2. Python

Python 3.8 or later is required.

### 3. Python Dependencies

Install all required packages with:

```bash
pip install -r requirements.txt
```

The main dependencies are:

| Package | Purpose |
|---|---|
| `lasso-python` | d3plot read/write interface used by Vortex-Radioss |
| `tqdm` | Progress bars during batch conversion |
| `psutil` | CPU thread detection |

---

## Installation

Clone this repository:

```bash
git clone https://github.com/HoussemMouradi/OpenRadioss2PhysicsNeMo.git
cd OpenRadioss2PhysicsNeMo
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage — Standalone Scripts

Use this approach if you want to run the pipeline directly from the command line without Jupyter notebooks, on any platform.

### Step 1 — Configure and Run Simulations

Open `radioss_generate_d3plot_dataset.py` and adjust the parameters at the bottom of the file under the `if __name__ == "__main__":` block:

```python
nt = 16                          # Number of CPU threads for the solver
openradioss_path = "C:/path/to/OpenRadioss"   # Path to your OpenRadioss installation
thickness_range = (1.2, 2.0)     # Shell thickness range (mm)
prop_ids_to_change = [2, 7]      # PROP/SHELL IDs to modify
pole_y_range = (-500, 500)       # Rigid pole Y-axis offset range (mm)
number_of_sims = 99              # Number of simulation runs to generate
```

Then run:

```bash
python radioss_generate_d3plot_dataset.py
```

This will create a `RAW_DATA/` directory in the current folder with the following structure:

```
RAW_DATA/
├── Run100/
│   ├── Bumper_Beam_AP_meshed.d3plot
│   ├── Bumper_Beam_AP_meshed_0000.rad   # Modified starter file
│   └── Bumper_Beam_AP_meshed_0001.rad   # Engine file
├── Run101/
│   └── ...
└── ...
```

> **Note (Windows):** The script calls `runradioss.bat` to launch the solver. Make sure it is present in the working directory.
>
> **Note (Linux):** Replace the `run_radioss` function call to use `runradioss.sh` instead of `runradioss.bat`, or run the solver commands directly.

### Step 2 — Generate the Global Features JSON

Once all simulations are complete, extract the simulation parameters (shell thickness, pole position, initial velocity) from each starter file into a single JSON file used by PhysicsNeMo as global features:

```bash
python generate_global_features_json.py
```

This produces `GLOBAL_FEATURES.json` in the current directory:

```json
{
    "Run100": {
        "velocity_x": -8000.0,
        "rwall_origin_y": 123.45,
        "thickness_scale": 1.73
    },
    "Run101": { ... },
    ...
}
```

---

## Usage — Jupyter Notebooks

The notebooks automate the same pipeline in a step-by-step interactive format and handle all dependency installation automatically. Two versions are provided depending on your platform.

### Windows Notebook

**File:** `OpenRadioss2PhysicsNeMo_Notebooks/OpenRadioss2PhysicsNEMO_windows.ipynb`

Designed to run locally on a Windows machine with Jupyter installed.

**Steps covered in the notebook:**
1. Download and extract OpenRadioss Windows binaries
2. Install Vortex-Radioss dependencies (`lasso-python`, `tqdm`)
3. Create the `runradioss.bat` run script
4. Download the Bumper Beam input files from Hugging Face
5. Detect CPU threads, define helper functions, and run simulations
6. Generate `GLOBAL_FEATURES.json`

### Linux / Google Colab Notebook

**File:** `OpenRadioss2PhysicsNeMo_Notebooks/OpenRadioss_PhysicsNEMO_linux.ipynb`

Designed for Linux environments and Google Colab. All outputs are saved to local storage (`/content/RAW_DATA/` on Colab).

> 🔗 **Open in Google Colab:** *(link coming soon)*

**Steps covered in the notebook:**
1. Download and extract OpenRadioss Linux binaries
2. Install Vortex-Radioss dependencies (`lasso-python`, `tqdm`)
3. Create the `runradioss.sh` run script
4. Download the Bumper Beam input files from Hugging Face
5. Detect CPU threads, define helper functions, and run simulations
6. *(Colab only)* Compress `RAW_DATA/` into a zip archive and download it
7. Generate `GLOBAL_FEATURES.json`

---

## How It Works

Each simulation run samples random values for two parameters within the configured ranges:

- **Shell thickness** — applied uniformly to all `PROP/SHELL` IDs listed in `prop_ids_to_change`
- **Pole Y-axis offset** — shifts the rigid pole impact position along the beam

For each run, the pipeline:
1. Writes a modified copy of the master starter file (`_0000.rad`) with the new parameters
2. Copies the engine file (`_0001.rad`) unchanged
3. Runs the OpenRadioss Starter (pre-processor) then Engine (solver)
4. Converts the ANIM output to d3plot format using Vortex-Radioss

---

## Related Links

| Resource | Link |
|---|---|
| PhysicsNeMo crash example | [github.com/NVIDIA/physicsnemo](https://github.com/NVIDIA/physicsnemo/tree/main/examples/structural_mechanics/crash) |
| OpenRadioss | [github.com/OpenRadioss/OpenRadioss](https://github.com/OpenRadioss/OpenRadioss) |
| OpenRadioss Bumper Beam example | [openradioss.atlassian.net](http://openradioss.atlassian.net/wiki/spaces/OPENRADIOSS/pages/11075585/Bumper+Beam) |
| Vortex-Radioss | [github.com/Vortex-CAE/Vortex-Radioss](https://github.com/Vortex-CAE/Vortex-Radioss) |
| Pre-generated dataset (Hugging Face) | [AIRBORNEPANDA/BumperBeamCrashExample](https://huggingface.co/datasets/AIRBORNEPANDA/BumperBeamCrashExample) |
| Bumper Beam input files (Hugging Face) | [AIRBORNEPANDA/Bumper_Beam_Radioss_Input](https://huggingface.co/datasets/AIRBORNEPANDA/Bumper_Beam_Radioss_Input) |

