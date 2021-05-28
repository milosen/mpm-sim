from mpm_sim.kspace import load_h5_signal


def main():
    signals_h5 = "signals.h5"
    _, m = load_h5_signal(signals_h5)
    print(m)


if __name__ == '__main__':
    main()
