import subprocess
import sys
import os


def main():
    # Percorso assoluto dello script principale
    main_script = os.path.join(os.path.dirname(__file__), "main.py")

    # Lancia Streamlit con il file principale
    subprocess.run([sys.executable, "-m", "streamlit", "run", main_script])
    print(f"Avvio Streamlit con il file: {main_script}")
    print("Apri il browser su http://localhost:8501")

    try:
        # Lancia Streamlit con il file principale
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", main_script], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'avvio di Streamlit: {e}")
    except Exception as e:
        print(f"Errore generico: {e}")


if __name__ == "__main__":
    main()
