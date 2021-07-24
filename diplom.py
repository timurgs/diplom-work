import requests
import pathlib
import json
from progressbar import ProgressBar
import time


with open('token.txt', 'r') as file_object:
    file_token = file_object.read().strip()


def progress_bar(iterate):
    bar = ProgressBar(maxval=iterate)
    bar.start()
    for i in range(iterate+1):
        time.sleep(0.5)
        bar.update(i)
    bar.finish()
    return 'Выполнено успешно!'


class VkBackup:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photos(self):
        vk_id = input('Введите id своего профиля: ')
        album_id = None
        album_name = input('Из какого альбома вы хотите сохранить фото, wall или profile? ')
        if album_name == 'wall':
            album_id = 'wall'
        elif album_name == 'profile':
            album_id = 'profile'
        elif album_name == 'saved':
            album_id = 'saved'
        else:
            print('Такого альбома не существует!')
        get_photos_url = self.url + 'photos.get'
        get_photos_params = {
            'owner_id': vk_id,
            'album_id': album_id,
            'extended': '1'
        }
        response = requests.get(get_photos_url, params={**self.params, **get_photos_params})
        if response.status_code == 200:
            print('Получение файлов...')
            print(progress_bar(len(response.json()["response"]["items"])))
            print('----------------')
        else:
            print('Ошибка работы программы!')
        return response


def file_writing(res):
    with open('result.json', 'w') as file_object_2:
        data = list()
        likes_list = list()
        iterate = res['response']['items']
        for obj in iterate:
            for i in obj:
                if i == 'likes':
                    file_format = pathlib.Path(obj['sizes'][-1]['url']).suffix.split('?')[0]
                    if obj != iterate[0] and obj[i]['count'] in likes_list:
                        file_name = f'{str(obj[i]["count"])}_{str(obj["date"])}{file_format}'
                    else:
                        likes_list.append(obj[i]['count'])
                        for obj_2 in iterate:
                            if obj[i]['count'] == obj_2['likes']['count'] and obj != obj_2:
                                file_name = f'{str(obj[i]["count"])}_{str(obj["date"])}{file_format}'
                                break
                            elif obj[i]['count'] != obj_2['likes']['count'] and obj_2 == iterate[-1]:
                                file_name = str(obj[i]['count']) + file_format
                            else:
                                file_name = str(obj[i]['count']) + file_format
            size = obj['sizes'][-1]['type']
            data.append({
                "file_name": file_name,
                "size": size
            })
        json.dump(data, file_object_2, indent=1)
    with open('result.json', 'r') as file_object_3:
        file_json = json.load(file_object_3)
        if len(file_json) == len(res['response']['items']):
            print('Запись информации по файлам...')
            print(progress_bar(len(res["response"]["items"])))
        else:
            print('Ошибка работы программы!')


class YaUploader:
    ya_token = input('Введите токен с Яндекс.Диска: ')

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "OAuth {}".format(self.ya_token)
        }
        return headers

    def download_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(url=upload_url, headers=headers, params=params)
        return response.json()

    def upload(self, href):
        get_response = requests.get(self.file_path)
        put_response = requests.put(href, data=get_response.content)
        if put_response.status_code == 201:
            print('----------------')
            print('Загрузка файла...')
            return progress_bar(1)
        else:
            return 'Ошибка работы программы!'


if __name__ == '__main__':
    backup = VkBackup(file_token, '5.131')
    photos = backup.get_photos()
    file_writing(photos.json())
    iterate_2 = photos.json()['response']['items']
    j = -1
    for obj_3 in iterate_2:
        uploader = YaUploader(obj_3['sizes'][-1]['url'])
        with open('result.json', 'r') as f:
            text = json.load(f)
            j = j + 1
            result_get_link = uploader.download_link(f'vk_photos/{text[j]["file_name"]}')
            result = uploader.upload(result_get_link["href"])
            print(result)
