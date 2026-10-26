import random
#Datos de entrenamiento
datos = [
    "El aprendiz estudia",
    "El aprendiz programa",
    "El aprendiz  desarrolla",
    "El estudiante estudia",
    "El estudiante programa",
    "El estudiante desarrolla",
    "El programador desarrolla software"
]

"""print("=== datos ===")
print(datos)"""


#modelo = construir relaciones entre palabras
modelo = {}
#Separar las palabras
for frase in datos:
    palabra = frase.split()
    print(palabra)

    for i in range(len(palabra)-1):
        actual = palabra[i]
        siguiente = palabra[i+1]

        if actual not in modelo:
            modelo[actual] = []

            modelo[actual].append(siguiente)
print("\n modelo")
for actual, siguiente in modelo.items():
        print(actual,"->",siguiente)

#Generar la palabra a partir del patron
actual = "aprendiz"

if actual in modelo:
    siguiente = random.choice(modelo[actual])
    print(actual,siguiente)
else:
    print("No conozco esa palabra")

#Crear la funcion generadora

def generar(actual):
     if actual not in modelo:
          return "No conozco esa palabra"
     
     siguiente = random.choice(modelo[actual])
     return actual + " " + siguiente
print("El resultado final")
print(generar("aprendiz"))

def generar_frase(actual,cantidad = 3):
     frase = [actual]
     for i in range (cantidad - 1):
          if actual not in modelo:
               break
          siguiente = random.choice(modelo[actual])
          frase.append(siguiente)

          actual = siguiente
          return " ".join(frase)
print("\n Frase generada")
print(generar_frase("estudiante"))