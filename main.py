import runpy
import sys
import os

def mostrar_menu():
    print(f"\n__--||  M E N U   P R I N C I P A L  ||--__")
    print("1. Sistema De Notas Por Voz")
    print("0. SALIR")

def ejecutar_script(script_rel, nombre_error):
    script_path = os.path.abspath(script_rel)
    script_dir = os.path.dirname(script_path)

    try:
        sys.path.insert(0, script_dir)
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        print(f"Error al ejecutar '{nombre_error}':", e)
    finally:
        if sys.path and sys.path[0] == script_dir:
            sys.path.pop(0)

if __name__ == "__main__":
    running = True
    while running:
        mostrar_menu()
        opcion = int(input("INGRESE UNA OPCION PARA EJECUTAR PROGRAMA: "))

        if opcion == 1:
            print("\nAbriendo Sistema De Notas Por Voz...\n")
            ejecutar_script(os.path.join("doc_secreto", "main.py"), "doc_secreto/main.py")

        elif opcion == 2:
            print("\nAbriendo Grabadora De Voz...\n")
            ejecutar_script("navegador.py", "navegador.py")

        elif opcion == 3:
            print("\nAbriendo Analizador De Audio...\n")
            ejecutar_script(os.path.join("testeo", "pruebas.py"), "testeo/pruebas.py")
        
        #elif opcion == 4:
        
        elif opcion == 0:
            running = False
        
        else:
            print("\nOpcion No Disponible")
