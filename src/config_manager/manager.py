from PyQt5.QtCore import QSettings

# Define constants for settings keys
CONFIG_OLLAMA_URL = "ollama/url"
CONFIG_GHIDRA_PATH = "ghidra/path"

# Define default values
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_GHIDRA_PATH = ""

class ConfigManager:
    def __init__(self, organization="BinSight", application="CAPA-Ollama-Ghidra-Inspector"):
        """Initializes the QSettings object."""
        # Using organization and application name helps QSettings find the right storage location
        self.settings = QSettings(organization, application)

    def get_ollama_url(self):
        """Retrieves the Ollama API URL from settings, returning the default if not set."""
        return self.settings.value(CONFIG_OLLAMA_URL, DEFAULT_OLLAMA_URL)

    def set_ollama_url(self, url):
        """Saves the Ollama API URL to settings."""
        self.settings.setValue(CONFIG_OLLAMA_URL, url)

    def get_ghidra_path(self):
        """Retrieves the Ghidra installation path from settings, returning the default if not set."""
        return self.settings.value(CONFIG_GHIDRA_PATH, DEFAULT_GHIDRA_PATH)

    def set_ghidra_path(self, path):
        """Saves the Ghidra installation path to settings."""
        self.settings.setValue(CONFIG_GHIDRA_PATH, path)

    def save(self):
        """Explicitly saves the settings (QSettings often saves automatically, but good practice)."""
        self.settings.sync()

# Example Usage (for testing)
if __name__ == '__main__':
    config = ConfigManager()
    print(f"Default Ollama URL: {config.get_ollama_url()}")
    print(f"Default Ghidra Path: {config.get_ghidra_path()}")

    # Example of setting and retrieving
    config.set_ollama_url("http://192.168.1.100:11434")
    config.set_ghidra_path("C:/ghidra_11.0")
    config.save()

    print(f"New Ollama URL: {config.get_ollama_url()}")
    print(f"New Ghidra Path: {config.get_ghidra_path()}")

    # Reset to defaults for next run (optional)
    # config.settings.remove(CONFIG_OLLAMA_URL)
    # config.settings.remove(CONFIG_GHIDRA_PATH)
    # config.save()
    # print("Settings reset.")
