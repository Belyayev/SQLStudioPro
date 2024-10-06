from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QSplitter, QLineEdit, QComboBox, QSizePolicy, QTableWidget, QListWidget, QLabel
from PySide6.QtCore import Qt
from sql_formatter import SQLFormatter

class UIComponents:
    def __init__(self):
        self.server_input = None
        self.database_list_widget = None
        self.tables_list_widget = None
        self.sql_input = None
        self.output_table = None
        self.formatter = None
        self.table_filter_input = None
        self.save_button = None
        self.info_label = None

def setup_ui(main_window):
    ui = UIComponents()
    
    # Main widget
    main_widget = QWidget()
    main_window.setCentralWidget(main_widget)
    
    # Main layout
    main_layout = QHBoxLayout(main_widget)
    
    # Splitter for sidebar and main content
    main_splitter = QSplitter(Qt.Horizontal)
    main_layout.addWidget(main_splitter)
    
    # Sidebar layout
    sidebar_widget = QWidget()
    sidebar_layout = QVBoxLayout(sidebar_widget)
    sidebar_layout.setAlignment(Qt.AlignTop)
    main_splitter.addWidget(sidebar_widget)
    
    # Server name input
    ui.server_input = QComboBox()
    ui.server_input.setEditable(True)
    ui.server_input.setPlaceholderText("Server Name")
    ui.server_input.setStyleSheet("border: none; border-bottom: 1px solid lightgray;")
    ui.server_input.setStyleSheet("""
    QComboBox {
        background-color: white;
        border: none;
        border-bottom: 1px solid lightgray;
    }
    QComboBox QAbstractItemView {
        background-color: white;
    }
    """)
    sidebar_layout.addWidget(ui.server_input)
    
    # Connect button with custom style
    connect_button = QPushButton("Connect to Database")
    connect_button.setStyleSheet("""
        QPushButton {
            font-weight: bold;
            color: black;
            background-color: lightGreen;
            border: 1px solid lightGreen;
            padding: 3px 6px;
        }
        QPushButton:hover {
            background-color: lightYellow;
            border: 1px solid lightYellow;
        }
    """)
    connect_button.clicked.connect(main_window.initial_connect)
    
    # Center-align the Connect button
    connect_button_layout = QHBoxLayout()
    connect_button_layout.addStretch()
    connect_button_layout.addWidget(connect_button)
    connect_button_layout.addStretch()
    sidebar_layout.addLayout(connect_button_layout)
    
    # Splitter for database and table lists
    list_splitter = QSplitter(Qt.Vertical)
    sidebar_layout.addWidget(list_splitter)
    
    # List widget for database buttons
    ui.database_list_widget = QListWidget()
    list_splitter.addWidget(ui.database_list_widget)
    
    # List widget for table buttons
    ui.tables_list_widget = QListWidget()
    list_splitter.addWidget(ui.tables_list_widget)
    
    # Set initial sizes for the lists
    list_splitter.setSizes([100, 200])
    
    # Table filter input
    ui.table_filter_input = QLineEdit()
    ui.table_filter_input.setPlaceholderText("Filter tables...")
    ui.table_filter_input.setStyleSheet("border: none; border-bottom: 1px solid lightgray;")
    ui.table_filter_input.textChanged.connect(main_window.filter_tables)
    sidebar_layout.addWidget(ui.table_filter_input)
    
    # Splitter for input and output
    content_splitter = QSplitter(Qt.Vertical)
    main_splitter.addWidget(content_splitter)
    main_splitter.setStretchFactor(1, 1)
    
    # SQL input layout
    sql_input_layout = QVBoxLayout()
    
    # Save and Execute buttons with custom style
    ui.save_button = QPushButton("Save")
    ui.save_button.setStyleSheet("""
        QPushButton {
            font-weight: bold;
            color: black;
            background-color: skyBlue;
            border: 1px solid skyBlue;
            padding: 3px 8px;
        }
        QPushButton:hover {
            border: 1px solid lightYellow;
            background-color: lightYellow;
        }
    """)
    ui.save_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    ui.save_button.clicked.connect(main_window.save_query)
    
    execute_button = QPushButton("Run >")
    execute_button.setStyleSheet("""
        QPushButton {
            font-weight: bold;
            color: black;
            background-color: lightGreen;
            border: 1px solid lightGreen;
            padding: 3px 6px;
        }
        QPushButton:hover {
            background-color: lightYellow;
            border: 1px solid lightYellow;
        }
    """)
    execute_button.clicked.connect(main_window.execute_sql)

    # Schema button with custom style
    schema_button = QPushButton("Schema")
    schema_button.setStyleSheet("""
        QPushButton {
            font-weight: bold;
            color: black;
            background-color: lightBlue;
            border: 1px solid lightBlue;
            padding: 3px 6px;
        }
        QPushButton:hover {
            background-color: lightYellow;
            border: 1px solid lightYellow;
        }
    """)
    schema_button.clicked.connect(main_window.show_table_schema)
    
    # Align the Execute, Schema, and Save buttons
    button_bar_layout = QHBoxLayout()
    button_bar_layout.addWidget(execute_button)
    button_bar_layout.addWidget(schema_button)  # Add Schema button here
    button_bar_layout.addStretch()
    button_bar_layout.addWidget(ui.save_button)
    sql_input_layout.addLayout(button_bar_layout)
    
    # SQL input
    ui.sql_input = QTextEdit()
    ui.sql_input.setStyleSheet("border: none; border-bottom: 1px solid lightgray;")
    ui.sql_input.setAcceptRichText(True)
    ui.sql_input.setPlaceholderText("Write your SQL queries here")
    sql_input_layout.addWidget(ui.sql_input)
    
    # Information label for table name and record count
    ui.info_label = QLabel("Tablename: N/A | Total records: N/A")

    sql_input_layout.addWidget(ui.info_label)

    # Apply SQL formatter
    ui.formatter = SQLFormatter(ui.sql_input.document())
    
    # Add SQL input layout to a widget and then to the splitter
    sql_input_widget = QWidget()
    sql_input_widget.setLayout(sql_input_layout)
    content_splitter.addWidget(sql_input_widget)
    
    # Output table
    ui.output_table = QTableWidget()
    content_splitter.addWidget(ui.output_table)
    
    # Set initial sizes for the input and output fields
    content_splitter.setSizes([300, 700])
    
    return ui
