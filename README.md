# BoxTracker - Video Motion Tracking


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-orange.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)](https://www.linux.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/Maybe4a6f7365/boxtracking)

Transform your videos with motion tracking effects. This application automatically detects and tracks moving objects in your videos, adding bounding boxes, coordinate displays, and lets you customize visual effects.

## Features

- **Real-time Object Detection**: Detect and track moving objects
- **Tracking Boxes**: Clean, minimal bounding boxes with precise coordinate display
- **Customizable Colors**: 8 different color modes including Matrix Green, Cyber Cyan, and Heat Vision
- **Shader Effects**: Basic glow and corner accent effects
- **Trail Lines**: Configurable motion trails that follow tracked objects
- **Coordinate Display**: Toggle-able coordinate text showing (x,y) positions
- **Easy to Use**: Simple drag-and-drop interface
- **Background Processing**: Videos are processed asynchronously with progress updates

## Installation

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Maybe4a6f7365/boxtracking.git
   cd boxtracking
   ```

2. **Run the start script:**
   ```bash
   ./start.sh
   ```

### Manual Setup

1. **Install system dependencies:**

   **Arch:**
   ```bash
   sudo pacman -S python
   ```
   **Debian:**
   ```bash
   sudo apt update
   sudo apt install python3
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   venv/bin/pip install --upgrade pip setuptools wheel
   venv/bin/pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   venv/bin/python app.py
   ```
6. **Open the Browser:**
   ```
   xdg-open $HOME/boxtracking/index.html
   ```


## Usage

1. **Start the application:**
   ```bash
   ./start.sh
   ```

2. **Open the frontend:**
   - Open the browser `xdg-open $HOME/boxtracking/index.html`
   - Backend runs on `http://localhost:5000`

## How It Works

1. **Motion Detection**: Uses MOG2 background subtraction to identify moving objects
2. **Object Tracking**: Detects and tracks bounding boxes around moving objects
3. **Visual Effects**: Applies customizable colors, shader effects, and trail lines
4. **Coordinate Display**: Shows precise positioning data for each tracked object
5. **Video Composition**: Overlays the tracking effects onto the original video

## Technical Stack

- **Backend**: Flask (Python)
- **Computer Vision**: OpenCV with MOG2 background subtraction
- **Frontend**: HTML5, CSS3, JavaScript with dark theme

## Project Structure

```boxtracking/
├── app.py              # Flask backend with API endpoints
├── box_tracker.py      # Motion tracking algorithm
├── index.html          # Frontend interface
├── README.md           # Project documentation
├── requirements.txt    # List of Python dependencies
├── start.sh            # Startup script for Bash shell
├── uploads/            # Directory for uploaded video files 
└── outputs/            # Directory for processed video files 
```


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Credits

Created by Not4a6f7365
