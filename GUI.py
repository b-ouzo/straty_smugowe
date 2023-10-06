# -*- coding: utf-8 -*-
"""Main window-style application."""
# TODO unify naming - properties and field names should start with big letter
#   as they do within the PyQt framework
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
    QTransform
)
from PyQt6.QtCore import (
    Qt,
    QDir,
    QPointF,
    QLine,
    QRectF
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image, ImageFilter, ImageOps
import numpy as np


WINDOW_SIZE = 1200

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("App")
        self.resize(WINDOW_SIZE, int(.76*WINDOW_SIZE))

        self._createMenu()
        self._createToolBar()
        self._createFileBrowser()
        self._createStatusBar()
        self._createMainWidget()
        self._createTopBar()
        self._createInterfaceButtons()
        self._createLossePlot()

    def _createMenu(self):
        menu = self.menuBar().addMenu("&Menu")
        menu.addAction("&Exit", self.close)

    def _createFileBrowser(self):
        docked = QDockWidget()
        docked.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        browser = FileBrowserWidget()
        docked.setWidget(browser)
        docked.setWindowTitle("Browse")

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docked)

    def _createTopBar(self):
        docked = QDockWidget()
        docked.setTitleBarWidget(QWidget())
        docked.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.topBar = TopBar()
        docked.setWidget(self.topBar)

        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, docked)

    def _createToolBar(self):
        self.tools = QToolBar()
        self.tools.addAction("Exit", self.close)
        self.addToolBar(self.tools)

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("I'm the Status Bar")
        self.setStatusBar(status)

    def _createMainWidget(self):
        self.generalLayout = QVBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)

        self.workingIm = WorkingImage()
        self.generalLayout.addWidget(self.workingIm)

        self.setCentralWidget(centralWidget)

    def _createInterfaceButtons(self):
        docked = QDockWidget(self)
        docked.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.controlsPanel = ControlsPanel()
        docked.setWidget(self.controlsPanel)
        docked.setWindowTitle("Controls")
        docked.setMaximumWidth(200)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, docked)

    def _createLossePlot(self):
        #TODO:
        # - separate docked widget class that can replace displayed widged
        #   depending on availability of data needed to calculate losses
        docked = QDockWidget(self)
        self.lossesPlot = PlotsWidget()
        docked.setWidget(self.lossesPlot)
        docked.setWindowTitle('Propagation losses plot')
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, docked)

class Scene(QGraphicsScene):
    def __init__(self,):
        super().__init__()

    def mouseMoveEvent(self, event) -> None:
        if isinstance(self.mouseGrabberItem(), QGraphicsLineItem):
            self.mouseGrabberItem().setX(event.scenePos().x())
        else:
            super().mouseMoveEvent(event)

class WorkingImage(QWidget):
    #TODO: open file button in the middle
    #TODO: drag and drop feature
    def __init__(self):
        super().__init__()
        self._image = QImage()
        self._createLabel()
        self._createViewAndScene()

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.view)
        vbox.addWidget(self.label)
        self.setLayout(vbox)

    def _createViewAndScene(self):
        self.scene = Scene()
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(QColor('#F0F0F0'))
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setFrameStyle(0)
        self.view.hide()

    def _createLabel(self):
        self.label = SubstituteLabel('Drop Image Here')

    def _drawSelectionTools(self, xleft=0, xright=0):
        # TODO:
        #   - create class for sidebars
        #   - keep slider positions when new image is loaded
        #   - improve naming, when slider on the left is moved to the right of
        #       the second slider - what then?
        pen = QPen(QColor('#CFBA15'))
        pen.setWidth(10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        boundLeft = self.scene.addLine(0, 0, 0, self.image.height(), pen)
        boundRight = self.scene.addLine(0, 0, 0, self.image.height(), pen)
        # moving the line to wanted position resolves some issue
        # with moving grabbed line
        boundLeft.setX(xleft)
        boundRight.setX(xright)

        boundLeft.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        boundLeft.setParentItem(self.scene.items()[-1])
        boundRight.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        boundRight.setParentItem(self.scene.items()[-1])

    def redrawSelectionTools(self, xleft, xright):
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                self.scene.removeItem(item)
        self._drawSelectionTools(xleft, xright)

    def resizeEvent(self, a0) -> None:
        if not self.image.isNull():
            self.view.fitInView(
                self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
            )
        self.label.resizeEvent(a0)
        super(WorkingImage, self).resizeEvent(a0)

    def clearView(self):
        self.image = QImage()
        if self.label.isHidden():
            self.view.hide()
            self.label.show()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, img):
        self.scene.clear()
        self._image = img
        self.scene.setSceneRect(QRectF(
            QPointF(), self.image.size().toSizeF())
        )
        self.scene.addPixmap(QPixmap.fromImage(img))
        if not self.image.isNull():
            self.view.fitInView(
                self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
            )
        self.redrawSelectionTools(0, self.image.width())
        if self.view.isHidden():
            self.view.show()
            self.label.hide()

    def chooseImage(self):
        filepath, _ = QFileDialog().getOpenFileName(
            self, 'Open Image', filter='*.bmp;*.jpg;*.png'
        )
        return filepath

    def loadImage(self, filepath=None):
        if not filepath:
            filepath = self.chooseImage()
        try:
            self.image = QImage(filepath)
        except Exception as msg:
            self.displayWarning(msg, 'Image failed to load!')

    def invertColors(self):
        try:
            imageCopy = self.image.copy()
            imageCopy.invertPixels()
            self.image = imageCopy
        except Exception as msg:
            self.displayWarning(msg)

    def rotateImage(self):
        try:
            if not self.image.isNull():
                self.image = self.image.transformed(QTransform().rotate(90))
        except Exception as msg:
            self.displayWarning(msg)

    def displayWarning(self, msg, text=''):
        dlg = QMessageBox(
            QMessageBox.Icon.Warning,
            f'{text}',
            f'Something went wrong:\n{msg}',
            QMessageBox.StandardButton.Ok
        )
        dlg.exec()

    def fdasfas(self):
        print('chuj')

class PlotsWidget(QWidget):
    def __init__(self, width=10, hight=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = SubstituteLabel(
            'Load image and select waveguide to calculate loss',
            ls='dashed'
        )
        self.canvas = LossesPlot(width, hight)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hbox.addWidget(self.label)
        hbox.addWidget(self.canvas)
        self.setLayout(hbox)

        self.canvas.hide()

    def drawPlots(self, img, xleft, xright, xstart, xend,
                 wgLength, signal, losses, res, ycenter, yspan, yspanFull):
        self.canvas._drawWaveguideCloseUp(
            img, xleft, xright, xstart, xend, ycenter, yspanFull
        )
        self.canvas._drawBasePlotForCalculations(
            img, wgLength, xleft, xright, xstart, xend, ycenter, yspan
        )
        self.canvas._drawSignalAndLosses(
            signal, losses, res, xleft, xright, wgLength
        )

        if self.canvas.isHidden():
            self.canvas.show()
            self.label.hide()


class SubstituteLabel(QLabel):
    def __init__(self, text, lw=4, ls='solid', c='#aaa', *args, **kwargs):
        borderStyle = '{'+f'border: {lw}px {ls} {c}'+'}'

        super().__init__(*args, **kwargs)
        self.setText(f'\n\n {text} \n\n')
        self.setStyleSheet(f'QLabel{borderStyle}')
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )


class LossesPlot(FigureCanvasQTAgg):
    #TODO: additional notes
    # - show/hide matplotlib controls option when docked (in menu)
    # - automatically show matplotlib controls when undocked
    # - what about size?
    # - plot formating options (colors and stuff)


    def __init__(self, width=10, hight=3):
        self._fig, (self._ax1, self._ax2, self._ax3) = plt.subplots(
            3, 1, tight_layout=True, figsize=(width, hight)
        )
        super(LossesPlot, self).__init__(self._fig)
        self._setAxesCosmetics()

    def _drawWaveguideCloseUp(
            self, img, xleft, xright, xstart, xend, ycenter, yspanFull
    ):
        xsize, _ = img.size
        fullWaveguideBox = (
            0, ycenter - yspanFull,
            xsize, ycenter + yspanFull
        )
        wgImgCropped = img.crop(fullWaveguideBox)

        self._ax1.imshow(
            ImageOps.invert(wgImgCropped),
            cmap=mpl.colormaps['gray']
        )
        self._ax1.axvspan(xleft, xright, alpha=.15, color='red')
        self._ax1.axvline(xstart, color='red', ls='--')
        self._ax1.axvline(xend, color='red', ls='--')


    def _drawBasePlotForCalculations(
            self, img, wgLength, xleft, xright, xstart, xend, ycenter, yspan,
    ):
        croppedWaveguideBox = (
            round(xstart + wgLength * xleft), ycenter - yspan,
            round(xend + wgLength * xright), ycenter + yspan
        )
        wgImgCropped = img.crop(croppedWaveguideBox).filter(
            ImageFilter.GaussianBlur
        )

        self._ax2.imshow(
            ImageOps.invert(wgImgCropped),
            cmap=mpl.colormaps['gray']
        )


    def _drawSignalAndLosses(self, signal, losses, res, xleft, xright, wgLength):
        def lin(x): return res.slope * x + res.intercept
        xvals = np.linspace(xleft*wgLength, xright*wgLength, signal.size)
        self._ax3.scatter(xvals, signal, marker='.', c='r', ls='')
        self._ax3.plot(xvals, lin(xvals), ls='--', c='k', lw=1.5)
        self._ax3.set_xlim((xleft * wgLength, xright * wgLength))
        self._ax3.text(
            .01, .95,
            f"Propagation loss: {losses :.2f} dB/cm",
            transform=self._ax3.transAxes,
            va='top'
        )

    def _setAxesCosmetics(self):
        self._ax1.set_xticks(())
        self._ax1.set_yticks(())
        self._ax2.set_xticks(())
        self._ax2.set_yticks(())
        self._ax3.set_xlabel("Distance [cm]")
        self._ax3.set_ylabel("Signal level [a.u.]")

    def clearPlots(self):
        self._ax1.clear()
        self._ax2.clear()
        self._ax3.clear()

    def updatePlots(self, *args, **kwargs):
        '''
        Upadates plots using given args and kwargs of drawPlots function
        '''
        self.clearPlots()
        self.drawPlots(*args, **kwargs)

    def getFigure(self, withAxes=False):
        return self._fig, (self._ax1, self._ax2, self._ax3) if withAxes\
            else self._fig

class FileBrowserWidget(QWidget):
    #TODO: set proper initial directory
    #TODO: implement functionalities - drag and drop, double click to open
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        h_layout = QHBoxLayout()
        self.setLayout(h_layout)
        self.treeview = QTreeView()
        h_layout.addWidget(self.treeview)

        path = QDir.currentPath()

        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(path)
        self.dirModel.setFilter(
            QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files
        )
        self.treeview.setModel(self.dirModel)
        self.treeview.setRootIndex(self.dirModel.index(path))

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        barLayout = QHBoxLayout()
        self.setLayout(barLayout)

        browseButton = QPushButton('Browse')
        pixmapi = QStyle.StandardPixmap.SP_DirOpenIcon
        icon = self.style().standardIcon(pixmapi)
        browseButton.setIcon(icon)
        barLayout.addWidget(browseButton)
        currentWD = QLineEdit()
        currentWD.setText(f'{QDir.currentPath()}')
        barLayout.addWidget(currentWD)

class ControlsPanel(QWidget):
    #TODO:
    # - grayscale checkbutton (automatically checked if img is in grayscale)
    # - save data opens dialog window when user can choose what data save?
    # - update edges positions when sliders positions change
    def __init__(self):
        super().__init__()
        self.buttonsAndLabels = dict(
            buttonLoadImage = QPushButton('Load Image'),
            buttonRotateImage = QPushButton('Rotate Image'),
            checkBoxInvertColors = QCheckBox('Invert colors'),
            checkBoxAutoSelection = QCheckBox('Auto-selection'),
            buttonCancelSelection = QPushButton('Cancel selection'),
            buttonDrawWaveguideAxis = QPushButton('Draw waveguide axis'),
            editLineSelectionInfo = QWidget(),
            labelScaling = QLabel('Scaling'),
            buttonFullWaveguideSelect = QRadioButton('Full waveguide length'),
            buttonPartWaveguideSelect = QRadioButton('Waveguide section length'),
            editLineScale = QLineEdit(),
            labelPlot = QLabel('Plot'),
            buttonSave = QPushButton('Save'),
            buttonSaveAs = QPushButton('Save as...'),
            labelData = QLabel('Raw data'),
            buttonSaveData = QPushButton('Save data'),
            buttonSaveDataAs = QPushButton('Save data as...')
        )

        ### additional controls customization
        self.buttonsAndLabels['editLineScale'].setPlaceholderText(
            'Waveguide length [cm]'
        )
        self.buttonsAndLabels['editLineScale'].setText('1.83')

        selectionWidthLayout = QFormLayout()
        selectionWidthLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        selectionWidthLayout.addRow('Selection width [px]:', QLineEdit('20'))
        selectionWidthLayout.addRow('Left edge pos. [px]:', QLineEdit())
        selectionWidthLayout.addRow('Right edge pos. [px]:', QLineEdit())
        selectionWidthLayout.addRow('Signal starts at [0-1]:', QLineEdit())
        selectionWidthLayout.addRow('Signal ends at [0-1]:', QLineEdit())
        selectionWidthLayout.itemAt(1).widget().setMaximumWidth(50)
        selectionWidthLayout.itemAt(7).widget().setText('0')
        selectionWidthLayout.itemAt(9).widget().setText('1')
        self.buttonsAndLabels['editLineSelectionInfo']\
            .setLayout(selectionWidthLayout)

        self.buttonsAndLabels['buttonFullWaveguideSelect'].setChecked(True)
        self.buttonsAndLabels['checkBoxAutoSelection'].setChecked(True)

        buttonsLayout = QVBoxLayout()
        buttonsLayout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )
        self.setLayout(buttonsLayout)
        for key, widget in self.buttonsAndLabels.items():
            buttonsLayout.addWidget(widget)
