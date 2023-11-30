import csv
from PIL import Image
from io import BytesIO
import requests

def resize_and_save_image(image_url, output_path, target_size=(200, 300), quality=95):
    try:
        # 이미지 URL에서 이미지를 가져옴
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # 원본 이미지 크기 확인
        original_size = image.size

        # 가로, 세로 중에서 더 긴 쪽을 기준으로 축소 비율 계산
        base_ratio = max(target_size[0] / original_size[0], target_size[1] / original_size[1])

        # 축소 비율을 적용하여 새로운 크기 계산
        new_size = (int(original_size[0] * base_ratio), int(original_size[1] * base_ratio))

        # 이미지 리사이즈
        resized_image = image.resize(new_size, resample=Image.LANCZOS)

        # 크기가 목표치를 초과하는 경우, 목표 크기로 다시 리사이즈
        resized_image = resized_image.resize(target_size, resample=Image.LANCZOS)

        # 리사이즈된 이미지를 저장
        resized_image.save(output_path, quality=quality)

        print(f"Resized and saved image to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

def index():
    # CSV 파일 읽기
    input_csv = './movie_crawl/output/movie.csv'
    output_csv = './movie_crawl/output/movie_resized.csv'
    with open(input_csv, 'r', encoding='utf-8-sig') as infile, open(output_csv, 'w', newline='', encoding='utf-8-sig') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['ResizedImg']  # 새로운 필드 추가

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # 각 행의 이미지 URL과 저장할 경로를 지정
            image_url = row['Img']
            output_path = f"./static/image_resized/{row['ID']}_resized.jpg"

            # 이미지 리사이즈 및 저장
            resize_and_save_image(image_url, output_path)

            # 새로운 필드에 리사이즈된 이미지 경로 추가
            row['ResizedImg'] = output_path

            # 새로운 행을 CSV 파일에 추가
            writer.writerow(row)

index()