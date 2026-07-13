# תיעוד הפרויקט — Kung Fu Chess

מסמך זה מסביר מה כל מחלקה עושה ומה תפקיד כל פונקציה.

---

## מבנה הפרויקט

```
model/       → נתונים (לוח, מיקום, כלי)
rules/       → חוקי משחק
engine/      → ניהול המשחק
input/       → קלט משתמש (קליקים)
game_io/     → קריאה והדפסה של קבצי קלט
main.py      → נקודת כניסה
```

---

## model/ — שכבת הנתונים

### `Position` — `model/position.py`

מייצגת מיקום על הלוח (שורה ועמודה).

| פונקציה | מה עושה |
|---------|---------|
| `__init__(row, col)` | יוצרת מיקום חדש עם שורה ועמודה |
| `as_tuple()` | מחזירה את המיקום כ-tuple: `(row, col)` |
| `__eq__(other)` | בודקת שוויון מול `Position` אחר או tuple |
| `__repr__()` | מחזירה ייצוג טקסטואלי, למשל `Position(0, 1)` |

---

### `Piece` — `model/piece.py`

מייצגת כלי שחמט (צבע + סוג).

| פונקציה | מה עושה |
|---------|---------|
| `__init__(color, piece_type)` | יוצרת כלי, למשל `color='w'`, `piece_type='K'` |
| `from_token(token)` | ממירה מחרוזת (`"wK"`) לאובייקט `Piece`. מחזירה `None` עבור `"."` |
| `to_token()` | ממירה את הכלי חזרה למחרוזת, למשל `"bQ"` |
| `is_same_color(other)` | בודקת אם שני כלים באותו צבע |

---

### `ChessBoard` — `model/board.py`

מחסן הלוח — שומר את מערך הכלים. **אין בה לוגיקת משחק.**

| פונקציה | מה עושה |
|---------|---------|
| `__init__()` | יוצרת לוח ריק |
| `set_grid(grid)` | מגדירה את מערך הלוח |
| `get_grid()` | מחזירה את מערך הלוח |
| `_to_coords(position)` | ממירה `Position` או tuple לקואורדינטות `(row, col)` |
| `is_within_bounds(row, col)` | בודקת אם הקואורדינטות בתוך גבולות הלוח |
| `get_piece_at(position)` | מחזירה את הטוקן במיקום, למשל `"wK"` או `"."` |
| `set_piece_at(position, token)` | מציבה כלי במיקום מסוים |
| `is_empty(position)` | בודקת אם המשבצת ריקה |
| `move_piece(source, destination)` | מעבירה כלי ממקור ליעד (כולל דריסת כלי ביעד = לכידה) |

---

### קבועים — `model/constants.py`

| מחלקה | מה מכילה |
|--------|----------|
| `BoardConstants` | `CELL_SIZE=100`, `EMPTY_CELL="."`, `MS_PER_SQUARE=100` |
| `Colors` | `WHITE="w"`, `BLACK="b"` |
| `PieceTypes` | `KING`, `ROOK`, `BISHOP`, `QUEEN`, `KNIGHT`, `PAWN` |
| `InputHeaders` | `BOARD_HEADER="Board:"`, `COMMANDS_HEADER="Commands:"` |
| `Commands` | `CLICK`, `WAIT`, `PRINT_BOARD` |
| `MoveResult` | קודי תוצאה אפשריים למהלך (מוגדר לשימוש עתידי) |

---

## rules/ — חוקי המשחק

### `PieceRules` — `rules/piece_rules.py`

בודקת אם תנועת כלי מסוים חוקית מבחינה גיאומטרית. כל הפונקציות הן `@staticmethod`.

| פונקציה | מה עושה |
|---------|---------|
| `is_path_blocked(grid, source, destination)` | בודקת אם יש כלי בדרך בין מקור ליעד (לא כולל היעד). משמשת R/B/Q |
| `is_king_move(source, destination)` | מלך — לכל היותר משבצת אחת בכל כיוון |
| `is_rook_move(grid, source, destination)` | צריח — תנועה ישרה + אין חסימה בדרך |
| `is_bishop_move(grid, source, destination)` | רץ — תנועה אלכסונית + אין חסימה בדרך |
| `is_queen_move(grid, source, destination)` | מלכה — ישר או אלכסון + אין חסימה בדרך |
| `is_knight_move(source, destination)` | פרש — צורת L. **לא** בודק חסימות — קופץ מעל כלים |
| `is_piece_move_valid(grid, piece_type, source, destination)` | מפנה לפונקציית הבדיקה הנכונה לפי סוג הכלי |

---

### `RuleEngine` — `rules/rule_engine.py`

ה"מוח" — מחליט אם מהלך מותר או אסור.

| פונקציה | מה עושה |
|---------|---------|
| `_to_coords(position)` | ממירה `Position` או tuple ל-`(row, col)` |
| `are_same_color(board, first, second)` | בודקת אם שני כלים במיקומים נתונים באותו צבע |
| `is_valid_move(board, source, destination)` | בודקת אם המהלך חוקי: גבולות, מקור לא ריק, לא לכידת חבר, וחוקי תנועת הכלי |

---

## engine/ — ניהול המשחק

### `GameEngine` — `engine/game_engine.py`

מחבר בין הנתונים (`Board`), החוקים (`RuleEngine`) והקלט (`Controller`).

| פונקציה | מה עושה |
|---------|---------|
| `__init__(board)` | יוצרת מנוע משחק עם לוח, שעון, ובקר |
| `get_board()` | מחזירה את הלוח |
| `get_clock()` | מחזירה את זמן השעון במילישניות |
| `get_selected_position()` | מחזירה את המיקום שנבחר כרגע (או `None`) |
| `handle_click(x, y)` | מעבירה לחיצה לבקר |
| `try_move(source, destination)` | מתחילה מהלך אם חוקי — הכלי **נכנס למצב תנועה** (הלוח מתעדכן רק בסיום) |
| `handle_wait(milliseconds)` | מוסיפה זמן לשעון ומסיימת תנועה כשהזמן מספיק |
| `is_moving()` | מחזירה `True` אם כלי נמצא באמצע תנועה |
| `_start_movement(...)` | מגדירה תנועה ממתינה ומחשבת מתי היא תסתיים |
| `_finish_movement_if_ready()` | מעדכנת את הלוח כשהשעון הגיע לזמן סיום התנועה |

**חוק חובה (שמואל):** בזמן `is_moving=True` — `handle_click` ו-`try_move` מתעלמים מפקודות חדשות.

---

## input/ — קלט משתמש

### `BoardMapper` — `input/board_mapper.py`

מתרגמת קואורדינטות פיקסלים למיקום על הלוח.

| פונקציה | מה עושה |
|---------|---------|
| `pixel_to_position(board, x, y)` | ממירה `(x, y)` בפיקסלים ל-`Position`. מחזירה `None` אם מחוץ ללוח |

---

### `Controller` — `input/controller.py`

מנהלת את בחירת הכלי ותגובה ללחיצות.

| פונקציה | מה עושה |
|---------|---------|
| `__init__()` | יוצרת בקר ללא כלי נבחר |
| `get_selected_position()` | מחזירה את המיקום הנבחר |
| `handle_click(game_engine, x, y)` | מטפלת בלחיצה: בחירת כלי / החלפת בחירה / ניסיון מהלך |

**לוגיקת לחיצה:**
1. אין כלי נבחר → לחיצה על כלי = בחירה
2. יש כלי נבחר → לחיצה על כלי ידידותי = החלפת בחירה
3. אחרת → ניסיון מהלך דרך `game_engine.try_move()`

---

## game_io/ — קלט ופלט

### `BoardParser` — `game_io/board_parser.py`

קוראת ומפרסרת את הלוח מקלט.

| פונקציה | מה עושה |
|---------|---------|
| `is_token_valid(token)` | בודקת אם טוקן תקין (`"wK"`, `"."` וכו') |
| `validate_row_widths(temp_rows)` | בודקת שכל השורות באותו רוחב |
| `parse_from_lines(lines)` | קוראת שורות, בונה `ChessBoard`, מחזירה `None` בשגיאה |

---

### `BoardPrinter` — `game_io/board_printer.py`

| פונקציה | מה עושה |
|---------|---------|
| `get_canonical_representation(board)` | מחזירה את הלוח כמחרוזת להדפסה |

---

## main.py — נקודת כניסה

| פונקציה | מה עושה |
|---------|---------|
| `process_commands(game_engine, commands)` | מריצה רשימת פקודות: `click`, `wait`, `print board` |
| `main()` | קוראת stdin → בונה לוח → יוצרת `GameEngine` → מריצה פקודות |

---

## זרימת המערכת

```
stdin
  ↓
BoardParser.parse_from_lines()  →  ChessBoard
  ↓
GameEngine(board)
  ↓
process_commands()
  ↓
click → Controller → BoardMapper → Position
                          ↓
                    RuleEngine → PieceRules
                          ↓
                    ChessBoard.move_piece()
```

---

## סיכום אחריות לפי שכבה

| שכבה | אחריות | לא אחראית על |
|------|--------|--------------|
| `model/` | שמירת נתונים | חוקים, קליקים |
| `rules/` | חוקי תנועה ולכידה | עדכון הלוח |
| `engine/` | ניהול זרימת המשחק | פירסור קלט |
| `input/` | תרגום קליקים | חוקי משחק |
| `game_io/` | קריאה והדפסה | לוגיקת משחק |
| `main.py` | חיבור הכל | — |
