# PyQt UI Project

This project is a PyQt-based user interface application.

## Prerequisites

Before running this project, ensure you have the following installed:

*   **Python 3**: The application is written in Python 3.
*   **PyQt**: The graphical user interface framework.
*   **Wayland (Linux)**: The `start.sh` script explicitly sets `QT_QPA_PLATFORM=wayland`, indicating it's configured to run on a Wayland display server. If you are not using Wayland, you might need to adjust the `start.sh` script or your environment variables.

## Setup Instructions

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository_url>
    cd pyqtui
    ```
    (Replace `<repository_url>` with the actual URL of your repository.)

2.  **Install Python dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # If you have a requirements.txt file, install dependencies:
    # pip install -r requirements.txt
    # Otherwise, you might need to install PyQt manually:
    pip install PyQt5 # Or PyQt6, depending on the project's specific PyQt version
    ```

## Running the Application

To start the application, execute the `start.sh` script:

```bash
./start.sh
```

This script sets the `QT_QPA_PLATFORM` environment variable to `wayland` and then runs the `main.py` script using `python3`.
