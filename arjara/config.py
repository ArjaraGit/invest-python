from pathlib import Path

""" Ограничения через списки """
acc_name_list = ["Основной счет", "ИИС"]
#acc_name_list = ["ИИС"]

""" Путь к yaml файлам """
yaml_path = Path(Path.cwd().parent, "portfolio")

if yaml_path.exists():
    pass
else:
    yaml_path = Path(Path.cwd(), "portfolio")

base_yaml_file = "base.yaml"
