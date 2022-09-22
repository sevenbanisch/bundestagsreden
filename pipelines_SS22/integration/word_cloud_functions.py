from typing import List

import numpy as np
from wordcloud import WordCloud
from PIL import Image


def topics_to_word_clouds(topics: List[List[str]]) -> List[WordCloud]:
    mask = np.array(Image.open('imgs/circle.png'))
    wcs = []

    for i, words in enumerate(topics):
        wordcloud = WordCloud(
            background_color='white',
            max_words=50,
            mask=mask,
            contour_color='#000000',
            contour_width=3,
            colormap='rainbow')\
            .generate(' '.join(words))

        wordcloud.to_file(f'imgs/wordclouds/wordcloud_{i}.png')

        wcs.append(wordcloud)

    return wcs
