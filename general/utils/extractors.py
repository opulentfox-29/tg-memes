import requests


def extractor_url(url: str) -> tuple[str, str, str, str] or tuple[str, str, None, None]:
    """Из ссылки на пост с видео, делает прямую ссылку на скачивание видео."""
    video_part_url = url.split('video')[1]
    video_id = video_part_url.split('?list=')[0]
    if 'list' in video_part_url:
        list_id = video_part_url.split('?list=')[1]
    else:
        list_id = ''
    
    headers = {
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    params = {
        'act': 'video_box',
    }
    
    data = {
        'al': '1',
        'list': list_id,
        'video': video_id,
    }

    response = requests.post('https://vk.com/al_video.php', params=params, headers=headers, data=data)
    payload_1 = response.json()['payload'][1]

    if payload_1[3]['player']['type'] == 'youtube':
        url_video = payload_1[1].split('src="')[1].split('"')[0]
        duration = payload_1[3]['mvData']['duration']
        return url_video, duration, None, None

    json_answer = payload_1[3]['player']['params'][0]

    qualities = ('url1080', 'url720', 'url480', 'url360', 'url240', 'url144', 'direct_mp4')

    url_video = tuple(filter(bool, map(lambda x: json_answer.get(x), qualities)))[0]

    manifest = json_answer.get('manifest')
    if manifest:
        width = manifest.split('width="')[-1].split('"')[0]
        height = manifest.split('height="')[-1].split('"')[0]
    else:
        width = height = 0
    duration = json_answer.get('duration')

    return url_video, duration, width, height
