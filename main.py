# main.py
# Orquestador simple: mano -> time -> noboard

import sys


def _call(module_name):
    try:
        mod = __import__(module_name)
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        sys.exit(1)

    if hasattr(mod, "run"):
        return mod.run()
    if hasattr(mod, "main"):
        return mod.main()

    print(f"{module_name} has no run() or main()")
    sys.exit(1)


def main():
    print("Starting musica_new...")

    # 1) MANO
    mano_result = _call("reconocer_mano")

    # 2) TIME
    time_result = _call("encontrar_time")

    # 3) NOBOARD
    noboard_result = _call("encontrar_noboard")

    # Imprimir solo resumen limpio
    print("\n--- RESULT ---")
    print("mano:", mano_result if mano_result is not None else "")
    print("time:", time_result if time_result is not None else "")
    print("noboard:", noboard_result if noboard_result is not None else "")


if __name__ == "__main__":
    main()
