# SoulPlanner Task Tracker

A modern, feature-rich task tracker application with project management, filtering, and a beautiful UI.

## Features
- Add, edit, and delete tasks with due dates, priorities, and notes
- Project management: create, delete (soft/hard), and switch between projects
- Date, status, and priority filtering
- Responsive, modern UI with dark/light mode
- Data stored in a local SQLite database
- One-click EXE build for Windows

## Installation

### Requirements
- Python 3.8+
- pip

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the app
```bash
python main.py
```

### Build a Windows EXE
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the EXE:
   ```bash
   pyinstaller --noconfirm --onefile --windowed main.py
   ```
3. The EXE will be in the `dist/` folder.

## Git Usage

1. Initialize git (if not already):
   ```bash
   git init
   ```
2. Add and commit your files:
   ```bash
   git add .
   git commit -m "Initial commit"
   ```
3. Add your remote and push:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

## Credits
- **Logiciel creator:** YAELDI1
- UI/UX: Modern, vivid color scheme
- Built with Python, Tkinter, ttkbootstrap

---

For any issues or contributions, please open an issue or pull request on GitHub. 