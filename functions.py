import os        
import threading   
from time import sleep 
import queue

from bs4 import BeautifulSoup         
import requests         
import lxml
#from tkinter import Image
from PIL import Image, ImageChops

headers = {"User-Agent":"Mozilla/5.0"}


def make_dir(directory_name):                                                   
    if not os.path.isdir('dataset'):      
        os.mkdir('dataset')               
    if not os.path.exists(os.path.join('dataset', directory_name)):   
        os.mkdir(os.path.join('dataset', directory_name))


def get_image_url(request_name):
    for page_number in range(1, 35):
        print(page_number, " page")
        request_name.replace(' ', '%20')  
        url = f'https://yandex.ru/images/search?text={request_name}&p={page_number}'
        responce = requests.get(url, headers=headers).text       
        #sleep(2)
        soup = BeautifulSoup(responce, 'lxml')                   
        image_block = soup.find_all('img', class_='serp-item__thumb justifier__thumb')
        for image in image_block:
            image_url = 'https:' + image.get('src')
            print(image_url)
            yield (image_url)                   #Возврат из функции лок. пер. 


def download_image(image_url, image_name, folder_name):
    response = requests.get(image_url, headers=headers).content

    file_name = open(os.path.join('dataset', folder_name, f"{image_name}.jpg"), 'wb')
    with file_name as handler:
        handler.write(response)


class diff_image(threading.Thread):  # класс по сравнению картинок.
   #Потоковый обработчик

    def __init__(self, queue):
        #Инициализация потока
        threading.Thread.__init__(self)
        self.queue = queue


    def run(self):
        #Запуск потока
        while True:
            # Получаем пару путей из очереди
            files = self.queue.get()
            # Делим и сравниваем
            self.difference_images(files.split(':')[0], files.split(':')[1])
            # Отправляем сигнал о том, что задача завершена
            self.queue.task_done()


    def difference_images(self, img1, img2, path):
        image_1 = Image.open(img1)
        image_2 = Image.open(img2)

        size = [400, 300]  # размер в пикселях
        image_1.thumbnail(size)  # уменьшаем первое изображение
        image_2.thumbnail(size)  # уменьшаем второе изображение

        result = ImageChops.difference(image_1, image_2).getbbox()
        if result is None:
            print(img1, img2, 'matches')
            os.remove(path, img2)
        return


def main_remove(path):
    imgs = os.listdir(path)  # Получаем список картинок
    q = queue.Queue()

    # Запускаем поток и очередь
    for i in range(4):  # 4 - кол-во одновременных потоков
        t = diff_image(q)

        t.start()

        # Даем очереди нужные пары файлов для проверки
    check_file = 0
    current_file = 0

    while check_file < len(imgs):
        if current_file == check_file:
            current_file += 1
            continue
        q.put(path + imgs[current_file] + ':' + path + imgs[check_file])
        current_file += 1
        if current_file == len(imgs):
            check_file += 1
            current_file = check_file

            # Ждем завершения работы очереди
    q.join()


def run(animal_name):
    count = 0
    make_dir(animal_name)
    for url in get_image_url(animal_name):
        download_image(url, str(count).zfill(4), animal_name)
        count += 1
        sleep(2)
        print(count, ' downloaded') 