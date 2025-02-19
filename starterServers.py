import subprocess

# Liste des fichiers à exécuter
servers = [
    "RollerShades.py",
    "MotionDetector.py",
    "airControl.py",
    "lampe.py",
    "WeatherServer.py",
    "ClimaServer.py"
]

# Démarrer chaque serveur dans un sous-processus
processes = []
for server in servers:
    process = subprocess.Popen(['python', server])
    processes.append(process)

# Attendre que tous les processus se terminent
for process in processes:
    process.wait()
