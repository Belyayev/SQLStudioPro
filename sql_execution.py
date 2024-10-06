import pandas as pd
import logging
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from sqlalchemy import text

def execute_sql(engine, query, output_table, status_bar):
    if not engine:
        QMessageBox.warning(None, "Connection Error", "Please connect to the database first.")
        logging.error("Execute SQL failed: No database connection.")
        return
    
    command = query.strip()
    logging.info(f"Executing SQL command: {command}")
    if command:
        try:
            if command.lower().startswith(('select', 'show', 'describe', 'explain')):
                df = pd.read_sql(command, engine)
                
                # Clear the table
                output_table.clear()
                output_table.setRowCount(len(df))
                output_table.setColumnCount(len(df.columns))
                
                # Insert column names
                output_table.setHorizontalHeaderLabels(df.columns)
                
                # Insert row data
                for row_idx, row in enumerate(df.itertuples(index=False)):
                    for col_idx, col_data in enumerate(row):
                        output_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
                
                output_table.resizeColumnsToContents()
                status_bar.showMessage("SQL command executed successfully")
            else:
                with engine.connect() as connection:
                    transaction = connection.begin()
                    try:
                        connection.execute(text(command))
                        transaction.commit()
                        status_bar.showMessage("SQL command executed successfully")
                        logging.info("SQL command executed successfully")
                    except Exception as e:
                        transaction.rollback()
                        logging.error(f"Error executing SQL command: {e}")
                        QMessageBox.critical(None, "Error", str(e))
                        status_bar.showMessage(f"Error executing query: {e}")
        except Exception as e:
            logging.error(f"Error executing SQL command: {e}")
            QMessageBox.critical(None, "Error", str(e))
            status_bar.showMessage(f"Error executing query: {e}")
