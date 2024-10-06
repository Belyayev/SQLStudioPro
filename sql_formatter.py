import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor
from PySide6.QtCore import QRegularExpression

class SQLFormatter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("blue"))
        self.keyword_format.setFontWeight(QFont.Bold)
        self.keywords = [
            "select", "update", "from", "where", "insert", "delete", "create", "drop", "table", "alter", "in",
            "order by", "group by", "having", "insert into", "alter", "truncate", "create index", "drop index",
            "join", "union", "exists", "between", "like", "is null", "distinct", "left join", "inner join", "merge"
        ]

        self.highlighting_rules = []
        for keyword in self.keywords:
            pattern = QRegularExpression(r'\b' + re.escape(keyword) + r'\b', QRegularExpression.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, self.keyword_format))

        # SQL strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("darkGreen"))
        self.highlighting_rules.append((QRegularExpression("\".*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'.*\'"), string_format))

        # SQL comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("darkGray"))
        self.highlighting_rules.append((QRegularExpression("--[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

    def capitalize_sql_commands(self, text):
        pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in self.keywords) + r')\b'
        return re.sub(pattern, lambda match: match.group(0).upper(), text, flags=re.IGNORECASE)

    def format_text(self, text_edit):
        cursor = text_edit.textCursor()
        cursor_position = cursor.position()

        text = text_edit.toPlainText()
        formatted_text = self.capitalize_sql_commands(text)

        # Only update the text if it has changed
        if text != formatted_text:
            text_edit.blockSignals(True)
            text_edit.setPlainText(formatted_text)
            cursor.setPosition(cursor_position)
            text_edit.setTextCursor(cursor)
            text_edit.blockSignals(False)
