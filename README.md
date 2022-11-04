# 😼 Search Images API

## Introduction

This is a simple API that allows you to search for images using image or text.

## Requirements

- Python 3.6+
- Docker (optional)

## Setup API

1. Clone the repository

```bash
git clone <repo>.git
```

2. Create a virtual environment

```bash
python3 -m venv venv
```

3. Install the requirements

```bash
pip install -r requirements.txt
```

4. Run the API

```bash
python app.py --host 0.0.0.0 --port 80
```

## Usage

### Prepare data

- [images folder](images) stores the images for search.

- image types are supported: `jpg`, `jpeg`, `png`

### Search by image

```bash
curl -X POST -H 'Content-Type:application/json' -d '{"image": <base64>}' http://localhost:80/search
```

base64: Base64 encoded image

for example:

```bash
curl -X POST -H 'Content-Type:application/json' -d '{"image": "/9j/4AAQSkZJRgAB..."}' http://localhost:80/search
curl -X POST -H 'Content-Type:application/json' -d '{"image": "data:image/png;base64,/9j/4AAQSkZJRgAB..."}' http://localhost:80/search
```

### Search by text

```bash
curl -X POST -H 'Content-Type:application/json' -d '{"search_text":"a cat"}' 192.168.1.144:80/api
```

### Web UI

This is a simple web UI that allows you to search for images using image or text.

![Image](res\webUI.png)

The results are displayed.

![Image](res\webUI_results.png)

## Docker

### Build

```bash
docker build -t image-search-api .
```

### Run

```bash
docker run -p 80:80 image-search-api
```
