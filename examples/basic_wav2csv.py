import radioamnion

# TODO: add argparser

if __name__ == "__main__":
    f_name = 'test.wav'

    audio_led = radioamnion.Audio2LED(f_name)
    print(f'Resulting fps: {audio_led.fps:.2f} frames/s')

    audio_led.save_to_csv()