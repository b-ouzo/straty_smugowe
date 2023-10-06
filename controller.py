import sys
from functools import partial

from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QWidget,
    QDockWidget,
    QTreeView,
    QHBoxLayout,
    QFormLayout,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QRadioButton,
    QCheckBox,
    QLineEdit,
    QStyle,
    QFileDialog,
    QMessageBox,
    QGraphicsScene,
    QGraphicsView,
    QSizePolicy,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsBlurEffect
)
from PyQt6.QtGui import (
    QImage,
    QPixmap,
    QIcon,
    QFileSystemModel,
    QPainter,
    QColor,
    QPen,
)
from PyQt6.QtCore import (
    Qt,
    QDir,
    QPointF,
    QLine
)

class App:
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._connectSignalsAndSlots()
        self._chooseLoadAndCalculate()

    def isAutoSelectionEnabled(self):
        signal = self._view.controlsPanel\
            .buttonsAndLabels['checkBoxAutoSelection'].checkState()
        match signal:
            case 2:
                return True
            case 1:
                return False

    def isSelectionInfoAvailable(self):
        raise NotImplementedError

    def getSelectionData(self):
        try:
            wgLength = self._view.controlsPanel\
                .buttonsAndLabels['editLineScale'].text()
            xstart, xend = sorted([
                item.x() for item in self._view.workingIm.scene.item()
                if isinstance(item, QGraphicsLineItem)
            ])
        except Exception:
            pass

    def _chooseLoadAndCalculate(self):
        '''auxilary function for testing purposes'''
        filepath = self._view.workingIm.chooseImage()
        self._view.workingIm.loadImage(filepath)
        self._model.loadImage(filepath)
        # leftEdgePos, rightEdgePos = sorted(
        #     item.x() for item in self._view.workingIm.scene.item()
        #     if isinstance(item, QGraphicsLineItem)
        # )
        yspan = eval(
            self._view.controlsPanel.buttonsAndLabels['editLineSelectionInfo']\
                .layout().itemAt(1).widget().text()
        )
        signalStartsAt = eval(
            self._view.controlsPanel.buttonsAndLabels['editLineSelectionInfo']\
                .layout().itemAt(7).widget().text()
        )
        signalEndsAt = eval(
            self._view.controlsPanel.buttonsAndLabels['editLineSelectionInfo']\
                .layout().itemAt(9).widget().text()
        )
        wgLength = eval(self._view.controlsPanel.buttonsAndLabels['editLineScale'].text())
        leftEdge, rightEdge, ycenter = self._model.findWaveguidePosition(
            signalStartsAt, signalEndsAt
        )
        results = self._model.calculateLoss(
            filepath, wgLength, xleft=signalStartsAt, xright=signalEndsAt,
            xstart=leftEdge, xend=rightEdge, ycenter=ycenter, yspan=yspan
        )
        signal, losses, res = results

        self._view.lossesPlot.drawPlots(
            self._model.img, xleft=signalStartsAt, xright=signalEndsAt,
            xstart=leftEdge, xend=rightEdge, wgLength=wgLength, ycenter=ycenter,
            signal=signal, losses=losses, res=res, yspan=yspan, yspanFull=80
        )

        sliders = [
            item for item in self._view.workingIm.scene.items()
            if isinstance(item, QGraphicsLineItem)
        ]
        sliders[0].setX(leftEdge)
        sliders[1].setX(rightEdge)


    def _connectSignalsAndSlots(self):
        self._view.controlsPanel.buttonsAndLabels['buttonLoadImage']\
            .clicked.connect(self._chooseLoadAndCalculate)
        self._view.controlsPanel.buttonsAndLabels['buttonRotateImage']\
            .clicked.connect(self._view.workingIm.rotateImage)
        self._view.controlsPanel.buttonsAndLabels['checkBoxInvertColors']\
            .stateChanged.connect(self._view.workingIm.invertColors)

'''controls to connect'''
# checkBoxAutoSelection = QCheckBox('Auto-selection'),
# buttonCancelSelection = QPushButton('Cancel selection'),
# buttonDrawWaveguideAxis = QPushButton('Draw waveguide axis'),
# editLineSelectionWidth = QWidget(),
# labelScaling = QLabel('Scaling'),
# buttonFullWaveguideSelect = QRadioButton('Full waveguide length'),
# buttonPartWaveguideSelect = QRadioButton('Waveguide section length'),
# editLineScale = QLineEdit(),
# labelPlot = QLabel('Plot'),
# buttonSave = QPushButton('Save'),
# buttonSaveAs = QPushButton('Save as...'),
# labelData = QLabel('Raw data'),
# buttonSaveData = QPushButton('Save data'),
# buttonSaveDataAs = QPushButton('Save data as...')