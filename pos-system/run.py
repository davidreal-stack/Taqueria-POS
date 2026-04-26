import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    # Attempt to open local default browser
    webbrowser.open_new("http://127.0.0.1:5000/")

def main():
    # Allow imports if run from executable/compiled bundle
    if getattr(sys, 'frozen', False):
        # We are running as bundled executable
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        sys.path.insert(0, sys._MEIPASS)
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from app import create_app
    app = create_app()
    
    print("========================================")
    print(" INICIANDO TAQUERIA POS SYSTEM EN LOCAL")
    print("========================================")
    
    # Start thread to open browser after short delay
    Timer(1.5, open_browser).start()
    
    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
