import runpy
import sys
import os

def mostrar_menu():
    print(f"\n__--||  M E N U   P R I N C I P A L  ||--__")
    print("1. Sistema De Notas Por Voz")
    print("0. SALIR")

if __name__ == "__main__":
    running = True
    while running:
        mostrar_menu()
        opcion = int(input("INGRESE UNA OPCION PARA EJECUTAR PROGRAMA: "))
    
        if opcion == 1:
            print("\nAbriendo Sistema De Notas Por Voz...\n")
            script_rel = os.path.join("doc_secreto", "main.py")
            script_path = os.path.abspath(script_rel)
            script_dir = os.path.dirname(script_path)
            try:
                # Añade temporalmente la carpeta `doc_secreto` a sys.path
                sys.path.insert(0, script_dir)
                runpy.run_path(script_path, run_name="__main__")
            except Exception as e:
                print("Error al ejecutar 'doc_secreto/main.py':", e)
            finally:
                # Restaurar sys.path (eliminar la entrada que agregamos si sigue presente)
                if sys.path and sys.path[0] == script_dir:
                    sys.path.pop(0)
        elif opcion == 0:
            running = False
