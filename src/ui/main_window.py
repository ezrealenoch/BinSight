import sys
import json # Import json for handling potential JSONDecodeError
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, 
    QFileDialog, QLineEdit, QTextEdit, QSplitter, QFormLayout, QTabWidget, 
    QMenuBar, QAction, QStatusBar, QMessageBox, QTreeWidget, QTreeWidgetItem, 
    QHBoxLayout, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication # For clipboard

# Import the CAPA parser functions
from src.capa_parser.parser import parse_capa_json # format_findings_for_display is no longer needed here
# Import Config Stuff
from src.config_manager.manager import ConfigManager
from src.ui.config_dialog import ConfigDialog 
# Import Ollama Stuff
from src.ollama_client.client import OllamaClient, OllamaError

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAPA-Ollama-Ghidra Inspector")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height

        # Initialize ConfigManager
        self.config_manager = ConfigManager()
        # Initialize OllamaClient (URL will be updated before use)
        self.ollama_client = OllamaClient(self.config_manager.get_ollama_url())

        self.capa_data = {} # To store the parsed findings {rule: [addr1, addr2]}

        self._create_menu_bar()
        self._create_status_bar()
        self._create_central_widget()

        self.show()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        # Load CAPA File Action
        load_action = QAction("&Load CAPA File...", self)
        load_action.triggered.connect(self._load_capa_file)
        file_menu.addAction(load_action)

        # Configuration Action
        config_action = QAction("&Configure", self)
        config_action.triggered.connect(self._open_config_dialog)
        file_menu.addAction(config_action)

        # Exit Action
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def _create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget) # Main layout for the central widget

        # Create a splitter for the main areas
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- Left Pane: CAPA Findings Tree --- #
        capa_widget = QWidget()
        capa_layout = QVBoxLayout(capa_widget)
        capa_label = QLabel("CAPA Findings (Select an address)")
        capa_layout.addWidget(capa_label)
        
        self.capa_findings_tree = QTreeWidget()
        self.capa_findings_tree.setHeaderLabels(["Rule / Address"])
        self.capa_findings_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.capa_findings_tree.itemClicked.connect(self._on_capa_item_selected)
        capa_layout.addWidget(self.capa_findings_tree)
        splitter.addWidget(capa_widget)

        # --- Right Pane: Interaction & Results (Using Tabs) --- #
        right_pane_widget = QWidget()
        right_pane_layout = QVBoxLayout(right_pane_widget)

        tab_widget = QTabWidget()
        right_pane_layout.addWidget(tab_widget)

        # Ghidra/Ollama Interaction Tab
        interaction_tab = QWidget()
        interaction_layout = QFormLayout(interaction_tab) # Use QFormLayout for label-field pairs
        interaction_tab.setObjectName("InteractionTab") # Set object name

        # Selected Address Area
        self.selected_address_label = QLabel("Selected Address:")
        self.selected_address_display = QLineEdit()
        self.selected_address_display.setReadOnly(True)
        self.copy_address_button = QPushButton("Copy Address")
        self.copy_address_button.clicked.connect(self._copy_selected_address)
        self.copy_address_button.setEnabled(False) # Disable initially
        
        address_layout = QHBoxLayout()
        address_layout.addWidget(self.selected_address_display)
        address_layout.addWidget(self.copy_address_button)
        interaction_layout.addRow(self.selected_address_label, address_layout)

        # Ghidra Instructions
        self.ghidra_instructions_label = QLabel(
            "<b>Ghidra Navigation:</b><br>" 
            "1. Copy the address above.<br>" 
            "2. In Ghidra, press 'G' (Go To).<br>" 
            "3. Paste the address and press Enter.<br>"
            "4. Select the relevant code block.<br>"
            "5. Copy the code (Ctrl+C)."
        )
        self.ghidra_instructions_label.setWordWrap(True)
        self.ghidra_instructions_label.setAlignment(Qt.AlignTop)
        interaction_layout.addRow(QLabel("Instructions:"), self.ghidra_instructions_label)

        # Code Input Area
        self.code_input_label = QLabel("Paste Ghidra Code:")
        self.code_input_area = QTextEdit()
        self.code_input_area.setPlaceholderText("Paste Ghidra code snippet here after navigation...")
        interaction_layout.addRow(self.code_input_label, self.code_input_area)
        
        # Ollama Prompt
        self.ollama_prompt_label = QLabel("Ollama Prompt:")
        self.ollama_prompt_input = QLineEdit()
        self.ollama_prompt_input.setPlaceholderText("Enter your question/prompt for Ollama...")
        interaction_layout.addRow(self.ollama_prompt_label, self.ollama_prompt_input)
        
        # Submit Button (aligned to the right, maybe?)
        self.submit_to_ollama_button = QPushButton("Analyze with Ollama")
        self.submit_to_ollama_button.clicked.connect(self._submit_to_ollama)
        interaction_layout.addRow("", self.submit_to_ollama_button) # Add button without a label on the left

        tab_widget.addTab(interaction_tab, "Interaction")

        # Ollama Results Tab
        results_tab = QWidget()
        results_tab.setObjectName("ResultsTab") # Set object name
        results_layout = QVBoxLayout(results_tab)
        results_layout.addWidget(QLabel("Ollama Analysis Result"))
        self.ollama_results_view = QTextEdit("Ollama analysis results will appear here.")
        self.ollama_results_view.setReadOnly(True)
        results_layout.addWidget(self.ollama_results_view)
        # Add reference back to CAPA/Address?
        self.analysis_context_label = QLabel("Analysis Context: (Load CAPA and select address first)")
        self.analysis_context_label.setWordWrap(True)
        results_layout.insertWidget(1, self.analysis_context_label) # Insert before results view
        tab_widget.addTab(results_tab, "Results")

        # Store reference to tab widget to switch tabs programmatically
        self.tab_widget = tab_widget 

        splitter.addWidget(right_pane_widget)

        # Adjust splitter sizes (optional)
        splitter.setSizes([400, 800]) # Initial sizes for left and right panes

    def _open_config_dialog(self):
        # Instantiate and show the configuration dialog
        config_dialog = ConfigDialog(self.config_manager, self)
        if config_dialog.exec_(): # Show the dialog modally
            self.statusBar.showMessage("Configuration saved.", 3000)
            print("Configuration dialog accepted and settings saved.")
            # Optionally update Ghidra instructions if path changed?
        else:
            self.statusBar.showMessage("Configuration cancelled.", 3000)
            print("Configuration dialog cancelled.")

    def _load_capa_file(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Load CAPA Output File", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if file_name:
            try:
                self.statusBar.showMessage(f"Loading CAPA file: {file_name}...")
                # Reset UI elements related to previous file
                self.capa_findings_tree.clear()
                self.selected_address_display.clear()
                self.copy_address_button.setEnabled(False)
                self.code_input_area.clear()
                self.ollama_results_view.clear()
                self.analysis_context_label.setText("Analysis Context: (Load CAPA and select address first)") # Reset context label
                
                # Call the parser
                self.capa_data = parse_capa_json(file_name) # Store the parsed data
                
                # Update the QTreeWidget
                self._populate_capa_tree()
                
                self.statusBar.showMessage(f"Successfully loaded CAPA file: {file_name}", 5000) # Show message for 5 seconds
                print(f"Successfully parsed CAPA file: {file_name}")

            except FileNotFoundError:
                QMessageBox.critical(self, "Error", f"File not found: {file_name}")
                self.statusBar.showMessage("Error: File not found.")
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", f"Invalid JSON format in file: {file_name}")
                self.statusBar.showMessage("Error: Invalid JSON format.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred while parsing {file_name}:\n{e}")
                self.statusBar.showMessage(f"Error parsing file: {e}")
                print(f"Error parsing {file_name}: {e}")
        else:
            self.statusBar.showMessage("No CAPA file selected.")

    def _populate_capa_tree(self):
        self.capa_findings_tree.clear()
        if not self.capa_data:
            # Display a message if no findings were parsed or the file was empty/invalid
            placeholder_item = QTreeWidgetItem(self.capa_findings_tree, ["No address findings in loaded file."])
            placeholder_item.setDisabled(True)
            return

        for rule_name, addresses in self.capa_data.items():
            rule_item = QTreeWidgetItem(self.capa_findings_tree, [rule_name])
            rule_item.setData(0, Qt.UserRole, {"type": "rule"}) # Store type info
            for addr in addresses:
                addr_item = QTreeWidgetItem(rule_item, [addr])
                addr_item.setData(0, Qt.UserRole, {"type": "address", "value": addr}) # Store type and value
            rule_item.setExpanded(True) # Optionally expand rules

    def _on_capa_item_selected(self, item, column):
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data.get("type") == "address":
            address = item_data.get("value")
            self.selected_address_display.setText(address)
            self.copy_address_button.setEnabled(True)
            self.statusBar.showMessage(f"Selected address: {address}", 3000)
        else:
            # Clear display and disable copy if a rule or non-address item is clicked
            self.selected_address_display.clear()
            self.copy_address_button.setEnabled(False)

    def _copy_selected_address(self):
        address = self.selected_address_display.text()
        if address:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(address)
            self.statusBar.showMessage(f"Address {address} copied to clipboard.", 3000)

    def _submit_to_ollama(self):
        code_snippet = self.code_input_area.toPlainText().strip()
        prompt = self.ollama_prompt_input.text().strip()
        selected_address = self.selected_address_display.text() # Get context

        if not code_snippet:
            QMessageBox.warning(self, "Input Missing", "Please paste code from Ghidra into the 'Paste Ghidra Code' area.")
            self.statusBar.showMessage("Input Missing: Code snippet required.")
            return
        if not prompt:
            QMessageBox.warning(self, "Input Missing", "Please enter a prompt for Ollama.")
            self.statusBar.showMessage("Input Missing: Ollama prompt required.")
            return

        try:
            # Ensure the client is using the latest configured URL
            current_ollama_url = self.config_manager.get_ollama_url()
            if not current_ollama_url:
                 QMessageBox.critical(self, "Configuration Error", "Ollama URL is not configured. Please set it via File -> Configure.")
                 self.statusBar.showMessage("Ollama URL not configured.")
                 return
                 
            self.ollama_client.base_url = current_ollama_url.rstrip('/')
            self.ollama_client.generate_endpoint = f"{self.ollama_client.base_url}/api/generate"
            
            self.statusBar.showMessage("Submitting to Ollama... Please wait.")
            QApplication.processEvents() # Update UI to show status message

            # Optional: Add context to the results display
            context = f"Analysis for Address: {selected_address if selected_address else 'N/A'}"
            self.analysis_context_label.setText(context)
            self.ollama_results_view.clear() # Clear previous results

            # Call the Ollama client
            # TODO: Make model configurable?
            analysis_result = self.ollama_client.analyze_code(code_snippet, prompt, model="llama3")

            # Display the result
            self.ollama_results_view.setText(analysis_result)
            self.statusBar.showMessage("Ollama analysis complete.", 5000)
            print("Ollama analysis successful.")

            # Switch to the results tab
            results_tab_widget = self.tab_widget.findChild(QWidget, "ResultsTab")
            if results_tab_widget:
                self.tab_widget.setCurrentWidget(results_tab_widget)
            else:
                print("Error: Could not find 'ResultsTab' widget to switch to.")

        except OllamaError as e:
            error_message = f"Ollama Error: {e}"
            print(error_message)
            QMessageBox.critical(self, "Ollama Error", error_message)
            self.statusBar.showMessage(f"Error communicating with Ollama: {e}")
            # Clear potentially incomplete results
            self.ollama_results_view.clear()
            self.analysis_context_label.setText("Analysis Context: Error occurred")
        except Exception as e:
            # Catch any other unexpected errors
            error_message = f"An unexpected error occurred: {e}"
            print(error_message)
            QMessageBox.critical(self, "Unexpected Error", error_message)
            self.statusBar.showMessage("An unexpected error occurred.")
            self.ollama_results_view.clear()
            self.analysis_context_label.setText("Analysis Context: Error occurred")
        finally:
             # Re-enable button? Consider disabling it during processing.
             pass # For now, keep it enabled

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())

# This check ensures the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()
