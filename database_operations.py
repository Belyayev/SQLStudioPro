from sqlalchemy import create_engine
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt
from sqlalchemy import text
import logging

def populate_database_list(engine, list_widget, status_bar, main_window):
    try:
        query = text("SELECT name FROM sys.databases")
        with engine.connect() as connection:
            result = connection.execute(query)
            databases = result.fetchall()
        
        # Clear existing items
        list_widget.clear()
        
        for db in databases:
            item = QListWidgetItem(db.name)
            item.setData(Qt.UserRole, db.name)
            list_widget.addItem(item)
            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setSelected(False)
        
        # Connect itemClicked signal only once
        if not hasattr(list_widget, 'itemClickedConnected'):
            list_widget.itemClicked.connect(lambda item: main_window.switch_database(item.data(Qt.UserRole)))
            list_widget.itemClickedConnected = True
        
        status_bar.showMessage("Databases loaded successfully.")
        logging.info("Databases loaded successfully.")
    except Exception as e:
        status_bar.showMessage(f"Error loading databases: {e}")
        logging.error(f"Error loading databases: {e}")

def switch_database(server_input, db_name, status_bar, tables_list_widget, main_window, old_engine=None):
    try:
        # Dispose of the old engine if it exists
        if old_engine:
            old_engine.dispose()
        
        # Create a new SQLAlchemy engine for the selected database
        server = server_input.currentText().strip()
        conn_str = f'mssql+pyodbc://{server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server&authentication=ActiveDirectoryIntegrated'
        new_engine = create_engine(conn_str)
        status_bar.showMessage(f"Switched to database: {db_name}")
        
        # Populate tables as list items
        populate_tables_list(new_engine, tables_list_widget, status_bar, main_window)
        return new_engine
    except Exception as e:
        status_bar.showMessage(f"Failed to switch database: {e}")
        logging.error(f"Failed to switch database: {e}")
        return None

def populate_tables_list(engine, tables_list_widget, status_bar, main_window):
    try:
        query = text("""
        SELECT 
            s.name AS schema_name,
            t.name AS table_name
        FROM 
            sys.tables t
        INNER JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        WHERE 
            t.is_external = 0
        ORDER BY 
            s.name, t.name;
        """)
        with engine.connect() as connection:
            result = connection.execute(query)
            tables = result.fetchall()
        
        # Clear existing items
        tables_list_widget.clear()
        
        for table in tables:
            item = QListWidgetItem(f"[{table.schema_name}].[{table.table_name}]")
            item.setData(Qt.UserRole, (table.schema_name, table.table_name))
            tables_list_widget.addItem(item)
        
        # Connect item click event to load_query method
        tables_list_widget.itemClicked.connect(lambda item: main_window.load_query(item.data(Qt.UserRole)))
        
        status_bar.showMessage("Tables loaded successfully.")
        logging.info("Tables loaded successfully.")
    except Exception as e:
        status_bar.showMessage(f"Failed to load tables: {e}")
        logging.error(f"Failed to load tables: {e}")
