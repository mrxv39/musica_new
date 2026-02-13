# main.py
# Punto de entrada principal del proyecto musica_new

import sys

print("Starting musica_new...")

try:
    import reconocer_mano
except ImportError as e:
    print("Error importing reconocer_mano:", e)
    sys.exit(1)


def _execute():
    if hasattr(reconocer_mano, "run") and callable(reconocer_mano.run):
        reconocer_mano.run()
    elif hasattr(reconocer_mano, "main") and callable(reconocer_mano.main):
        reconocer_mano.main()
    else:
        print("reconocer_mano does not expose run() or main()")
        sys.exit(1)


if __name__ == "__main__":
    _execute()
