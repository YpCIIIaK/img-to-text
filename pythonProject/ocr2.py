import os
import glob
import pytesseract
from PIL import ImageGrab, Image
import g4f
from g4f.client import Client
from pynput import keyboard, mouse
import datetime
import threading
import nltk
from nltk.classify import textcat


save_folder = r"C:\Users\bigbo\OneDrive\Изображения\Screenshots"

classifier = textcat.TextCat()

timestamp = None
first_point = None
s_pressed = threading.Event()


def on_press(key):
    global timestamp, first_point, s_pressed

    try:
        if key.char == 's' and timestamp is None:
            # Получаем текущую дату и время
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print("Выберите первую точку...")

            with mouse.Listener(on_click=on_click) as mouse_listener:
                mouse_listener.join()  # ждём пока не закончится

    except AttributeError:
        pass


def on_click(x, y, button, pressed):
    global first_point, timestamp

    if pressed:
        # первый клик
        if first_point is None:
            first_point = (x, y)
            print(f"Первая точка: {first_point}")
            print("Выберите вторую точку...")
        # второй клик
        else:
            second_point = (x, y)
            print(f"Вторая точка: {second_point}")
            #  размеры прямоугольника между двумя точками
            x1, y1 = min(first_point[0], second_point[0]), min(first_point[1], second_point[1])
            x2, y2 = max(first_point[0], second_point[0]), max(first_point[1], second_point[1])

            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            # создаем имя файла
            screenshot_filename = f"screenshot_{timestamp}.png"
            # сохраняем скриншот
            screenshot_path = os.path.join(save_folder, screenshot_filename)
            screenshot.save(screenshot_path)
            print(f"Скриншот сохранен как '{screenshot_path}'")
            # сбрасываем время и координаты
            first_point = None
            timestamp = None
            s_pressed.set()


# Создаем и запускаем прослушку клавиатуры
keyboard_thread = threading.Thread(target=lambda: keyboard.Listener(on_press=on_press).start())
keyboard_thread.start()

# Ожидаем нажатия клавиши 's' перед продолжением выполнения кода ниже
s_pressed.wait()

# Получение списка скриншотов в папке
screenshot_files = glob.glob(os.path.join(save_folder, '*.png'))

# последний скриншот
if screenshot_files:
    last_screenshot = max(screenshot_files, key=os.path.getctime)
    pytesseract.pytesseract.tesseract_cmd = r'C:\flut\tesseract.exe'
    # Считывание текста с последнего скриншота
    text = pytesseract.image_to_string(Image.open(last_screenshot))
    print(text)

else:
    print("В папке нет скриншотов")

client = Client()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": text}],
)


def allinfo():
    language = classifier.guess_language(str(response)) #  язык
    with open("all.txt", "a") as file:
        file.write(language + "\n")
        file.write(str(response))
        file.write("\n")


allinfo()

print(response.choices[0].message.content)



with open("answers.txt", "w") as file:
    # Записываем текст в файл
    file.write(response.choices[0].message.content)

os.system("notepad.exe answers.txt")