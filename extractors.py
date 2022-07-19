import requests
import subprocess

import logger as log


def extractor_url(url: str) -> str or None:
    """Из ссылки на пост с видео, делает прямую ссылку на скачивание видео."""
    video_part_url = url.split('video')[1]
    video_id = video_part_url.split('?list=')[0]
    if 'list' in video_part_url:
        list_id = video_part_url.split('?list=')[1]
    else:
        list_id = ''
    
    headers = {
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
    try:
        response = requests.post('https://vk.com/al_video.php', params=params, headers=headers, data=data)
        payload_1 = response.json()['payload'][1]
        
        if 'video_yt_player' in payload_1[1]:
            url_video = payload_1[1].split('src="')[1].split('"')[0]
        
        json_answer = payload_1[3]['player']['params'][0]
        
        direct_mp4 = json_answer.get('direct_mp4')
        url144 = json_answer.get('url144')
        url240 = json_answer.get('url240')
        url360 = json_answer.get('url360')
        url480 = json_answer.get('url480')
        url720 = json_answer.get('url720')
        url1080 = json_answer.get('url1080')
        
        if direct_mp4: url_video = direct_mp4
        if url144: url_video = url144
        if url240: url_video = url240
        if url360: url_video = url360
        if url480: url_video = url480
        if url720: url_video = url720
        if url1080: url_video = url1080
        
        return url_video
    except Exception as err:
        log.log(str(response.text))
        log.error(str(err))
        return None


def extractor_info(path) -> dict:
    """Извлекает длительность, ширину, высоту видео."""
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1', path],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result2 = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                              'stream=height,width', '-of', 'csv=s=x:p=0', path], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    
    duration = int(float(result.stdout))
    width, height = str(result2.stdout).split("b'")[1].split("\\r")[0].split('x')
    return {'duration': duration, 'width': width, 'height': height}
