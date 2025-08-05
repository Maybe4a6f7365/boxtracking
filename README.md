# BoxTracker - Video Motion Tracking

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-orange.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)](https://www.linux.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/Maybe4a6f7365/boxtracking)

A simple web application that adds bounding boxes to moving objects in videos. Upload a video, configure some settings, and get back a version with tracked objects highlighted Features

- **Motion Detection**: Uses OpenCV's MOG2 background subtraction
- **Object Tracking**: Assigns IDs to moving objects and follows them between frames
- **Area Selection**: Option to limit tracking to a drawn rectangle area
- **Smart Filtering**: Remove jittery objects and size-based object filtering
- **Color Options**: Choose box colors (auto-contrast, white, black, blue, green, cyan, purple, orange)
- **Object Size Selection**: Target small objects (faces), medium objects (people), large objects (vehicles), or all sizes
- **Visual Options**: Show trail lines and coordinates for tracked objects

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Maybe4a6f7365/boxtracking.git
   cd boxtracking
   ```

2. **Run the start script:**
   ```bash
   ./start.sh
   ```

3. **Open the frontend:**
   - Open `index.html` in your browser
   - Backend runs on `http://localhost:5000`

## Manual Setup

1. **Install system dependencies:**
   ```bash
   # Arch
   sudo pacman -S python
   
   # Debian/Ubuntu
   sudo apt update && sudo apt install python3
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## Settings

- **Show trail lines**: Display movement trails for tracked objects
- **Box color**: Choose from auto-contrast, white, black, blue, green, cyan, purple, orange
- **Remove jittery objects**: Filters out erratic movements and camera shake artifacts
- **Object size to track**: Select small objects (faces, hands), medium objects (people, cars), large objects (vehicles, groups), or all sizes
- **Show coordinates**: Display (x,y) position next to tracked objects
- **Enable area selection**: Limit tracking to a user-drawn rectangle area with mobile/landscape format options

## Usage

1. **Upload Video**: Drag and drop or click to select (MP4, MOV, AVI, WEBM)
2. **Configure Settings**: Adjust the options as needed
3. **Area Selection (Optional)**:
   - Enable area selection checkbox
   - Draw a rectangle on the canvas
   - Double-click to clear
4. **Process & Download**: Wait for processing and download the result

## Technical Details

- **Backend**: Flask server that handles uploads and runs OpenCV processing
- **Frontend**: Clean HTML/CSS/JavaScript interface with modern styling
- **Detection**: MOG2 background subtraction with morphological operations
- **Tracking**: Distance-based matching with jitter detection and size filtering
- **Processing**: Runs in a separate thread with real-time status updates

## Project Structure

```
boxtracking/
├── app.py              # Flask backend with API endpoints
├── box_tracker.py      # Motion tracking algorithm
├── index.html          # Frontend interface
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── start.sh            # Startup script
├── uploads/            # Uploaded video files
└── outputs/            # Processed video files
```

## API Endpoints

- `POST /api/upload` - Upload video with settings
- `GET /api/status/<job_id>` - Check processing status
- `GET /api/download/<job_id>` - Download processed video
- `GET /api/health` - Health check

## Recent Updates

### v2.0 - Enhanced Tracking & Clean UI
- Jitter detection and removal for stable tracking
- Intuitive object size selection (small, medium, large, all)
- Simplified color options with professional naming
- Area selection with mobile/landscape format support
- Clean, modern interface without visual effects

### Performance Improvements
- Smart filtering reduces false positives
- Size-based object filtering for targeted tracking
- Improved movement validation algorithms
- Better user experience with "Back to Settings" option

## Contributing

Feel free to fork and submit pull requests. It's a simple project, so there's plenty of room for improvements.

## License

This project is open source and available under the MIT License.

## Credits

Created by Not4a6f7365