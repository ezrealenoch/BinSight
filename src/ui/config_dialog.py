from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QDialogButtonBox,
    QLabel, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Configuration")
        self.setMinimumWidth(500)

        # Main layout
        layout = QVBoxLayout(self)

        # Form layout for settings
        form_layout = QFormLayout()

        # Ollama URL
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("e.g., http://localhost:11434")
        form_layout.addRow(QLabel("Ollama API URL:"), self.ollama_url_input)

        # Ghidra Path
        self.ghidra_path_input = QLineEdit()
        self.ghidra_path_input.setPlaceholderText("Path to Ghidra installation directory")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_ghidra_path)
        
        ghidra_layout = QHBoxLayout()
        ghidra_layout.addWidget(self.ghidra_path_input)
        ghidra_layout.addWidget(browse_button)
        form_layout.addRow(QLabel("Ghidra Path:"), ghidra_layout)

        layout.addLayout(form_layout)

        # Dialog Buttons (OK, Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Load current settings into fields
        self._load_settings()

    def _load_settings(self):
        """Loads current settings from ConfigManager into the input fields."""
        self.ollama_url_input.setText(self.config_manager.get_ollama_url())
        self.ghidra_path_input.setText(self.config_manager.get_ghidra_path())

    def _browse_ghidra_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Ghidra Installation Directory", self.config_manager.get_ghidra_path())
        if directory:
            self.ghidra_path_input.setText(directory)

    def accept(self):
        """Saves the settings when OK is clicked."""
        self.config_manager.set_ollama_url(self.ollama_url_input.text().strip())
        self.config_manager.set_ghidra_path(self.ghidra_path_input.text().strip())
        self.config_manager.save()
        super().accept() # Call the base class accept

# Example Usage (for testing within this file)
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    # Need a dummy ConfigManager for testing
    from src.config_manager.manager import ConfigManager

    app = QApplication(sys.argv)
    
    # Ensure a ConfigManager instance is created
    config = ConfigManager()
    
    dialog = ConfigDialog(config)
    if dialog.exec_(): # Show the dialog modally
        print("Dialog accepted.")
        print(f"Saved Ollama URL: {config.get_ollama_url()}")
        print(f"Saved Ghidra Path: {config.get_ghidra_path()}")
    else:
        print("Dialog cancelled.")
    
    sys.exit()
