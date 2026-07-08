from validators import BoardValidator
class ChessBoard:
    def __init__(self):
        self._grid = []
        self.selected_piece_pos = None
        self.game_time_ms = 0

    def load_from_text_lines(self, lines: list) -> bool:
        reading_board = False
        temp_rows = []

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            if clean_line.startswith("Board:"):
                reading_board = True
                continue
            elif clean_line.startswith("Commands"):
                reading_board = False
                break

            if reading_board:
                tokens = clean_line.split()
                for token in tokens:
                    if not BoardValidator.is_token_valid(token):
                        print("ERROR UNKNOWN_TOKEN")
                        return False
                temp_rows.append(tokens)

        if not BoardValidator.validate_row_widths(temp_rows):
            print("ERROR ROW_WIDTH_MISMATCH")
            return False

        self._grid = temp_rows
        return True

    def get_canonical_representation(self) -> str:
        return "\n".join(" ".join(row) for row in self._grid)

    def process_commands(self, commands_lines: list):
        """פונקציה שעוברת על כל השורות ומחפשת פקודות להרצה"""
        for line in commands_lines:
            clean_line = line.strip()  # מנקה רווחים מיותרים מהקצוות של השורה
            if not clean_line:
                continue

            # עדכון חכם: אם השורה היא בדיוק "print board", נהפוך אותה למילה אחת בשביל הפיצול
            if clean_line == "print board":
                clean_line = "print_board"

            parts = clean_line.split()  # מפרק את השורה למילים לפי רווחים
            command_type = parts[0]  # המילה הראשונה ברשימה קובעת מה סוג הפקודה

            if command_type == "click":
                x = int(parts[1])
                y = int(parts[2])
                self._handle_click(x, y)

            elif command_type == "wait":
                ms = int(parts[1])
                self.game_time_ms += ms

            elif command_type == "print_board":
                print(self.get_canonical_representation())  # מפעיל את הדפסת הלוח

    def _handle_click(self, x: int, y: int):
        """ממירה פיקסלים למשבצות ומנהלת את התנועה רק אם היא חוקית"""
        col = x // 100
        row = y // 100

        # הגנה מפני לחיצה מחוץ ללוח
        if row < 0 or row >= len(self._grid) or col < 0 or col >= len(self._grid[0]):
            return

        clicked_piece = self._grid[row][col]

        # תרחיש א': אין כלי נבחר כרגע בזיכרון
        if self.selected_piece_pos is None:
            if clicked_piece != ".":
                self.selected_piece_pos = (row, col)  # בוחרים את הכלי
            return  # אם לחצו על תא ריק, פשוט עוצרים כאן

        # תרחיש ב': כבר יש כלי נבחר, ועכשיו לוחצים על יעד חדש
        prev_row, prev_col = self.selected_piece_pos
        current_selected_piece = self._grid[prev_row][prev_col]

        # 1. אם השחקן לחץ שוב על אותו הכלי בדיוק - נבטל את הבחירה
        if row == prev_row and col == prev_col:
            self.selected_piece_pos = None
            return

        # 2. אם לחצו על כלי אחר של אותו שחקן (אותה אות ראשונה 'w' או 'b') - מחליפים בחירה
        if clicked_piece != "." and clicked_piece[0] == current_selected_piece[0]:
            self.selected_piece_pos = (row, col)
            return

        # 3. אם הגענו לכאן, השחקן מנסה לבצע מהלך (לתא ריק או לאכול כלי אויב)
        # נבדוק אם המהלך חוקי מבחינת הצורה של הכלי!
        if self._is_move_legal(current_selected_piece, prev_row, prev_col, row, col):
            self._execute_move(prev_row, prev_col, row, col)

        # בכל מקרה, אחרי ניסיון תנועה (חוקי או לא) - מאפסים את הבחירה
        self.selected_piece_pos = None
    def _is_move_legal(self, piece: str, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """מחשבת מרחקים בערך מוחלט ובודקת חוקיות לפי סוג הכלי"""
        piece_type = piece[1]  # האות השנייה (K, R, B, Q, N)

        row_diff = abs(to_row - from_row)  # כמה תאים זזנו בשורות
        col_diff = abs(to_col - from_col)  # כמה תאים זזנו בעמודות

        # לחיצה על אותה משבצת בדיוק היא לא מהלך חוקי
        if row_diff == 0 and col_diff == 0:
            return False

        # 1. מלך (King) - משבצת אחת לכל כיוון
        if piece_type == "K":
            return row_diff <= 1 and col_diff <= 1

        # 2. צריח (Rook) - רק ישר (או שורות או עמודות)
        elif piece_type == "R":
            return row_diff == 0 or col_diff == 0

        # 3. רץ (Bishop) - רק באלכסונים מושלמים
        elif piece_type == "B":
            return row_diff == col_diff

        # 4. מלכה (Queen) - שילוב של צריח ורץ (ישר או אלכסון)
        elif piece_type == "Q":
            return (row_diff == 0 or col_diff == 0) or (row_diff == col_diff)

        # 5. פרש (Knight) - תנועת L (2 ו-1 או 1 ו-2)
        elif piece_type == "N":
            return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

        return False
    def _execute_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """הפונקציה שהייתה חסרה! מבצעת את ההזזה הפיזית בתוך המערך"""
        piece = self._grid[from_row][from_col]  # לוקח את הכלי מהמיקום המקורי
        self._grid[to_row][to_col] = piece  # שם את הכלי במיקום החדש
        self._grid[from_row][from_col] = "."  # מרוקן את המשבצת המקורית