# Helper Classes to create color-scales for plotly
import plotly.express as px
import numpy as np


class ColorscaleModifier:
    @staticmethod
    def colorscale_to_array(cscale: str):
        colorscale = px.colors.get_colorscale(cscale)

        colorscale_arr = np.zeros((len(colorscale), 5))  # [[value, red, green, blue, alpha]]
        for i, color_i in enumerate(colorscale):
            if isinstance(color_i[1], str) and color_i[1].startswith('#'):
                colorscale_arr[i] = np.array([color_i[0], *px.colors.hex_to_rgb(color_i[1]), 1.])

            elif isinstance(color_i[1], str) and color_i[1].startswith('rgb('):
                colorscale_arr[i] = np.array([color_i[0],
                                              *ColorscaleModifier.rgb_to_tuple(color_i[1]),
                                              1.])

            elif isinstance(color_i[1], str) and color_i[1].startswith('rgba('):
                colorscale_arr[i] = np.array([color_i[0],
                                              *ColorscaleModifier.rgba_to_tuple(color_i[1])])

            elif isinstance(color_i[1], tuple):
                colorscale_arr[i] = np.array([color_i[0], *color_i[1], 1.])

        return colorscale_arr

    @staticmethod
    def array_to_colorscale(colorscale_arr):
        return [[i[0], f'rgba({i[1]:.0f},{i[2]:.0f},{i[3]:.0f},{i[4]})'] for i in colorscale_arr]

    @staticmethod
    def rgb_to_tuple(rgb):
        rgb = rgb.replace('rgb(', '').replace(')', '')
        return tuple(map(int, rgb.split(',')))

    @staticmethod
    def rgba_to_tuple(rgb):
        rgb = rgb.replace('rgba(', '').replace(')', '')
        return tuple(map(int, rgb.split(',')))

    @staticmethod
    def add_color_below(colorscale_arr, color_rgba):
        colorscale_arr[0, 0] += 1e-2  # lower values seems to not work if the len(colorscale) is too big
        return np.append([[0.0, *color_rgba]], colorscale_arr, axis=0)

    @staticmethod
    def add_color_above(colorscale_arr, color_rgba):
        colorscale_arr[-1, 0] -= 1e-2  # lower values seems to not work if the len(colorscale) is too big
        return np.append(colorscale_arr, [[1.0, *color_rgba]], axis=0)

    @staticmethod
    def fade_alpha(colorscale_arr, inverse=False, alpha_start=0., alpha_stop=1.):
        if inverse:
            alpha_start, alpha_stop = alpha_stop, alpha_start
        colorscale_arr[:, -1] = np.linspace(alpha_start, alpha_stop, colorscale_arr.shape[0])
        return colorscale_arr

    @staticmethod
    def interp(colorscale_arr, n=10):
        x = np.linspace(0, 1, n)
        colorscale_arr = np.array([x,
                                   np.interp(x, colorscale_arr[:, 0], colorscale_arr[:, 1]),
                                   np.interp(x, colorscale_arr[:, 0], colorscale_arr[:, 2]),
                                   np.interp(x, colorscale_arr[:, 0], colorscale_arr[:, 3]),
                                   np.interp(x, colorscale_arr[:, 0], colorscale_arr[:, 4]),
                                   ]).T
        return colorscale_arr


class Colorscale(ColorscaleModifier):
    def __init__(self, cscale=None):
        if cscale is None:
            self.cscale = None
            self.colorscale_arr = None
        else:
            self.cscale = cscale
            self.colorscale_arr = self.colorscale_to_array(cscale)

    @property
    def colorscale(self, ):
        return self.array_to_colorscale(self.colorscale_arr)

    def add_color_below(self, color_rgba):
        self.colorscale_arr = ColorscaleModifier.add_color_below(self.colorscale_arr, color_rgba)
        return self

    def add_color_above(self, color_rgba):
        self.colorscale_arr = ColorscaleModifier.add_color_above(self.colorscale_arr, color_rgba)
        return self

    def fade_alpha(self, inverse=False, alpha_start=0., alpha_stop=1.):
        self.colorscale_arr = ColorscaleModifier.fade_alpha(self.colorscale_arr,
                                                            inverse=inverse,
                                                            alpha_start=alpha_start, alpha_stop=alpha_stop)
        return self

    def interp(self, n=10):
        self.colorscale_arr = ColorscaleModifier.interp(self.colorscale_arr, n=n)
        return self
