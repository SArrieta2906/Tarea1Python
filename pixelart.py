import re
import numpy as np
from PIL import Image

RepetirBox = []

'''
Descripcion de la funcion
Funcion encargada de escribir las lineas con errores de sintaxis en el errores.txt.

Parametros:
Error: array con los datos del error como el numero de linea y el cointenido de la linea.
Errortxt: archivo donde se escribira el error.

Retorno:
'''

def writeError(Error, Errortxt):        
    Errortxt.write(' '.join(Error))

'''
Descripcion de la funcion
Esta funcion revisa la sintaxis de las primeras lineas correspondientes a la configuracion del pixelart.png como el ancho y el color de fondo.

Parametros:
line: linea a revisar sintacticamente
n: numero de linea
Errortxt: archivo donde se escribira el error

Retorno:
'''

def ImgConfigSintax(line, n, Errortxt):
    if(n == 2):
        patern = r'^(Color de fondo) (Rojo|Verde|Azul|Negro|Blanco|RGB\(([0-9]{1,3}),([0-9]{1,3}),([0-9]{1,3})\))$'
    elif(n == 3):
        patern = r'^\n$'
    elif(n == 1):
        patern = r'^Ancho ([0-9]+)$'

    result = re.search(patern, line)

    if(result == None):
        writeError([str(n), line], Errortxt)

'''
Descripcion de la funcion
revision sintactica de la operacion pintar

Parametros:
array: array con todos los comandos 'Pintar' que se encontraron en la linea
 
Retorno:
Si detecta alguna operacion que no coincida con las reglas de sintaxis retorna True para posteriormente escribir el error en la funcion commandSintax, de lo contrario retorna False
'''
def CheckPintar(array):
    instructions = r'(Pintar )(Rojo|Verde|Azul|Negro|Blanco|RGB\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3}\))'
    for j in array:
        if(re.search(instructions, j) == None):
            return True
    return False

'''
Descripcion de la funcion
Funcion encargada de escribir las lineas con errores de sintaxis en el errores.txt

Parametros:
Error: array con los datos del error como el numero de linea y el cointenido de la linea
Errortxt: archivo donde se escribira el error

Retorno:
'''

def ComandSintax(line, n, Errortxt):
    if(re.search(r'^\s*\n', line) != None):
        writeError([str(n), line], Errortxt)

    instructions = r' Izquierda| Derecha| Avanzar\s?[-]?[0-9]*| Pintar [a-zA-Z0-9,()]*| Repetir [0-9]+ veces \{| }|\s'
    result = re.split(instructions, ' ' + line)
    result = list(filter(None, result))

    openCheck = re.search(r'{', line)
    closeCheck = re.search(r'}', line)

    if(openCheck != None or closeCheck != None):
        RepetirBox.append((line, n))

    CheckNegatives = re.findall('(Avanzar )([-]?[0-9]+)', line)
    
    for j in CheckNegatives:
        if(int(j[1]) < 0):
            writeError([str(n), line], Errortxt)

    if(CheckPintar(re.findall(r'Pintar [a-zA-Z0-9,()]*', line)) or len(result) != 0):
        writeError([str(n), line], Errortxt)
    
'''
Descripcion de la funcion
Funcion encargada de escribir las lineas con errores de sintaxis en el errores.txt

Parametros:
Error: array con los datos del error como el numero de linea y el cointenido de la linea
Errortxt: archivo donde se escribira el error

Retorno:
'''

def RepetirSintax(array, Errortxt):
    lineError = []
    closingNumber = 0
    for i in range(len(array)):
        if(len(re.findall(r'\{', array[i][0])) > 0):
            closingNumber += len(re.findall(r'\{', array[i][0]))
            lineError.append([array[i], len(re.findall(r'\{', array[i][0]))])
        
        if(len(re.findall(r'\}', array[i][0])) > 0):
            dlt = len(re.findall(r'\}', array[i][0]))
            closingNumber -= dlt
            
            if(len(lineError) > 0):
                while(dlt != 0):
                    if(lineError[-1][1] > 1):
                        lineError[-1][1] -= 1
                    else:
                        lineError.pop()
                    dlt -= 1
                        
        if(closingNumber < 0):
            writeError([str(array[i][1]), array[i][0]], Errortxt)
            if(i != len(array)-1):
                RepetirSintax(array[i+1:], Errortxt)
                return

    if(closingNumber > 0):
        for j in range(closingNumber):
            writeError([str(lineError[j][0][1]), lineError[j][0][0]], Errortxt)

'''
Descripcion de la funcion
Funcion encargada de escribir las lineas con errores de sintaxis en el errores.txt

Parametros:
Error: array con los datos del error como el numero de linea y el cointenido de la linea
Errortxt: archivo donde se escribira el error

Retorno:
'''

def ConvertRgb(color, line):
    if(color == 'Rojo'):
        return [255,0,0]
    elif(color == 'Verde'):
        return [0,255,0]
    elif(color == 'Azul'):
        return [0,0,255]
    elif(color == 'Negro'):
        return [0,0,0]
    elif(color == 'Blanco'):
        return [255,255,255]
    else:
        getColor = re.findall('[0-9]{1,3}', color)
        for x in range(len(getColor)):
            if(int(getColor[x]) > 255 or int(getColor[x]) < 0):
                exit('RGB Invalido' + ' ' + line)
            getColor[x] = int(getColor[x])
        return getColor

'''
Descripcion de la funcion
Funcion encargada de escribir las lineas con errores de sintaxis en el errores.txt

Parametros:
Error: array con los datos del error como el numero de linea y el cointenido de la linea
Errortxt: archivo donde se escribira el error

Retorno:
'''

def Advance(ins, Cpos, Adv, size):
    move = ins
    if(ins == ' ' or ins == None):
        move = '1'

    for i in range(2):
        Cpos[i] = Cpos[i] + (Adv[i]*int(move))

        if(Cpos[i] > size-1 or Cpos[i] < 0):
            return False
    return True

'''
Descripcion de la funcion
Esta funcion se encarga de ejecutar los distintos comandos que modifican la mariz dada segun lo indique el codigo

Parametros:
matriz: matriz que representa el dibujo y que sera modificada segun lo indique el codigo
text: linea de codigo que contiene las instrucciones que modificaran a la matriz
advance: este es un array el cual funciona coo un vector representativo que determina la direccion en la que se aplicaran ciertos comandos como el de avanzar N casillas
pos: posicion actual en la matriz
ancho: indica las dimensiones de la matriz

Retorno:
'''

def ExecuteCommand(matriz, text, advance, pos, ancho):
    if(len(text) == 0):
        return 

    inst = re.search(r'Izquierda|Derecha|(Avanzar)( [0-9]*)?|(Pintar) (RGB)?([a-zA-Z0-9,()]+)|(Repetir)( [0-9]+) veces {', text)
    if(inst != None):
        Error = re.search(r'\([0-9]+\)', text[inst.end():])
        if(inst.group(1) == 'Avanzar'):
            status = Advance(inst.group(2), pos, advance, ancho)
            if status == False:
                exit("Error en la linea" + ' ' + Error.group())
        
        if(inst.group(3) == 'Pintar'):
            matriz[pos[0], pos[1]] = ConvertRgb(inst.group(5), Error.group())

        if(inst.group() == 'Izquierda'):
            if(advance[0] != 0):
                aux = advance[0]
                advance[0] = advance[1]
                advance[1] = aux
            else:
                aux = advance[0]
                advance[0] = -advance[1]
                advance[1] = aux

        if(inst.group() == 'Derecha'):
            if(advance[0] == 0):
                aux = advance[1]
                advance[1] = advance[0]
                advance[0] = aux
            else:
                aux = advance[1]
                advance[1] = -advance[0]
                advance[0] = aux

        if(inst.group(6) == 'Repetir'):
            repeatCounter = 1
            sendText = inst.end()

            while(repeatCounter != 0):
                Close = re.search(r'(Repetir [0-9]+ veces \{)|(\})', text[sendText:])

                if(Close.group(1) != None):
                    repeatCounter += 1
                elif(Close.group(2) != None):
                    repeatCounter -= 1
                
                sendText = sendText + Close.end()

            for i in range(int(inst.group(7))):
                ExecuteCommand(matriz, text[inst.end():sendText] + Error.group(), advance, pos, ancho)
            
            ExecuteCommand(matriz, text[sendText:], advance, pos, ancho)
            return

        ExecuteCommand(matriz, text[inst.end():], advance, pos, ancho)
    


file = open('codigo.txt', 'r')
Errorfile = open('errores.txt','w+')

text = file.readlines()

for i in range(3):
    ImgConfigSintax(text[i], i+1, Errorfile)

for j in range(3, len(text)):
    ComandSintax(text[j], j+1, Errorfile)

RepetirSintax(RepetirBox, Errorfile)

Errorfile.seek(0)
if(Errorfile.readline() == ""):
    Errorfile.write("No hay errores!")

    ancho = re.search(r'\d+', text[0])
    ancho = ancho.group()

    fondo = re.search(r'Rojo|Verde|Azul|Negro|Blanco|\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3}\)', text[1])
    fondo = ConvertRgb(fondo.group(), 2)

    matriz = np.full((int(ancho), int(ancho), 3), fondo, dtype=np.uint8)

    for i in range(len(text)):
        text[i] = re.sub('\n', ' (' + str(i+1) + ') ', text[i])

    text[len(text)-1] = text[len(text)-1] + ' (' + str(len(text)) + ')'
    textString = ' '.join(text[3:])
    ExecuteCommand(matriz, textString, [0, 1], [0, 0], int(ancho))#[-1, 0][0, -1][1, 0][0,1]IZQ [1, 0] [0, -1] [-1, 0] [0, 1]

    np.swapaxes(matriz, 0, -1)
    N = np.shape(matriz)[0]

    img = Image.fromarray(matriz, 'RGB')
    img = img.resize((N*50, N*50), Image.Resampling.BOX)
    img.save('pixelart.png')

    print(matriz)

Errorfile.close()
file.close()
