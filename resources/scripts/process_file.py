#! /usr/bin/env python3
# coding: utf-8

"""
WHAT THIS SCRIPT DOES
---------------------
1. This script transforms a audio file (wav or mp3) for the radioamnion
2. All transformations are stored in the a directory along the file with the same name as the file
3. The transformations are:
    - a .csv file with the light pattern for the deployed modules
    - a bunch of plots, each stored in different formats .png, .pdf and .html
2. it saves the metadata from the ONC server for all files under:
"""
import argparse
import os

import numpy as np
import plotly.graph_objects as go
import scipy.fft
import scipy.io.wavfile
import scipy.signal

import radioamnion


def parser_args():
    parser = argparse.ArgumentParser(description='Transforms a audio file (wav or mp3) for the radioamnion')
    parser.add_argument('file', metavar='FILE', type=str, nargs='*', default=[],
                        help="Path to the audio file")

    return parser.parse_args()


def create_plots(audio_led, ):
    """Creates the plots. Its a bit ugly and should be rewritten."""

    # Create the colorscale for plotly
    c_name = ['Viridis_r', 'Viridis', 'Blues', 'Speed', 'Speed_r', 'Tempo', 'Tempo_r', 'Deep', 'Deep_r'][-2]
    color_mod = radioamnion.Colorscale(c_name)
    # color_mod.fade_alpha()  # to add alpha
    # color_mod.add_color_below((0,0,0,0))  # to add a color for the lower limit

    # the fourier transformation
    fourier_visualizer = radioamnion.FourierSpaceVisualizer()
    xx, yy, zz = fourier_visualizer.create_2d_arrays(led_converter=audio_led,
                                                     log=True,
                                                     t_steps=1,
                                                     f_steps=1)

    # get it smoother
    steps_x, steps_y = 30, 10  # shape convolution core
    core = np.ones((steps_x, steps_y))  # core is all 1., rectangle signal
    core /= np.sum(core)

    zz_conv = scipy.signal.convolve2d(zz, core, mode='valid')
    x_conv = np.convolve(xx[0, :] / 1e3, np.ones(steps_y) / steps_y, mode='valid')
    y_conv = np.convolve(yy[:, 0], np.ones(steps_y) / steps_y, mode='valid')
    y_conv = (y_conv * 1000.).astype('datetime64[ms]')

    # TODO: why the following lines
    i = 50
    width = 16 * i
    height = 9 * i

    # Create the first plot
    print('Create first Plot')
    steps_x, steps_y = 30, 10
    fig = go.Figure(layout_width=width,
                    layout_height=height,
                    data=[go.Surface(z=zz_conv[steps_x // 4::steps_x // 2, steps_y // 4::steps_y // 2],
                                     x=x_conv[steps_y // 4::steps_y // 2],
                                     y=y_conv[steps_x // 4::steps_x // 2],
                                     showscale=False,
                                     colorscale=color_mod.colorscale,
                                     yhoverformat="%H:%M:%S.%L",
                                     hovertemplate='Time: %{y}<br>'
                                                   'Frequency: %{x:.2f} kHz<br>'
                                     # 'Amplitude: %{z:.2f}'
                                                   '<extra></extra>',
                                     )])

    axis_dict = dict(showticklabels=False,
                     showgrid=False,
                     title='',
                     backgroundcolor="rgba(0,0,0,0)",
                     zerolinecolor="rgba(0,0,0,0)",
                     )

    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.75, y=0, z=1)
    )

    fig.update_layout(scene=dict(xaxis=axis_dict, yaxis=axis_dict, zaxis=axis_dict),
                      scene_camera=camera,
                      scene_aspectmode='manual',
                      scene_aspectratio=dict(x=1, y=2.5, z=1),
                      template="plotly_white",
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=0, b=0, t=0, pad=0),
                      )

    file_name = os.path.basename(audio_led.file_name).rsplit(".", 1)[0]
    file_dir = os.path.join(os.path.dirname(audio_led.file_name), file_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_name_plot = os.path.join(file_dir, f'{file_name}-3d-{color_mod.cscale.lower()}')

    fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1),
                                        center=dict(x=0, y=0, z=0),
                                        eye=dict(x=3.1, y=0, z=1)),
                      )
    fig.write_image(f'{file_name_plot}.pdf', format='pdf', scale=10)
    fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1),
                                        center=dict(x=0, y=0, z=0),
                                        eye=dict(x=3.1, y=0, z=1))
                      )
    fig.write_image(f'{file_name_plot}.png', format='png', scale=10)

    fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1),
                                        center=dict(x=0, y=0, z=0),
                                        eye=dict(x=2., y=0, z=1)),
                      width=None,
                      height=None,
                      )

    fig.write_html(f'{file_name_plot}.html',
                   auto_play=False,
                   config={'displaylogo': False},
                   include_plotlyjs='cdn', include_mathjax='cdn',
                   )

    # fig.show(config={'displaylogo': False})

    # Create the second plot
    print('Create second Plot')
    color_mod = radioamnion.Colorscale(
        ['Viridis', 'Blues', 'Speed', 'Speed_r', 'Tempo', 'Tempo_r', 'Deep', 'Deep_r'][-1])
    n_colors = 15
    zz_plot = zz_conv[steps_x // 4::steps_x // 2, steps_y // 4::steps_y // 2].T

    fig = go.Figure(layout_width=width,
                    layout_height=height,
                    data=[go.Contour(x=y_conv[steps_x // 4::steps_x // 2],
                                     y=x_conv[steps_y // 4::steps_y // 2],
                                     z=zz_plot,

                                     # line_smoothing=0.85,
                                     colorscale=color_mod.colorscale,
                                     showscale=False,
                                     contours=dict(start=zz_plot.min(), end=zz_plot.max(),
                                                   size=(zz_plot.max() - zz_plot.min()) / n_colors),
                                     xhoverformat="%H:%M:%S.%L",
                                     hovertemplate='Time: %{x}<br>'
                                                   'Frequency: %{y:.2f} kHz<br>'
                                                   '<extra></extra>',
                                     # contours_coloring='heatmap',
                                     contours_showlines=False,
                                     line_width=0,
                                     ),
                          ])

    axis_dict = dict(showticklabels=False,
                     showgrid=False,
                     title='',
                     linecolor="rgba(0,0,0,0)",
                     backgroundcolor="rgba(0,0,0,0)",
                     gridcolor="rgba(0,0,0,0)",
                     zerolinecolor="rgba(0,0,0,0)",
                     gridwidth=0,
                     linewidth=0,
                     )
    fig.update_layout(xaxis=dict(showticklabels=False),
                      yaxis=dict(showticklabels=False),
                      scene=dict(xaxis=axis_dict, yaxis=axis_dict, zaxis=axis_dict),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=0, b=0, t=0, pad=0),
                      )

    file_name = os.path.basename(audio_led.file_name).rsplit(".", 1)[0]
    file_dir = os.path.join(os.path.dirname(audio_led.file_name), file_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_name_plot = os.path.join(file_dir, f'{file_name}-2d-{color_mod.cscale.lower()}')

    fig.write_image(f'{file_name_plot}.pdf', format='pdf', scale=10)
    fig.write_image(f'{file_name_plot}.png', format='png', scale=10)

    fig.update_layout(width=None, height=None, )
    fig.write_html(f'{file_name_plot}.html', auto_play=False,
                   include_plotlyjs='cdn', include_mathjax='cdn')

    # Create the last plot
    print('Create last Plot')
    # make figure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    updatemenus = [{"buttons": [{"args": [None,
                                          {"frame": {"duration": 2000,
                                                     "redraw": False},
                                           "fromcurrent": True,
                                           "transition": {"duration": 300,
                                                          "easing": "quadratic-in-out"}}],
                                 "label": "Play",
                                 "method": "animate"
                                 },
                                {"args": [[None], {"frame": {"duration": 0, "redraw": False},
                                                   "mode": "immediate",
                                                   "transition": {"duration": 0}}],
                                 "label": "Pause",
                                 "method": "animate"
                                 }
                                ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                    }
                   ]
    # fig_dict["layout"]["updatemenus"] = updatemenus

    sliders_dict = {"active": 0,
                    "yanchor": "top",
                    "xanchor": "left",
                    "currentvalue": {
                        # "font": {"size": 20},
                        "visible": True,
                        "xanchor": "right"
                    },
                    "transition": {"duration": 300, "easing": "cubic-in-out"},
                    "pad": {"b": 10, "t": 50},
                    "len": .9,
                    "x": 0.05,
                    "y": 0,
                    "steps": []
                    }

    data = go.Contour(x=y_conv[steps_x // 4::steps_x // 2],
                      y=x_conv[steps_y // 4::steps_y // 2],
                      z=zz_plot,

                      # line_smoothing=0.85,
                      colorscale=color_mod.colorscale,
                      showscale=False,
                      contours=dict(start=zz_plot.min(), end=zz_plot.max(),
                                    size=(zz_plot.max() - zz_plot.min()) / n_colors),
                      xhoverformat="%H:%M:%S.%L",
                      hovertemplate='Time: %{x}<br>'
                                    'Frequency: %{y:.2f} kHz<br>'
                                    '<extra></extra>',
                      # contours_coloring='heatmap',
                      contours_showlines=False,
                      line_width=0,
                      )
    fig_dict["data"].append(data)

    # make frames
    for color in ['Viridis', 'Viridis_r', 'Cividis', 'Cividis_r', 'Blues', 'Blues_r', 'Speed', 'Speed_r',
                  'Tempo', 'Tempo_r', 'Deep', 'Deep_r', 'Magma', 'Magma_r', 'Portland', 'Portland_r']:
        # data_i = copy.copy(data)
        # data_i.colorscale = color
        data_i = go.Contour(colorscale=color)
        frame = {"data": [data_i], "name": str(color)}
        fig_dict["frames"].append(frame)
        slider_step = {"args": [[color],
                                {"frame": {"duration": 300, "redraw": True},
                                 "mode": "immediate",
                                 "transition": {"duration": 300}}
                                ],
                       "label": color,
                       "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)

    axis_dict = dict(showticklabels=False,
                     showgrid=False,
                     title='',
                     linecolor="rgba(0,0,0,0)",
                     backgroundcolor="rgba(0,0,0,0)",
                     gridcolor="rgba(0,0,0,0)",
                     zerolinecolor="rgba(0,0,0,0)",
                     gridwidth=0,
                     linewidth=0,
                     )
    fig.update_layout(xaxis=dict(showticklabels=False),
                      yaxis=dict(showticklabels=False),
                      scene=dict(xaxis=axis_dict, yaxis=axis_dict, zaxis=axis_dict),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=0, b=0, t=0, pad=0),
                      )

    fig.write_html(f'{file_name_plot}_multi.html', auto_play=False,
                   include_plotlyjs='cdn', include_mathjax='cdn')


def main(file_name):
    audio_led = radioamnion.Audio2LED(file_name)
    print(f'Resulting fps: {audio_led.fps:.2f} frames/s')
    audio_led.save_to_csv()

    print('Create Plots')
    create_plots(audio_led)


# execute only if run as a script
if __name__ == "__main__":
    args = parser_args()

    if args.file == []:
        print('No file defined.')
    else:
        for i in args.file:
            print(f'Process: {i}')
            main(file_name=i)
        print(f'Done')
