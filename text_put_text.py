from view.img import Img

canvas = Img().read("assets/board.png", size=(400, 400))
canvas.put_text("Score: 0", 20, 40, 1.0, color=(255, 0, 0, 255), thickness=2)
canvas.show()