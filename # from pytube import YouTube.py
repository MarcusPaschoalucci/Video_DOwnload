# from pytube import YouTube
import youtube_dl
import string
import random


# def generate_random_string(length):
#     letters = string.ascii_lowercase
#     return ''.join(random.choice(letters) for _ in range(length))

def download_youtube_video(page_url, output_path):
    ydl_opts = {
        # 'outtmpl': output_path + '/Clipe-%(id)s'+ generate_random_string(8) +'-sabao.%(ext)s',
        'outtmpl': output_path + '/Clipe-%(id)s-sabao.%(ext)s',
        'ignoreerrors': True,
        'no_warnings': True
    }

    video_info_list = []

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(page_url, download=False)

        for entry in playlist_info['entries']:
            url = entry['webpage_url']
            title = entry['title'] 
            duration = entry['duration']
            ydl.download([url])
            video_info = {'title': title, 'duration': duration}
            video_info_list.append(video_info)
            # print(f"Testing Video '{title}' downloaded successfully! Duration: {duration} seconds.")

    return video_info_list


# Example usage
# video_url = "https://www.youtube.com/@ASMRSOAP/shorts" ##lots of midias  # Replace with the desired YouTube video URL
video_url = "https://www.youtube.com/watch?v=8XBpZAetcb8"
output_directory = "C:\\Users\\marcu\\OneDrive\\Documents\\GitHub\\Video_DOwnload\\BAIXADOS"  # Replace with the desired output directory

video_info = download_youtube_video(video_url, output_directory)
print('TESTE DE PRINT', video_info)

for video in video_info:
    print(f"Print final - Video: {video['title']}, Duration: {video['duration']} seconds.")