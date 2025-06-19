import sys
import os
import subprocess
import webbrowser
import threading
import time
import requests
import multiprocessing
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QTextEdit, QLabel, QGridLayout, QGroupBox,
                           QHBoxLayout, QLineEdit, QTabWidget, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QProcess
from PyQt5.QtGui import QFont, QIcon, QTextCursor

from dotenv import load_dotenv
from kiteconnect import KiteConnect

from src.kite_utils import KiteHelper


class KiteLoginManager:
    """Handles the login and token generation process for Kite Connect"""
    
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key or os.getenv("KITE_API_KEY")
        self.api_secret = api_secret or os.getenv("KITE_API_SECRET")
        self.kite = KiteConnect(api_key=self.api_key)
        
    def get_login_url(self):
        """Returns the URL where the user should login to Kite"""
        return self.kite.login_url()
    
    def generate_access_token(self, request_token):
        """Exchanges request token for access token"""
        if not request_token:
            raise ValueError("Request token is required")
            
        data = self.kite.generate_session(request_token, api_secret=self.api_secret)
        access_token = data["access_token"]
        return access_token
    
    def update_env_file(self, access_token):
        """Updates the .env file with the new access token"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        # Read the current content of the .env file
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                env_content = f.readlines()
            
            # Update or add the access token
            token_updated = False
            for i, line in enumerate(env_content):
                if line.startswith("KITE_ACCESS_TOKEN="):
                    env_content[i] = f'KITE_ACCESS_TOKEN="{access_token}"\n'
                    token_updated = True
                    break
            
            if not token_updated:
                env_content.append(f'KITE_ACCESS_TOKEN="{access_token}"\n')
        else:
            # Create a new .env file if it doesn't exist
            env_content = [
                f'KITE_API_KEY="{self.api_key}"\n',
                f'KITE_API_SECRET="{self.api_secret}"\n',
                f'KITE_ACCESS_TOKEN="{access_token}"\n'
            ]
        
        # Write the updated content back to the .env file
        with open(env_path, "w") as f:
            f.writelines(env_content)


class LogRedirector:
    """Redirects standard output and error to a QTextEdit widget"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def write(self, text):
        # Write both to the original stdout and to the text widget
        self.original_stdout.write(text)
        self.text_widget.moveCursor(QTextCursor.End)
        self.text_widget.insertPlainText(text)
    
    def flush(self):
        self.original_stdout.flush()


class APIServerProcess(multiprocessing.Process):
    """Process that runs the FastAPI server"""
    
    def __init__(self, gui):
        super().__init__()
        self.gui = gui
        self.daemon = True
        self.running = False
        
    def run(self):
        self.running = True
        try:
            from src.main import start_server
            start_server()
        except Exception as e:
            print(f"Error in API server: {e}")
        finally:
            self.running = False
    
    def stop(self):
        if self.running and self.is_alive():
            self.terminate()
            self.join(timeout=5)  # Wait up to 5 seconds for the process to stop
            self.running = False


class ClaudeTraderGUI(QMainWindow):
    """Main GUI window for the Claude-Python Trading Bot"""
    
    def __init__(self):
        super().__init__()
        self.login_manager = KiteLoginManager()
        self.server_process = None
        
        load_dotenv()  # Load environment variables
        
        self.init_ui()
        self.update_server_status()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Claude-Python Trading Bot")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        self.server_tab = QWidget()
        self.token_tab = QWidget()
        self.help_tab = QWidget()
        
        tab_widget.addTab(self.server_tab, "Server Control")
        tab_widget.addTab(self.token_tab, "Token Management")
        tab_widget.addTab(self.help_tab, "Help")
        
        # Set up the server control tab
        self.setup_server_tab()
        
        # Set up the token management tab
        self.setup_token_tab()
        
        # Set up the help tab
        self.setup_help_tab()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create server status label in status bar
        self.server_status_label = QLabel("Server status: Not running")
        self.status_bar.addPermanentWidget(self.server_status_label)
        
    def setup_server_tab(self):
        """Set up the server control tab"""
        layout = QVBoxLayout(self.server_tab)
        
        # Create controls
        control_group = QGroupBox("Server Control")
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Trading API Server")
        self.start_button.clicked.connect(self.start_server)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Trading API Server")
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Create log output
        log_group = QGroupBox("Server Log")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_output)
        
        # Redirect stdout to log output
        sys.stdout = LogRedirector(self.log_output)
        sys.stderr = LogRedirector(self.log_output)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def setup_token_tab(self):
        """Set up the token management tab"""
        layout = QVBoxLayout(self.token_tab)
        
        # Create step-by-step instructions
        instructions_group = QGroupBox("How to Generate an Access Token")
        instructions_layout = QVBoxLayout()
        
        instructions = QLabel("""
        <ol>
            <li>Click the "Open Zerodha Login" button below.</li>
            <li>Log in to your Zerodha account.</li>
            <li>After successful login, you'll be redirected to a new page.</li>
            <li>Copy the request token from the URL parameter.</li>
            <li>Paste the request token in the field below and click Generate.</li>
        </ol>
        """)
        instructions.setWordWrap(True)
        instructions_layout.addWidget(instructions)
        
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        # Create login button
        login_group = QGroupBox("Step 1: Login to Zerodha")
        login_layout = QVBoxLayout()
        
        login_button = QPushButton("Open Zerodha Login")
        login_button.clicked.connect(self.open_kite_login)
        login_layout.addWidget(login_button)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # Create token input field
        token_group = QGroupBox("Step 2: Generate Access Token")
        token_layout = QGridLayout()
        
        token_label = QLabel("Request Token:")
        token_layout.addWidget(token_label, 0, 0)
        
        self.token_input = QLineEdit()
        token_layout.addWidget(self.token_input, 0, 1)
        
        token_button = QPushButton("Generate Access Token")
        token_button.clicked.connect(self.generate_access_token)
        token_layout.addWidget(token_button, 1, 1, Qt.AlignRight)
        
        current_token_label = QLabel("Current Token:")
        token_layout.addWidget(current_token_label, 2, 0)
        
        self.current_token_display = QLineEdit()
        self.current_token_display.setReadOnly(True)
        self.current_token_display.setText(os.getenv("KITE_ACCESS_TOKEN", "No token found"))
        token_layout.addWidget(self.current_token_display, 2, 1)
        
        token_group.setLayout(token_layout)
        layout.addWidget(token_group)
        
    def setup_help_tab(self):
        """Set up the help tab"""
        layout = QVBoxLayout(self.help_tab)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        
        help_content = """
        <h1>Claude-Python Trading Bot Help</h1>
        
        <h2>Getting Started</h2>
        <ol>
            <li>First, generate a Zerodha access token in the Token Management tab.</li>
            <li>Then, start the API server in the Server Control tab.</li>
            <li>Finally, open Claude in the desktop app and initiate a conversation.</li>
        </ol>
        
        <h2>Using Claude with the Trading Bot</h2>
        <p>Once the server is running, you can ask Claude to perform trading actions like:</p>
        <ul>
            <li>"Buy 10 shares of INFY at market price."</li>
            <li>"Show me my current holdings."</li>
            <li>"Sell 5 shares of TCS at limit price 3600."</li>
        </ul>
        
        <h2>Troubleshooting</h2>
        <p>If you encounter issues:</p>
        <ul>
            <li>Check that your Zerodha API key and access token are valid</li>
            <li>Make sure the API server is running before connecting with Claude</li>
            <li>Remember that access tokens expire daily</li>
        </ul>
        """
        
        help_text.setHtml(help_content)
        layout.addWidget(help_text)
    
    def open_kite_login(self):
        """Open Kite login page in the default browser"""
        login_url = self.login_manager.get_login_url()
        webbrowser.open(login_url)
    
    def generate_access_token(self):
        """Generate and save a new access token"""
        request_token = self.token_input.text().strip()
        
        if not request_token:
            QMessageBox.warning(self, "Token Error", "Please enter a request token.")
            return
            
        try:
            access_token = self.login_manager.generate_access_token(request_token)
            self.login_manager.update_env_file(access_token)
            self.current_token_display.setText(access_token)
            
            QMessageBox.information(
                self, "Success", 
                "Access token generated and saved to .env file successfully!"
            )
            
            # Clear the request token input
            self.token_input.clear()
            
            # Reload environment variables
            load_dotenv(override=True)
        except Exception as e:
            QMessageBox.critical(self, "Token Error", f"Error generating access token: {e}")
    
    def start_server(self):
        """Start the API server in a separate process"""
        if not hasattr(self, 'server_process') or not self.server_process.running:
            self.server_process = APIServerProcess(self)
            self.server_process.start()
            
            # Wait a moment for the server to start
            time.sleep(1.0)
            self.update_server_status()
            
            self.log_output.append("Starting Trading API server...\n")
    
    def stop_server(self):
        """Stop the API server"""
        if hasattr(self, 'server_process') and self.server_process.running:
            self.log_output.append("Stopping Trading API server...\n")
            self.server_process.stop()
            self.update_server_status()
    def update_server_status(self):
        """Update the server status display"""
        running = hasattr(self, 'server_process') and self.server_process is not None and self.server_process.is_alive()
        
        if running:
            self.server_status_label.setText("Server status: Running")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.server_status_label.setText("Server status: Not running")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if hasattr(self, 'server_process') and self.server_process.is_alive():
            # Stop the server before closing
            self.stop_server()
        
        # Restore the original stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        event.accept()


def main():
    """Main entry point for the GUI application"""
    # Check for --api-only flag
    if "--api-only" in sys.argv:
        # Run only the API server without the GUI
        from src.main import main as run_api_server
        run_api_server()
        return
        
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = ClaudeTraderGUI()
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
