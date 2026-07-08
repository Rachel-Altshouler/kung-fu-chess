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
        """פונקציה שממירה פיקסלים למשבצות ומחליטה אם לבחור, להחליף או להזיז כלי"""
        col = x // 100
        row = y // 100

        # הגנה: אם הלחיצה היא מחוץ לגבולות הלוח - הקוד מתעלם
        if row < 0 or row >= len(self._grid) or col < 0 or col >= len(self._grid[0]):
            return

        clicked_piece = self._grid[row][col]

        # תרחיש א': אם עדיין לא נבחר אף כלי
        if self.selected_piece_pos is None:
            if clicked_piece != ".":
                self.selected_piece_pos = (row, col)  # בוחרים את הכלי
            else:
                return

        # תרחיש ב': אם כבר יש כלי שנבחר בלחיצה הקודמת
        else:
            prev_row, prev_col = self.selected_piece_pos
            current_selected_piece = self._grid[prev_row][prev_col]

            # בדיקה האם המשבצת החדשה אינה ריקה, והאם הצבע שלה שווה לצבע הכלי הנבחר
            if clicked_piece != "." and clicked_piece[0] == current_selected_piece[0]:
                self.selected_piece_pos = (row, col)  # החלפת בחירה
            else:
                self._execute_move(prev_row, prev_col, row, col)  # ביצוע ההזזה
                self.selected_piece_pos = None  # איפוס הבחירה

    def _execute_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """הפונקציה שהייתה חסרה! מבצעת את ההזזה הפיזית בתוך המערך"""
        piece = self._grid[from_row][from_col]  # לוקח את הכלי מהמיקום המקורי
        self._grid[to_row][to_col] = piece  # שם את הכלי במיקום החדש
        self._grid[from_row][from_col] = "."  # מרוקן את המשבצת המקורית