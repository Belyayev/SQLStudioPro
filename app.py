import sys
import logging
import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from ui_setup import setup_ui
from database_operations import switch_database, populate_database_list
from sql_execution import execute_sql, text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SQLManagementStudioPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL Server Management Studio PRO")
        self.setGeometry(100, 100, 800, 600)
        
        # Setup UI
        self.ui = setup_ui(self)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Enter server and database details to connect.")
        
        # Initialize the engine attribute
        self.engine = None
        logging.info("Initialized SQLManagementStudioPro with no engine.")
        
        # Check and create the SQLite database and table
        self.check_and_create_database()

        # Fetch and populate server list
        self.fetch_and_populate_server_list()

        # Connect the textChanged signal to the on_text_changed method
        self.ui.sql_input.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self):
        self.ui.formatter.format_text(self.ui.sql_input)
    
    def check_and_create_database(self):
        db_name = 'SQL_Pro_data.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Create queries table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                dbName TEXT(100),
                tableName TEXT(100),
                query TEXT,
                UNIQUE(dbName, tableName)
            )
        ''')

        # Create serverList table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS serverList (
                serverName TEXT PRIMARY KEY
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info(f"Database '{db_name}' checked and table 'queries' created if it didn't exist.")

    def fetch_and_populate_server_list(self):
        db_name = 'SQL_Pro_data.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT serverName FROM serverList')
        servers = cursor.fetchall()
        
        conn.close()
        
        logging.info(servers)
        # Extract the first element from each tuple
        server_names = [str(server)[2:-3] for server in servers if server]  # Ensure no empty strings are added
        logging.info(server_names)
        self.ui.server_input.addItems(server_names)
        logging.info("Server list populated from database.")


    def load_query(self, table_info):
        logging.info(f"Attempting to load query for table: {table_info}")
        schema_name, table_name = table_info
        
        # Fetch the query from the SQLite database
        db_name = 'SQL_Pro_data.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT query FROM queries WHERE dbName = ? AND tableName = ?
        ''', (schema_name, table_name))
        
        result = cursor.fetchone()
        if result:
            query = result  # Extract the query string from the tuple
            if isinstance(query, bytes):
                query = query.decode('utf-8')  # Decode if it's stored as bytes
            
            # Ensure the query is a string and trim the first two and last three characters
            if isinstance(query, str):
                trimmed_query = query[2:-3]
                self.ui.sql_input.setHtml(trimmed_query)  # Set the HTML representation back to the QTextEdit
            else:
                trimmed_query = str(query)[2:-3]
                self.ui.sql_input.setHtml(trimmed_query)
        else:
            query = f'SELECT * FROM [{schema_name}].[{table_name}]'
            self.ui.sql_input.setPlainText(query)
        
        conn.close()
        
        # Run a SELECT COUNT(*) query to get the total number of records from SQL Server
        if not self.engine:
            QMessageBox.warning(None, "Connection Error", "Please connect to the database first.")
            logging.error("Execute SQL failed: No database connection.")
            return
        
        try:
            with self.engine.connect() as connection:
                count_query = text(f'SELECT COUNT(*) FROM [{schema_name}].[{table_name}]')
                result = connection.execute(count_query)
                record_count = result.scalar()

                # Format the record count with commas
                formatted_count = f"{record_count:,}"
                
                # Update the info_label with the table name and record count
                self.ui.info_label.setText(f"Tablename: <b>[{schema_name}].[{table_name}]</b> | Total records: <b>{formatted_count}</b>")
        except Exception as e:
            logging.error(f"Error executing SQL command: {e}")
            QMessageBox.critical(None, "Error", str(e))
            self.status_bar.showMessage(f"Error executing query: {e}")
        
        logging.info(f"Loaded query for table: [{schema_name}].[{table_name}]")

    def save_query(self):
        current_item = self.ui.tables_list_widget.currentItem()
        if current_item:
            table_info = current_item.data(Qt.UserRole)
            logging.info(f"Current item data: {table_info}")
            if table_info:
                server_name, table_name = table_info
                query_html = self.ui.sql_input.toHtml()  # Get the HTML representation of the text
                
                # Remove newline characters from the HTML content
                query_html_cleaned = query_html.replace('\n', '')
                
                db_name = 'SQL_Pro_data.db'
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO queries (dbName, tableName, query) VALUES (?, ?, ?)
                    ON CONFLICT(dbName, tableName) DO UPDATE SET query = excluded.query
                ''', (server_name, table_name, query_html_cleaned))
                
                conn.commit()
                conn.close()
                logging.info(f"Saved query for table: [{server_name}].[{table_name}]")
                self.status_bar.showMessage("Query saved successfully.")
            else:
                QMessageBox.warning(self, "Save Error", "No table information available.")
                logging.error("Save query failed: No table information available.")
        else:
            QMessageBox.warning(self, "Save Error", "No table selected.")
            logging.error("Save query failed: No table selected.")

    def initial_connect(self):
        db_name = 'master'
        server_name = self.ui.server_input.currentText()

        if not server_name:
            QMessageBox.warning(None, "Input Error", "Please enter the server name.")
            return None, None

        self.engine = switch_database(self.ui.server_input, db_name, self.status_bar, self.ui.tables_list_widget, self)
        if self.engine:
            populate_database_list(self.engine, self.ui.database_list_widget, self.status_bar, self)
            logging.info("Initial connection established.")

            # Save the server name to the serverList table
            db_name = 'SQL_Pro_data.db'
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO serverList (serverName) VALUES (?)
            ''', (server_name,))
            conn.commit()
            conn.close()
            logging.info(f"Server name '{server_name}' saved to serverList.")
             # Add the server name to the QComboBox if it's not already there
            if server_name not in [self.ui.server_input.itemText(i) for i in range(self.ui.server_input.count())]:
                self.ui.server_input.addItem(server_name)
        else:
            logging.error("Initial connection failed.")

    def switch_database(self, db_name):
        if db_name:
            self.engine = switch_database(self.ui.server_input, db_name, self.status_bar, self.ui.tables_list_widget, self.engine)
            if self.engine:
                logging.info(f"Switched to database: {db_name}")
            else:
                logging.error(f"Failed to switch to database: {db_name}")
    
    def execute_sql(self):
        if not self.engine:
            QMessageBox.warning(self, "Connection Error", "Please connect to the database first.")
            logging.error("Execute SQL failed: No database connection.")
            return
        
        cursor = self.ui.sql_input.textCursor()
        if cursor.hasSelection():
            query = cursor.selectedText().strip()
        else:
            query = self.ui.sql_input.toPlainText().strip()
        
        execute_sql(self.engine, query, self.ui.output_table, self.status_bar)
    
    def filter_tables(self):
        filter_text = self.ui.table_filter_input.text().lower()
        for i in range(self.ui.tables_list_widget.count()):
            item = self.ui.tables_list_widget.item(i)
            if filter_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def capitalize_sql_commands(self):
        cursor = self.ui.sql_input.textCursor()
        text = self.ui.sql_input.toPlainText()
        capitalized_text = self.ui.formatter.capitalize_sql_commands(text)
        self.ui.sql_input.blockSignals(True)
        self.ui.sql_input.setPlainText(capitalized_text)
        self.ui.sql_input.blockSignals(False)
        self.ui.sql_input.setTextCursor(cursor)

    def show_table_schema(self):
        current_item = self.ui.tables_list_widget.currentItem()
        if current_item:
            table_info = current_item.data(Qt.UserRole)
            if not table_info:
                QMessageBox.warning(self, "Selection Error", "Please select a table first.")
                return
            
            schema_name, table_name = table_info
            
            # SQL query to get table schema
            query = f"""
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH, 
                IS_NULLABLE
            FROM 
                INFORMATION_SCHEMA.COLUMNS
            WHERE 
                TABLE_SCHEMA = '{schema_name}' 
                AND TABLE_NAME = '{table_name}';
            """
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                schema_details = result.fetchall()
                
                # Display schema details in the output table
                self.ui.output_table.clear()
                self.ui.output_table.setRowCount(len(schema_details))
                self.ui.output_table.setColumnCount(4)
                self.ui.output_table.setHorizontalHeaderLabels(['Column Name', 'Data Type', 'Max Length', 'Is Nullable'])
                
                for row_idx, row in enumerate(schema_details):
                    for col_idx, col_data in enumerate(row):
                        self.ui.output_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
                
                self.ui.output_table.resizeColumnsToContents()
                self.status_bar.showMessage("Schema details loaded successfully")
        except Exception as e:
            logging.error(f"Error executing SQL command: {e}")
            QMessageBox.critical(self, "Error", str(e))
            self.status_bar.showMessage(f"Error executing query: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLManagementStudioPro()
    window.showMaximized()
    sys.exit(app.exec())
