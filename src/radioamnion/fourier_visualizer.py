import os
import sys

import matplotlib
import matplotlib.animation
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import tqdm
from matplotlib.colors import ListedColormap


class FourierSpaceVisualizer:
    def __init__(self, ):
        self.fig, self.ax, self.figure_dict = None, None, None

    @staticmethod
    def set_up_3d_fig(facecolor):
        figure_dict = {'facecolor': facecolor}  # 'black'}
        fig = plt.figure(figsize=(10, 10), **figure_dict)
        ax = fig.gca(projection='3d', **figure_dict)
        ax.set_axis_off()

        return fig, ax, figure_dict

    def plot_3d(self, led_converter, log=True, t_steps=23, f_steps=30, cmap='viridis', facecolor='white', n_trans=0):
        ff, tt = np.meshgrid(led_converter.frequency_arr[::f_steps],
                             np.average(led_converter.time_chunked, axis=-1)[::t_steps])
        zz = np.copy(led_converter.f_data[0, ::t_steps, ::f_steps])
        if log:
            zz = np.log10(zz)

        fig, ax, figure_dict = self.set_up_3d_fig(facecolor)
        self.fig, self.ax, self.figure_dict = fig, ax, figure_dict

        # norm for cmap, log for lin and lin for log
        ZZ = np.abs(zz.flatten())

        cmap_cmap = matplotlib.cm.get_cmap(cmap)
        my_cmap = np.array(cmap_cmap(np.arange(cmap_cmap.N)))
        fade_n = n_trans
        my_cmap[:fade_n, -1] *= np.linspace(0, 1, fade_n)

        # Create new colormap
        my_cmap = ListedColormap(my_cmap)

        if log:
            norm = None
        else:
            norm = colors.LogNorm(vmin=ZZ.min() * 1000, vmax=ZZ.max() * 1.)

        ax.plot_trisurf(ff.flatten() / 1e3,
                        tt.flatten(),
                        ZZ,
                        shade=True,
                        linewidth=0.0001,
                        antialiased=True,
                        norm=norm,
                        cmap=my_cmap,
                        )

        ax.set_xlabel('Frequency [kHz]')
        ax.set_ylabel('Time [s]')
        ax.set_zlabel('Amplitude [a.u.]')
        if log:
            ax.set_zscale('log')
        plt.tight_layout()

        return fig, ax, figure_dict

    def animate_3d(self, led_converter, file_name='fft', overwrite=False, log=True, t_steps=23, f_steps=30,
                   cmap='viridis', n_trans=0,
                   facecolor='white', steps=36, fps=30):
        if log:
            str_scale = 'log'
        else:
            str_scale = 'lin'

        file_name = f'{file_name}_t{t_steps}_f{f_steps}_{str_scale}_{cmap}_' \
                    f'ntrans_{n_trans}_{facecolor}_s{steps}_fps{fps}.mp4'
        if os.path.exists(file_name) and not overwrite:
            print(f"File exists: {file_name}")
            # return
        print(f"File: {file_name}")

        self.plot_3d(led_converter=led_converter,
                     log=log,
                     t_steps=t_steps,
                     f_steps=f_steps,
                     cmap=cmap,
                     facecolor=facecolor,
                     n_trans=n_trans)

        def animate(i):
            self.ax.view_init(15, i)
            return self.ax

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = matplotlib.animation.FuncAnimation(self.fig, animate,
                                                  # init_func=init,
                                                  frames=np.linspace(0, 360, steps),
                                                  interval=fps,
                                                  blit=True)

        # save the animation as an mp4.  This requires ffmpeg or mencoder to be
        # installed.  The extra_args ensure that the x264 codec is used, so that
        # the video can be embedded in html5.  You may need to adjust this for
        # your system: for more information, see
        # http://matplotlib.sourceforge.net/api/animation_api.html
        with tqdm.tqdm(range(steps), file=sys.stdout) as pbar:
            anim.save(file_name, fps=fps, extra_args=['-vcodec', 'libx264'], savefig_kwargs=self.figure_dict,
                      progress_callback=lambda i, n: pbar.update())
