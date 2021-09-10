#!/usr/bin/env python
# encoding: utf8
# Artificial Intelligence, UBI 2019-20
# Modified by: Pedro Marreiros Nº36642, Diogo Dias Nº35394
 
import rospy
import array as arr
import math
import time
from std_msgs.msg import String
from nav_msgs.msg import Odometry
 
x_ant = 0
y_ant = 0
div_ant = 0
div_ant_ant = -1
obj_ant = ''
start_time = time.time()
 
# Lista de Objetos
#ObjectoID da sala] = obj1,obj2,...
objecto = [[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
 
# Lista de Divisões
#Divisão[ID] = Xmin, Xmax, Ymin, Ymax, Desc, visitada(0=não,1=sim), divisão anterior
Divisao = [[-15.6,3.6,-3.1,-1.5,-1,0,-1],
    [-11.8,-9.6,-1.3,5.1,-1,0,-1],
    [-11.8,3.6,5.2,7.3,-1,0,-1],
    [-4,-1.4,-1.3,5.1,-1,0,-1],
    [-15.6,-12.4,-0.8,2.3,-1,0,-1],
    [-15.6,-12.4,2.9,7.3,-1,0,-1],
    [-15.6,-11.1,7.9,11.1,-1,0,-1],
    [-10.6,-6.2,7.9,11.1,-1,0,-1],
    [-5.5,-1.2,7.9,11.1,-1,0,-1],
    [-0.6,3.6,7.9,11.1,-1,0,-1],
    [-0.8,3.6,2.3,4.9,-1,0,-1],
    [-0.8,3.6,-0.8,1.7,-1,0,-1],
    [-9,-7,-0.8,4.9,-1,0,-1],
    [-6.5,-4.5,-0.8,4.9,-1,0,-1]]
 
# ---------------------------------------------------------------
# odometry callback
def callback(data):
    global x_ant, y_ant, div_ant, div_ant_ant
    x=data.pose.pose.position.x-15
    y=data.pose.pose.position.y-1.5
    # show coordinates only when they change
    if x != x_ant or y != y_ant:
        print "x=%.1f y=%.1f" % (x,y)
        print "Divisao %i" % (divisao(x,y) + 1)
    x_ant = x
    y_ant = y
 
# ---------------------------------------------------------------
# Divisao do Robot no mapa (devolve o ID)
def divisao(x,y):
    global div_ant, div_ant_ant
    for i in range(14):
        if x >= Divisao[i][0] and x <= Divisao[i][1] and y >= Divisao[i][2] and y <= Divisao[i][3]:
            if i != div_ant:
        if Divisao[i][5] == 0:
           Divisao[i][5] = 1
           Divisao[i][6] = div_ant
                div_ant_ant = div_ant
                div_ant = i
            print "div %i di_ant %i" % (div_ant, div_ant_ant)
            if i == 0 or i == 1 or i == 2 or i == 3:
                Divisao[i][4] = 5            #Corredores
                return i
            #VERIFICAR O TIPO DE DIVISÃO
            camas = 0
            mesas = 0
            cadeiras = 0
            for j in range(len(objecto[i])):
                if "bed" in objecto[i][j]:
                    camas += 1
                elif "table" in objecto[i][j]:
                    mesas += 1
                elif "chair" in objecto[i][j]:
                    cadeiras += 1          
            if  Divisao[i][4] == 3:
                return i
            elif camas == 1:
                Divisao[i][4] = 1            #Quarto Simples
            elif camas == 2:
                Divisao[i][4] = 2            #Quarto Duplo              
            elif mesas == 1 and cadeiras > 1:
                Divisao[i][4] = 4            #Sala de Convívio
            else:
                Divisao[i][4] = 0            #Sala Genérica
            if Divisao[div_ant_ant][4] != 5 and (Divisao[div_ant_ant][4] == 1 or Divisao[div_ant_ant][4] == 2 or Divisao[i][4] == 1 or Divisao[i][4] == 2):
                print "Suites: %i%i" % (i, div_ant_ant)
                Divisao[i][4] = 3            #Suite
                Divisao[div_ant_ant][4] = 3        #Suite
            return i
    return -1
 
# ---------------------------------------------------------------
# Adiciona objetos à matriz
def addobj(id,nome):
    for i in range(len(objecto[id])):
        if nome == objecto[id][i]:
            return
    objecto[id].append(nome)
    print objecto[id]
 
# ---------------------------------------------------------------
# object_recognition callback
def callback1(data):
    global obj_ant, div_ant
    obj = data.data.split(",")
 
    if obj != obj_ant and data.data != "":
        print "object is %s" % data.data
        for i in range(len(obj)):
            addobj(div_ant, obj[i])
        obj_ant = obj
 
# ---------------------------------------------------------------
# questions_keyboard callback
def callback2(data):
    #PERGUNTA 1
    if int(data.data) == 1:
        cont_total = 0
        cont_pessoas = 0
        for i in range(3,14):
            if Divisao[i][4] != -1:
                cont_total += 1
            for j in range(len(objecto[i])):
                if "person" in objecto[i][j]:
                    cont_pessoas += 1
                    break
        print "Até ao momento foram encontradas %i Divisões não ocupadas." % (cont_total - cont_pessoas)
    #PERGUNTA 2
    if int(data.data) == 2:
        cont_suites = 0
        for i in range (3,14):
            if Divisao[i][4] == 3:
                cont_suites += 1
        print "Até ao momento foram encontradas %i Suites." % (cont_suites / 2)
    print "question is %s" % data.data
 
    #PERGUNTA 4
    if int(data.data) == 4:
        comps = arr.array('i', [0,0,0,0,0])
        for i in range(3,14):
            for j in range(len(objecto[i])):
                if "computer" in objecto[i][j]:
                    comps[Divisao[i][4]] += 1
        MaxID = "Por agora nada"
        MAX = 0
        for k in range(5):
            if comps[k] > MAX:
                MAX = comps[k]
                if k == 0:
                    MaxID = "Sala Genérica"
                elif k == 1:
                    MaxID = "Quarto Simples"
                elif k == 2:
                    MaxID = "Quarto Duplo"
                elif k == 3:
                    MaxID = "Suite"
                elif k == 4:
                    MaxID = "Sala de Convívio"
        print "É recomendado: %s." % MaxID
 
    #PERGUNTA 5
    if int(data.data) == 5:
        MIN = 9999
        MinID = 0
        for i in range(3,14):
            if Divisao[i][4] == 1 and i != divisao(x_ant, y_ant):
                x = (Divisao[i][0] + Divisao[i][1]) / 2
                y = (Divisao[i][2] + Divisao[i][3]) / 2
                dist = math.sqrt(((x_ant - x)**2) + ((y_ant - y)**2))
                #print dist
                if dist < MIN:
                    MIN = dist
                    MinID = i + 1
        if MinID > 0:
            print "O número do Quarto Simples mais próximo é, até agora, %i." % MinID
        else:
            print "Ainda não foram encontrados Quartos Simples."
 
    #PERGUNTA 3
    if int(data.data) == 3:
    cont_people_corridor = 0
    cont_people_room = 0
    cont_people_total = 0
    prob_room = 0
    prob_corridor = 0
        for i in range (3):
        for j in range (len(objecto[i])):
        if "person" in objecto[i][j]:
            cont_people_corridor += 1
    for i in range (4, 14):
        for j in range (len(objecto[i])):
        if "person" in objecto[i][j]:
            cont_people_room += 1
    cont_people_total = cont_people_corridor + cont_people_room
    if cont_people_total == 0:
       print "Ainda não foram encontradas pessoas"
    else:
       prob_corridor = cont_people_corridor / cont_people_total
       prob_room = cont_people_room / cont_people_total
       if prob_corridor > prob_room:
          print "É mais provável encontrar pessoas nos corredores"
       else:
          print "É mais provável encontrar pessoas nos quartos"
    #PERGUNTA 6
    if int(data.data) == 6:
        current_div = divisao(x_ant,y_ant)
    if current_div == 0:
       print "Já se encontra na divisão do elevador"
    else:
       while current_div != 0:
          aux_div = current_div
              current_div = Divisao[aux_div][6]
          print "Divisão %i -> Divisão %i" % ((aux_div + 1), (current_div + 1))
    #PERGUNTA 7
    if int(data.data) == 7:
        current_time = time.time() - start_time
    print "Time since start = %i" % current_time
    books_found_total = 0
    estimated_books = 0
 
    for i in range (14):
       for j in range(len(objecto[i])):
          if "book" in objecto[i][j]:
            books_found_total += 1
 
    estimated_books = (120 * books_found_total) / current_time
 
    print "Estima-se encontrar %f livros nos próximos 2 minutos" % estimated_books
 
    #PERGUNTA 8
    if int(data.data) == 8:
    prob_find_book = 0
    prob_not_find_book = 0
    prob_find_chair = 0
    prob_find_table = 0
    cont_books = 0
    cont_chair = 0
    cont_table = 0
    cont_total = 0
   
    for i in range(14):
       cont_total += len(objecto[i])
   
    for i in range(14):
       for j in range(len(objecto[i])):
          if "book" in objecto[i][j]:
        cont_books += 1
 
    prob_find_book = float(cont_books) / float(cont_total)
    prob_not_find_book = 1.0 - prob_find_book
 
    for i in range(14):
       for j in range(len(objecto[i])):
          if "chair" in objecto[i][j]:
        cont_chair += 1
 
    prob_find_chair = float(cont_chair) / float(cont_total)
 
 
    for i in range(14):
       for j in range(len(objecto[i])):
          if "table" in objecto[i][j]:
        cont_table += 1
 
    prob_find_table = float(cont_table) / float(cont_total)
 
    prob_result = (float(prob_find_table) * float(prob_find_chair) * float(prob_not_find_book)) / float(prob_not_find_book)
 
    print "A probabilidade é %f" % prob_result
 
   
 
   
   
 
   
 
# ---------------------------------------------------------------
def agent():
    rospy.init_node('agent')
 
    rospy.Subscriber("questions_keyboard", String, callback2)
    rospy.Subscriber("object_recognition", String, callback1)
    rospy.Subscriber("odom", Odometry, callback)
 
    rospy.spin()
 
# ---------------------------------------------------------------
if __name__ == '__main__':
    agent()
