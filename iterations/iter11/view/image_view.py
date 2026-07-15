class ImageView:
    def __init__(self):
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def render(self, board):
        raise NotImplementedError("Image rendering is not available in text mode")
