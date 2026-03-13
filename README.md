# OmniPeek

> [!IMPORTANT]
> The great majority of this app's code has been generated with help of an AI agent.
> This app wouldn't exist without this kind of support.

OmniPeek is a lightweight, scalable live-preview tool for Windows. I decided to create it because I wasn't happy with OnTopReplica not being able to display the entire display. This app is inspired by OnTopReplica and allows you to monitor the contents of one or two (or more?) external displays via a real-time, scaleable floating window on your primary display. In the **right-click menu** you can freely select which display(s) you want to see, select the display layout and toggle borderless mode. You can also quickly move the window to an edge or corner of your screen but I noticed it works better while in borderless mode. While in borderless mode you can drag the window around just by left-clicking it and holding. I created this app for fun and for my own needs and I'll be happy if others find use for it too.

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
1. Download the exe from releases and run.

or
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `.\venv\Scripts\activate`
4. Install dependencies: `pip install PyQt6 mss pyinstaller`

### Executing and Building
- Run directly: `python main.py`
- Build executable: `python build.py` (Outputs to `dist/`)

## License
MIT


