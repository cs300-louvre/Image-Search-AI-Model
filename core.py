from typing import Union
import os
import re
import torch
import clip
from PIL import Image
from tqdm import tqdm
import pandas as pd


def normalize_text(text):
    ''' Normalize text '''
    text = text.lower()
    text = re.sub(r"([?.!,¿])", r" \1 ", text)
    text = re.sub(r'[" "]+', " ", text)
    text = re.sub(r"[^a-zA-Z?.!,¿]+", " ", text)
    text = text.strip()
    return text


class SearchEngine:
    ''' Search image with text or image '''

    def __init__(self,
                 model_path: str,
                 image_dir: str = 'images',
                 embed_dir: str = "embedding",
                 device: str = 'cuda'):
        '''
        Args:
            model_path: path to model
            image_dir: path to image directory
            embed_dir: path to embedding directory
            device: device to use
        '''
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.image_dir = image_dir
        self.embed_dir = embed_dir
        self.model, self.preprocess = clip.load(model_path, device=device)
        self.model.eval()
        self.model.to(device)

        # accepted image types
        self.accepted_image_types = ['jpg', 'jpeg', 'png']
        # list of image name
        self.image_name = os.listdir(self.image_dir)
        self.image_name = [image_name for image_name in self.image_name 
                    if image_name.split('.')[-1] in self.accepted_image_types]
        # embed image
        self.embed_image()
        # load embedding
        self.image_features = self.load_embedding()


    def embed_image(self):
        ''' embeding image\n
        embedding/<image_name>.pt for each image
        '''
        if not os.path.exists(self.embed_dir):
            os.mkdir(self.embed_dir)
        for image_name in tqdm(self.image_name, desc="Embedding image"):
            if not os.path.exists(os.path.join(self.embed_dir, image_name.split('.')[0] + '.pt')):
                image = self.preprocess(Image.open(os.path.join(
                    self.image_dir, image_name))).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    image_features = self.model.encode_image(image)
                torch.save(image_features, os.path.join(
                    self.embed_dir, image_name.split('.')[0] + '.pt'))

    def load_embedding(self):
        ''' load embedding '''
        image_features = []
        for image_name in tqdm(os.listdir(self.embed_dir), desc="Loading embedding"):
            image_features.append(torch.load(
                os.path.join(self.embed_dir, image_name)))
        image_features = torch.cat(image_features, dim=0)
        return image_features

    @torch.no_grad()
    def search_text(self, text: str, top_k: int = 5):
        ''' search image with text \n
        Args:
            text: text to search
            top_k: number of image to return
        '''
        text = normalize_text(text)
        text = clip.tokenize([text]).to(self.device)
        query_features = self.model.encode_text(text)
        image_features = self.image_features
        similarity = (100.0 * image_features @ query_features.T)
        values, indices = similarity.topk(top_k, dim=0)
        # load image name
        result = []
        for value, index in zip(values, indices):
            result.append(
                {'image_name': self.image_name[index], 'similarity': value.item()})
        return result

    @torch.no_grad()
    def search_image(self, image: Union[str, Image.Image], top_k: int = 5):
        '''
        search image with image \n
        Args:
            image: image to search (path or PIL image)
            top_k: number of image to return
        '''
        if isinstance(image, str):
            image = Image.open(image)
        elif isinstance(image, Image.Image):
            image = image
        else:
            raise TypeError('image must be str or PIL.Image.Image')

        image = self.preprocess(image).unsqueeze(0).to(self.device)
        query_features = self.model.encode_image(image)
        image_features = self.image_features
        similarity = (100.0 * image_features @ query_features.T)
        values, indices = similarity.topk(top_k, dim=0)
        # load image name
        df = pd.read_csv('image_name.csv')
        image_name = df['image_name'].values
        result = []
        for value, index in zip(values, indices):
            result.append(
                {'image_name': image_name[index], 'similarity': value.item()})
        return result
