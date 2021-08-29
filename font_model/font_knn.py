# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from fontTools.ttLib import TTFont
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier


class Classify:
    def __init__(self):
        self.len = None
        self.knn = self.get_knn()

    @staticmethod
    def prepare_font_datas():
        data = []
        file_num_map = {
            '0e29c2287da2b8c135ab0bce6eea76152284.woff': [4, 8, 7, 9, 0, 2, 3, 5, 1, 6],
            '1b92c8081d0a83f504d67960a64978422280.woff': [6, 4, 2, 9, 0, 3, 5, 1, 7, 8],
            '1bad2346cd96c2f8ca284b81b94262882304.woff': [5, 7, 2, 0, 8, 3, 1, 6, 9, 4],
            '1ecfd52279ef3246e7880e020a19483d2276.woff': [9, 6, 8, 0, 2, 3, 7, 4, 5, 1],
            '3f58f8be2eeded068ac3716633f4147c2276.woff': [7, 3, 2, 5, 1, 4, 9, 0, 8, 6],
            '4f6c4a8c4ff7067672a013a7fe642d9e2268.woff': [0, 8, 9, 3, 1, 4, 7, 2, 6, 5],
            '04e94537e020565679353b990538d9d52292.woff': [8, 4, 7, 5, 6, 9, 1, 0, 2, 3],
            '6e2cf3597f835e6c12dd3ea09616ddbf2276.woff': [9, 2, 3, 4, 8, 1, 7, 6, 5, 0],
            '6fcab5e5aa861fe2fcbd10c345e267812268.woff': [0, 4, 1, 6, 8, 7, 2, 3, 9, 5],
            '9e9d811852ebe18ae0c2ac470502b7d12272.woff': [6, 5, 0, 4, 2, 7, 9, 1, 8, 3],
        }
        cwd = os.getcwd()
        for file, num in file_num_map.items():
            font = TTFont('{}/font_model/{}'.format(cwd, file))
            glyph_order = font.getGlyphOrder()[2:]
            for i, g in enumerate(glyph_order):
                points = font['glyf'][g].coordinates
                coors = [_ for point in points for _ in point]
                coors.insert(0, num[i])
                data.append(coors)
        return data

    @staticmethod
    def process_data(data):
        inputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        return pd.DataFrame(inputer.fit_transform(pd.DataFrame(data)))

    def get_knn(self):
        data = self.process_data(self.prepare_font_datas())

        x_train = data.drop([0], axis=1)
        y_train = data[0]

        knn = KNeighborsClassifier(n_neighbors=1)
        knn.fit(x_train, y_train)

        self.len = x_train.shape[1]

        return knn

    def knn_predict(self, data):
        df = pd.DataFrame(data)
        data = pd.concat([df, pd.DataFrame(np.zeros(
            (df.shape[0], self.len - df.shape[1])), columns=range(df.shape[1], self.len))])
        data = self.process_data(data)

        y_predict = self.knn.predict(data)
        return y_predict
