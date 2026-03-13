# OmniPeek

OmniPeek is a lightweight, scalable live-preview tool for Windows. It allows you to monitor the contents of a secondary display via a real-time, scaleable floating window on your primary display.

## Features
- **Live Screen Mirroring:** Fast screen captures using `mss` with real-time mouse cursor overlay.
- **Smart Scaling:** Enforces aspect ratio locking to prevent image distortion when resizing.
- **Borderless Mode:** Toggleable frameless window for a clean, distraction-free appearance.
- **Snap-to-Edge:** Easily snap the preview window to any edge or corner of your screen.
- **Context-Menu Driven:** All options (monitor swapping, layout changes, snapping) are accessible via a responsive right-click context menu.

## Setup and Installation

### Prerequisites
- Windows 10 / 11
- Python 3.10+

### Installation
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `.\venv\Scripts\activate`
4. Install dependencies: `pip install PyQt6 mss pyinstaller`

### Executing and Building
- Run directly: `python main.py`
- Build executable: `python build.py` (Outputs to `dist/`)

## License
MIT
