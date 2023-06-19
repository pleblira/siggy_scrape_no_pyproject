import requests
import hashlib
import mimetypes

def upload_to_voidcat_and_return_url(media_file, filetype):
    print(f"Uploading {media_file}")

    content_type = mimetypes.guess_type(media_file)[0]
    headers = {
        "V-Content-Type": content_type,
        "V-Full-Digest": hashlib.sha256(open(media_file, 'rb').read()).hexdigest(),
        "V-Filename": media_file
    }

    with open(media_file, 'rb') as file:
        response = requests.post("https://void.cat/upload?cli=true", headers=headers, data=file)

    return response.text+"."+filetype