import radioamnion

# TODO: add argparser

if __name__ == "__main__":
    f_name = 'test.wav'

    audio_led = radioamnion.Audio2LED(f_name)
    print(f'Resulting fps: {audio_led.fps:.2f} frames/s')

    csv_file = audio_led.save_to_csv()

    print(f'Saved to: {csv_file}')