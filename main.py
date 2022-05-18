import time
import os
import sys
from collections import defaultdict
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import (
    Qt, QPoint, QPointF
)
from PySide6.QtGui import (
    QPixmap, QPainter, QPaintEvent, QBrush,
    QPen, QFont, QAction, QIcon, QCursor,
    QPainterPath
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QToolBar, QComboBox, QPushButton,
    QLineEdit
)
from gtts import gTTS

class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowIcon(QIcon("graph.ico"))
        self.setWindowTitle("Shape drawer")
        "tamaños de los circulos de los estados"
        self.size_inner_circle = 25
        self.size_outer_circle = 33
        "listas de estados"
        self.main_dictionary = {0:QPoint(100, 300)}
        self.states_dictionary = {0:QPoint(100, 300)}
        self.accepted_states_dictionary = {}
        self.transitions_dictionary = defaultdict(list)
        "inicializacion de componentes"
        self.initUI()
        self.initMenuBar()
        self.initTransitionsModule()
        self.initValidationsModule()
        self.initToolbar()
        self.statusBar().showMessage("Welcome to the AFND visualizer", 5000)
        self.show()
        """para deshabilitar la molesta opcion de hide toolbar cuando se da 
        click derecho, deshabilita los context menu en general"""
        self.setContextMenuPolicy(Qt.PreventContextMenu)

    def initUI(self):
        self.actual_pos = QPoint(0, 0)
        self.input = False
        self.lienzo = QLabel()
        self.pixmap = QPixmap(self.size())
        self.painter = QPainter(self.pixmap)
        self.font = QFont()
        self.font.setPixelSize(20)
        self.pen = QPen(Qt.black, 4, Qt.SolidLine)
        self.painter.setPen(self.pen)
        self.painter.setFont(self.font)
        self.painter.drawPixmap(0, 0, self.pixmap)
        self.pixmap.fill(Qt.white)
        self.painter.drawText(self.main_dictionary[0], str(len(self.main_dictionary) - 1))
        self.painter.drawEllipse(self.main_dictionary[0], self.size_inner_circle, self.size_inner_circle)
        puntoFlechaEstadoInicial = QPointF(self.main_dictionary[0].x() - self.size_inner_circle, self.main_dictionary[0].y())
        self.painter.drawLine(puntoFlechaEstadoInicial, QPointF(puntoFlechaEstadoInicial.x() - 45, puntoFlechaEstadoInicial.y()))
        self.painter.drawLine(puntoFlechaEstadoInicial, QPointF(puntoFlechaEstadoInicial.x() - 15, puntoFlechaEstadoInicial.y() - 15))
        self.painter.drawLine(puntoFlechaEstadoInicial, QPointF(puntoFlechaEstadoInicial.x() - 15, puntoFlechaEstadoInicial.y() + 15))
        self.setCentralWidget(self.lienzo)

    def paintEvent(self, event: QPaintEvent):
        self.lienzo.setPixmap(self.pixmap)
        if not self.statusBar().currentMessage():
            self.statusBar().setStyleSheet("background-color:#F0F0F0")

    def initMenuBar(self):
        self.menu_bar = self.menuBar()
        #opcion 1
        self.opcion1 = self.menu_bar.addMenu("File")
        self.subAction11 = self.opcion1.addAction("Save")
        self.subAction12 = self.opcion1.addAction("Load")
        self.opcion1.addSeparator()
        self.opcion1.addAction("Exit", self.close)
        #opcion2
        self.opcion2 = self.menu_bar.addMenu("Toolbar")
        self.subAction21 = self.opcion2.addAction("Option 1", self.toolbarShow)
        self.subAction22 = self.opcion2.addAction("Option 2")
        self.subAction21.setCheckable(True)
        self.subAction22.setCheckable(True)

    "modulo para insertar las aristas o transiciones(2 combobox y un boton)"
    def initTransitionsModule(self):
        self.transitionsModule = QWidget()
        self.layoutTransitionsModule = QVBoxLayout(self.transitionsModule)
        self.layoutComboboxes = QHBoxLayout()
        self.layoutLineEdit = QHBoxLayout()
        self.layoutButton = QVBoxLayout()
        self.initialState = QComboBox()
        self.endingState = QComboBox()
        self.initialState.setPlaceholderText("State 1")
        self.endingState.setPlaceholderText("State 2")
        self.initialState.addItem("0")
        self.endingState.addItem("0")
        self.textHolder = QLineEdit()
        self.layoutLineEdit.addWidget(self.textHolder)
        self.drawTransitionButton = QPushButton("Draw transition")
        self.drawTransitionButton.clicked.connect(self.drawTransitions)
        self.layoutComboboxes.addWidget(self.initialState)
        self.layoutComboboxes.addWidget(self.endingState)
        self.layoutButton.addWidget(self.drawTransitionButton)
        self.layoutTransitionsModule.addLayout(self.layoutComboboxes)
        self.layoutTransitionsModule.addLayout(self.layoutLineEdit)
        self.layoutTransitionsModule.addLayout(self.layoutButton)

    def initValidationsModule(self):
        self.validationsModule = QWidget()
        self.layoutValidationsModule = QVBoxLayout(self.validationsModule)
        self.layoutVerifyLineEdit = QHBoxLayout()
        self.layoutVerifyButton = QVBoxLayout()
        self.textVerifyHolder = QLineEdit()
        self.verifyButton = QPushButton("Verify")
        self.verifyButton.clicked.connect(self.verifyWord)
        self.layoutVerifyLineEdit.addWidget(self.textVerifyHolder)
        self.layoutVerifyButton.addWidget(self.verifyButton)
        self.layoutValidationsModule.addLayout(self.layoutVerifyLineEdit)
        self.layoutValidationsModule.addLayout(self.layoutVerifyButton)

    def initToolbar(self):
        self.subAction21.setChecked(True)
        self.options_toolbar = QToolBar("Options1")
        self.options_toolbar.setMovable(False)
        self.addToolBar(Qt.RightToolBarArea, self.options_toolbar)
        self.draw_state_action = QAction("Draw state")
        self.draw_accept_state_action = QAction("Draw accept state")
        self.draw_transition_action = QAction("Draw transition")
        self.draw_state_action.triggered.connect(self.drawStates)
        self.draw_accept_state_action.triggered.connect(self.drawStates)
        self.draw_transition_action.triggered.connect(self.drawTransitions)
        self.options_toolbar.addAction(self.draw_state_action)
        self.options_toolbar.addAction(self.draw_accept_state_action)
        self.options_toolbar.addSeparator()
        self.options_toolbar.addWidget(self.transitionsModule)
        self.options_toolbar.addSeparator()
        self.options_toolbar.addWidget(self.validationsModule)
        self.options_toolbar.addSeparator()
        self.options_toolbar.addAction("Clear screen", self.clearScreen)
        self.options_toolbar.addAction("Show data", self.showData)

    def mouseReleaseEvent(self, QMouseEvent):
        if self.input:
            self.actual_pos = self.lienzo.mapFromGlobal(QCursor.pos())
            print("la pos elegida es: ", self.actual_pos)
            self.input = False
        else:
            print("la pos cualquiera es: ", self.lienzo.mapFromGlobal(QCursor.pos()))

    def toolbarShow(self):
        if self.options_toolbar.isVisible():
            self.options_toolbar.setVisible(False)
        else:
            self.options_toolbar.setVisible(True)
    
    def speach(self,cadena):
        speech = gTTS(cadena,lang="es",slow=True)
        speech.save("speach.mp3")
        os.system("start speach.mp3")
        time.sleep(2)

    def drawStates(self):
        """el while fuerza a los eventos, haciendo que fuerce el evento del
        mouse para recoger la posicion a dibujar"""
        self.input = True
        self.draw_state_action.setEnabled(False)
        self.draw_accept_state_action.setEnabled(False)
        self.statusBar().setStyleSheet("background-color:yellow")
        self.statusBar().showMessage("STATUS:   esperando coordenadas...")
        match self.sender().text():
            case "Draw state":

                print("Draw state case")
                while self.input:
                    QtCore.QCoreApplication.processEvents()
                self.states_dictionary[len(self.main_dictionary)] = self.actual_pos
                self.painter.drawText(self.actual_pos, str(len(self.main_dictionary)))
                self.painter.drawEllipse(self.actual_pos, self.size_inner_circle, self.size_inner_circle)
                self.initialState.addItem(str(len(self.main_dictionary)))
                self.endingState.addItem(str(len(self.main_dictionary)))
                self.main_dictionary[len(self.main_dictionary)] = self.actual_pos
                self.statusBar().setStyleSheet("background-color:green")
                self.speach("Estado dibujado")
                self.statusBar().showMessage("STATUS:   State drawed!", 2000)
            case "Draw accept state":
                print("Draw accept state case")
                while self.input:
                    QtCore.QCoreApplication.processEvents()
                self.accepted_states_dictionary[len(self.main_dictionary)] = self.actual_pos
                self.painter.drawText(self.actual_pos, str(len(self.main_dictionary)))
                self.painter.drawEllipse(self.actual_pos, self.size_inner_circle, self.size_inner_circle)
                self.painter.drawEllipse(self.actual_pos, self.size_outer_circle, self.size_outer_circle)
                self.initialState.addItem(str(len(self.main_dictionary)))
                self.endingState.addItem(str(len(self.main_dictionary)))
                self.main_dictionary[len(self.main_dictionary)] = self.actual_pos
                self.statusBar().setStyleSheet("background-color:green")
                self.speach("Estado de aceptacion dibujado")
                self.statusBar().showMessage("STATUS:   Accept state drawed!", 2000)
            case _:
                print("Error option -> draw states match")
        self.draw_state_action.setEnabled(True)
        self.draw_accept_state_action.setEnabled(True)

    def drawTransitions(self):
        primerSeleccionado = self.initialState.currentText()
        segundoSeleccionado = self.endingState.currentText()
        datosTransicion = self.textHolder.displayText()
        self.statusBar().setStyleSheet("background-color:red")
        if primerSeleccionado != "" and segundoSeleccionado != "":
            if datosTransicion != "":
                path = QPainterPath()
                punto1 = QPointF(self.main_dictionary[int(primerSeleccionado)])
                punto2 = QPointF(self.main_dictionary[int(segundoSeleccionado)])
                size_arrow = 15
                """estos pequeños condicionales son para que quede bien dibujado"""
                controlDibujado1 = self.size_inner_circle
                controlDibujado2 = self.size_inner_circle
                if int(primerSeleccionado) in self.accepted_states_dictionary:
                    controlDibujado1 = self.size_outer_circle
                if int(segundoSeleccionado) in self.accepted_states_dictionary:
                    controlDibujado2 = self.size_outer_circle

                if punto1 == punto2:
                    tamaño_circulo = controlDibujado1 * 2
                    puntoFlecha = QPointF(punto1.x(), punto1.y() - controlDibujado1)
                    self.painter.drawArc(punto1.x() - tamaño_circulo, punto1.y() - tamaño_circulo, tamaño_circulo, tamaño_circulo, 0 * 16, 270 * 16)
                    self.painter.drawLine(puntoFlecha, QPointF(puntoFlecha.x() - size_arrow, puntoFlecha.y() - size_arrow))
                    self.painter.drawLine(puntoFlecha, QPointF(puntoFlecha.x() + size_arrow, puntoFlecha.y() - size_arrow))
                    self.painter.drawText(QPointF(punto1.x() - tamaño_circulo, punto1.y() - tamaño_circulo), str(datosTransicion))
                    if self.transitions_dictionary[int(primerSeleccionado)]:
                        auxiliar_dict = {int(segundoSeleccionado):datosTransicion}
                        self.transitions_dictionary[int(primerSeleccionado)].update(auxiliar_dict)
                    else:
                        self.transitions_dictionary[int(primerSeleccionado)] = {int(segundoSeleccionado):datosTransicion}
                    self.statusBar().setStyleSheet("background-color:green")
                    self.speach("Transicion dibujada")
                    self.statusBar().showMessage("STATUS:   Transition Drawed!", 2000)
                else:
                    restaPuntos = QPoint(punto1.x() - punto2.x(), punto1.y() - punto2.y())
                    #cuadrante 1
                    if restaPuntos.x() < 0 and restaPuntos.y() > 0:
                        path.moveTo(QPointF(punto1.x(), punto1.y() - controlDibujado1))
                        puntoControl1 = QPointF(punto1.x(), punto2.y())
                        path.quadTo(puntoControl1, QPointF(punto2.x() - controlDibujado2, punto2.y()))
                        puntoFinal = path.pointAtPercent(1)
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() - size_arrow, puntoFinal.y() - size_arrow))
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() - size_arrow, puntoFinal.y() + size_arrow))
                    #cuadrante 2
                    elif restaPuntos.x() < 0 and restaPuntos.y() < 0:
                        path.moveTo(QPointF(punto1.x() + controlDibujado1, punto1.y()))
                        puntoControl1 = QPointF(punto2.x(), punto1.y())
                        path.quadTo(puntoControl1, QPointF(punto2.x(), punto2.y() - controlDibujado2))
                        puntoFinal = path.pointAtPercent(1)
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() + size_arrow, puntoFinal.y() - size_arrow))
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() - size_arrow, puntoFinal.y() - size_arrow))
                    #cuadrante 3
                    elif restaPuntos.x() > 0 and restaPuntos.y() < 0:
                        path.moveTo(QPointF(punto1.x(), punto1.y() + controlDibujado1))
                        puntoControl1 = QPointF(punto1.x(), punto2.y())
                        path.quadTo(puntoControl1, QPointF(punto2.x()  + controlDibujado2, punto2.y()))
                        puntoFinal = path.pointAtPercent(1)
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() + size_arrow, puntoFinal.y() - size_arrow))
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() + size_arrow, puntoFinal.y() + size_arrow))
                    #cuadrante 4
                    elif restaPuntos.x() > 0 and restaPuntos.y() > 0:
                        path.moveTo(QPointF(punto1.x() - controlDibujado1, punto1.y()))
                        puntoControl1 = QPointF(punto2.x(), punto1.y())
                        path.quadTo(puntoControl1, QPointF(punto2.x(), punto2.y() + controlDibujado2))
                        puntoFinal = path.pointAtPercent(1)
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() + size_arrow, puntoFinal.y() + size_arrow))
                        self.painter.drawLine(puntoFinal, QPointF(puntoFinal.x() - size_arrow, puntoFinal.y() + size_arrow))
                    self.painter.drawText(path.pointAtPercent(0.5), str(datosTransicion))
                    self.painter.drawPath(path)
                    if self.transitions_dictionary[int(primerSeleccionado)]:
                        auxiliar_dict = {int(segundoSeleccionado):datosTransicion}
                        self.transitions_dictionary[int(primerSeleccionado)].update(auxiliar_dict)
                    else:
                        self.transitions_dictionary[int(primerSeleccionado)] = {int(segundoSeleccionado):datosTransicion}
                    self.statusBar().setStyleSheet("background-color:green")
                    self.speach("Transicion Dibujada")
                    self.statusBar().showMessage("STATUS:   Transition Drawed!", 2000)
            else:
                self.speach("ERROR Debe ingresar el dato de transicion")
                self.statusBar().showMessage("STATUS:   Debe ingresar el dato de transicion!", 5000)    
        else:
            self.speach("ERROR debe seleccionar dos indices")
            self.statusBar().showMessage("STATUS:   Debe seleccionar dos indices!", 5000)
    def verifyWord(self):
        initialPos = 0
        isMoved = False
        palabraAVerificar = self.textVerifyHolder.displayText()
        print(palabraAVerificar)
        lista_palabra = list(palabraAVerificar)
        print(lista_palabra)
        self.statusBar().setStyleSheet("background-color:red")
        if palabraAVerificar != "":
            if self.transitions_dictionary:
                self.speach("Posicion inicial "+str(initialPos))
                print("antes de:", initialPos)
                for item in lista_palabra:
                    print("seccion ",initialPos ," : ", self.transitions_dictionary[initialPos])
                    try:
                        isMoved = False
                        for key, value in self.transitions_dictionary[initialPos].items():
                            if item == value or item in value.split(","):
                                isMoved = True
                                initialPos = key
                        if isMoved:
                            self.speach("Se mueve")
                            print("se mueve")
                            self.speach("Posicion actual"+str(initialPos))
                        else:
                            self.speach("No se mueve")
                            print("no se mueve")
                            break
                    except:
                        self.statusBar().showMessage("STATUS:   Verify error!", 10000) 
                self.speach("Posicion final"+str(initialPos))   
                print("despues de:", initialPos)
                if initialPos not in self.accepted_states_dictionary or isMoved == False:
                    self.statusBar().showMessage("STATUS:   Invalid!", 10000)
                else: 
                    self.statusBar().setStyleSheet("background-color:green")
                    self.statusBar().showMessage("STATUS:   Valid!", 10000)
            else:
                self.statusBar().showMessage("STATUS:   No hay transiciones!", 10000)
        else:
            self.statusBar().showMessage("STATUS:   Debe ingresar una palabra!", 10000)

    def clearScreen(self):
        "borramos las opciones de los combobox iterando al revés"
        for i in range(len(self.main_dictionary) + 1, 0, -1):
            self.initialState.removeItem(i)
            self.endingState.removeItem(i)
        self.main_dictionary = {0:QPoint(100, 300)}
        self.states_dictionary = {0:QPoint(100, 300)}
        self.accepted_states_dictionary = {}
        self.transitions_dictionary = defaultdict(list)
        self.pixmap.fill(Qt.white)
        self.painter.drawText(self.main_dictionary[0], str(len(self.main_dictionary) - 1))
        self.painter.drawEllipse(self.main_dictionary[0], self.size_inner_circle, self.size_inner_circle)
        puntoFlechaEstadoInicial = QPointF(self.main_dictionary[0].x() - self.size_inner_circle, self.main_dictionary[0].y())
        self.painter.drawLine(puntoFlechaEstadoInicial, QPointF(puntoFlechaEstadoInicial.x() - 45, puntoFlechaEstadoInicial.y()))
        self.painter.drawLine(puntoFlechaEstadoInicial, QPointF(puntoFlechaEstadoInicial.x() - 15, puntoFlechaEstadoInicial.y() - 15))
        self.painter.drawLine(puntoFlechaEstadoInicial, QPointF(puntoFlechaEstadoInicial.x() - 15, puntoFlechaEstadoInicial.y() + 15))
        self.statusBar().setStyleSheet("background-color:green")
        self.statusBar().showMessage("STATUS:   Screen cleared!", 2000)

    def showData(self):
        print("\n\n\tdata\n\n")
        print("main dict: ", self.main_dictionary)
        print("states dict: ", self.states_dictionary)
        print("accepted states dict: ", self.accepted_states_dictionary)
        print("transitions dict: ", self.transitions_dictionary)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyApp()
    sys.exit(app.exec())