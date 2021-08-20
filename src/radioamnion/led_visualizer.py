import sys

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import moviepy.editor as mpe
import tqdm


class LEDVisualizer:
    def __init__(self, ):
        self.led_channel_levels = None
        self.fps = None

        # First set up the figure, the axis, and the plot element we want to animate
        self.figure_dict = {'facecolor': 'black'}

        # plt plotting
        self.fig = None
        self.ax = None
        self.scatter = None

        self.anim = None

        self._create_fig_()

    def _create_fig_(self, ):
        theta = np.linspace(0, np.pi * 2, 1000)
        r = 5
        scale = .8

        x_pos = np.array([-1, 1, r, r]) * scale
        y_pos = np.array([-r, -r, -1, 1]) * scale

        color = ['white', 'C0', 'white', 'C0']

        self.fig = plt.figure(**self.figure_dict)
        self.ax = plt.axes(xlim=(-r * 1.1, r * 1.1),
                           ylim=(-r * 1.1, r * 1.1),
                           **self.figure_dict)

        # plot the 'module' surrounding circle
        self.ax.plot(r * np.cos(theta), r * np.sin(theta))

        # plot the LEDs
        self.scatter = []
        for i, x_i in enumerate(x_pos):
            self.scatter.append(self.ax.scatter(x_pos[i], y_pos[i], s=500, c=color[i], alpha=1.))
        self.ax.set_aspect('equal')

        plt.tight_layout()

    def set_alpha(self, alpha):
        for scatter_i, alpha_i in zip(self.scatter, alpha):
            scatter_i.set_alpha(alpha_i)

    # initialization function: plot the background of each frame
    def init(self):
        self.set_alpha([0, 0, 0, 0])
        return self.scatter

    # animation function.  This is called sequentially
    def animate(self, i):
        self.set_alpha(self.led_channel_levels[:, i] / 16.)
        return self.scatter

    def cal_animation(self, led_channel_levels, fps, file_name):
        self.led_channel_levels = led_channel_levels
        self.fps = fps

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = matplotlib.animation.FuncAnimation(self.fig, self.animate,
                                                  init_func=self.init,
                                                  frames=self.led_channel_levels.shape[-1],
                                                  interval=self.fps,
                                                  blit=True)

        with tqdm.tqdm(range(self.led_channel_levels.shape[-1]), file=sys.stdout) as pbar:
            # save the animation as an mp4.  This requires ffmpeg or mencoder to be
            # installed.  The extra_args ensure that the x264 codec is used, so that
            # the video can be embedded in html5.  You may need to adjust this for
            # your system: for more information, see
            # http://matplotlib.sourceforge.net/api/animation_api.html
            anim.save(file_name, fps=fps,
                      extra_args=['-vcodec', 'libx264'],
                      savefig_kwargs=self.figure_dict,
                      progress_callback=lambda i, n: pbar.update())

    @staticmethod
    def add_music(file_name_clip, file_name_audio, file_name_final=None):
        if file_name_final == file_name_clip:
            raise ValueError('file_name_clip and file_name_clip have to be unequal')
        elif file_name_final is None:
            file_name_final = file_name_clip.rsplit('.', 1)[0] + '_audio.' + file_name_clip.rsplit('.', 1)[1]

        my_clip = mpe.VideoFileClip(file_name_clip)
        audio_background = mpe.AudioFileClip(file_name_audio)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(file_name_final, threads=6)
