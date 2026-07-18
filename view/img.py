from __future__ import annotations

import pathlib

import cv2
import numpy as np

class Img:
    WHITE_BG_THRESHOLD = 250
    BLACK_BG_THRESHOLD = 35

    def __init__(self):
        self.img = None

    def read(
        self,
        path: str | pathlib.Path,
        size: tuple[int, int] | None = None,
        keep_aspect: bool = False,
        interpolation: int = cv2.INTER_AREA,
        remove_white_bg: bool = False,
        remove_black_bg: bool = False,
    ) -> "Img":
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if remove_white_bg:
            self._remove_white_background()
        elif remove_black_bg:
            self._remove_black_background()

        if size is not None:
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self

    def _remove_white_background(self):
        if self.img.ndim != 3:
            return

        if self.img.shape[2] == 4:
            bgra = self.img
        else:
            bgra = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)

        blue, green, red, alpha = cv2.split(bgra)
        white = (
            (blue >= self.WHITE_BG_THRESHOLD)
            & (green >= self.WHITE_BG_THRESHOLD)
            & (red >= self.WHITE_BG_THRESHOLD)
        )
        alpha = np.where(white, 0, 255).astype(np.uint8)
        self.img = cv2.merge([blue, green, red, alpha])

    def _remove_black_background(self):
        if self.img.ndim != 3:
            return

        if self.img.shape[2] == 4:
            bgra = self.img
        else:
            bgra = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)

        blue, green, red, alpha = cv2.split(bgra)
        black = (
            (blue <= self.BLACK_BG_THRESHOLD)
            & (green <= self.BLACK_BG_THRESHOLD)
            & (red <= self.BLACK_BG_THRESHOLD)
        )
        alpha = np.where(black, 0, 255).astype(np.uint8)
        self.img = cv2.merge([blue, green, red, alpha])

    def draw_on(self, other_img, x, y):
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W or x < 0 or y < 0:
            raise ValueError("Logo does not fit at the specified position.")

        if self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
            roi = other_img.img[y:y + h, x:x + w]
            alpha = self.img[:, :, 3:4].astype(np.float32) / 255.0
            roi[:] = (
                (1.0 - alpha) * roi + alpha * self.img[:, :, :3]
            ).astype(np.uint8)
            return

        if self.img.shape[2] != other_img.img.shape[2]:
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        roi = other_img.img[y:y + h, x:x + w]

        if self.img.shape[2] == 4:
            b, g, r, a = cv2.split(self.img)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:
            other_img.img[y:y + h, x:x + w] = self.img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(
            self.img,
            txt,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            color,
            thickness,
            cv2.LINE_AA,
        )

    def show_loop(self, window_name="Image", delay_ms=30):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow(window_name, self.img)
        return cv2.waitKey(delay_ms) & 0xFF

    def close_window(self, window_name="Image"):
        cv2.destroyWindow(window_name)
        cv2.waitKey(1)

    def show(self):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()