from PIL import Image, ImageFilter, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import linregress



class Model:
    #TODO:
    # - rethink and simplify class methods

    def __init__(self):
        # coefficient required to obtain proper value of propagation loss
        # see: https://doi.org/10.1364/OE.460318 (end part of section 2)
        self.LOSS_COEFF = 4.343
        self.img = None

    def loadImage(self, filepath):
        with Image.open(filepath) as im:
            # convert to B&W
            self.img = im.convert('L')  # to black and white

    def findWaveguidePosition(self, xleft, xright):
        if isinstance(self.img, Image.Image):
            # get image size in pixels
            xsize, ysize = self.img.size
            proj = np.array(self.img).sum(axis=0)
            xstart = proj[:xsize // 2].argmax()
            xend = proj[xsize // 2:].argmax() + xsize // 2
            sample_width_px = xend - xstart
            xleftpx = round(xstart + sample_width_px * xleft)
            xrightpx = round(xstart + sample_width_px * xright)
            area = (xleftpx, 0, xrightpx, ysize)

            cropped = np.array(self.img.crop(area))
            ycenter = cropped.sum(axis=1).argmax()

            return xstart, xend, ycenter
        raise FileNotFoundError('No image found.')

    def calculateLoss(
        self, filePath, wgLength, ycenter=None, xstart=None, xend=None,
        xleft=None, xright=None, yspan=10, autoselection=False
    ):
        '''
        Calculates propagation loss based on file indicated by given filePath.
        Losses are scaled used wgLength arg and based on waveguide part
        described by xleft and xright arguments.

        Args:
            filePath: str or Path object
                Path to desired image.
            wgLength: int, float
                Physical length of the waveguide (or waveguide part) visible
                on the image
            ycenter: int
                Waveguide y position on the image in pixels.
            xstart, xend: int, int
                Postion (in pixels) of sample edges on the picture. If None
                then 1 and horizontal size of the image are set to xstart
                end xend respectively.
            xleft, xright: float, float
                0 to 1 float value indicating left and right margin of
                the waveguide fragment respectively used
                to losses calculations. If None then argument vales are set to
                0 and 1 respectively.
            yspan: int
                Vertical part of the image (in pixels) considered in loss
                calculations.
            autoselection: bool
                whether ycenter, xstart and xend variables should be determined
                automatically

        Returns:
            signal, losses, res: list[ndarray, float, obj]
                Calculated signal, propagation losses in dB/cm
                and linear regression results.
        '''
        # load image and convart to black and white
        self.loadImage(filePath)

        # set defaul values of xleft and xright if at least one is not given
        if not (xleft and xright):
            xleft, xright = 0, 1
        # find wg position automatically if autoselection is on
        # or at least one of the parameters is available
        if autoselection or not (xstart and xend and ycenter):
            wgPosition = self.findWaveguidePosition(xleft, xright)
            ycenter, xstart, xend = wgPosition

        croppedWaveguideBox = (
            round(xstart + wgLength * xleft), ycenter - yspan,
            round(xend + wgLength * xright), ycenter + yspan
        )

        wgImgCropped = self.img.crop(croppedWaveguideBox).filter(
            ImageFilter.GaussianBlur
        )

        signal = np.log(np.array(wgImgCropped).mean(axis=0))
        x = np.linspace(xleft * wgLength, xright * wgLength, signal.size)
        res = linregress(x, signal)
        losses = res.slope * self.LOSS_COEFF

        return signal, losses, res


def calculate_losses(filename, width, xleft, xright):
    FILENAME = filename
    YSPAN = 20  # hight/2 of part of the image containing fragment of the waveguide
    FULL_WG_YSPAN = 80  # hight/2 of part of the image containing whole waveguide
    WIDTH = width  # physical width of the sample [cm]
    XLEFT, XRIGHT = xleft, xright  # sample part used for losses calculations [0-1 val]

    # coefficient required to obtain proper value of propagation loss
    # see: https://doi.org/10.1364/OE.460318 (end part of section 2)
    LOSS_COEFF = 4.343

    with Image.open(filename) as im:
        # convert to B&W
        im = im.convert('L')  # to black and white
        proj = np.array(im).sum(axis=0)

        # calculate scale parameter and rectangle to calculate waveguide y position
        xsize, ysize = im.size
        xstart = proj[:xsize//2].argmax()
        xend = proj[xsize//2:].argmax() + xsize//2
        sample_width_px = xend - xstart
        xleft = round(xstart + sample_width_px * XLEFT)
        xright = round(xstart + sample_width_px * XRIGHT)
        area = (xleft, 0, xright, ysize)

        # calculate y coordinate of waveguide position
        # using cropped image
        cropped = np.array(im.crop(area))
        ycenter = cropped.sum(axis=1).argmax()

        cropped_waveguide_box = (
            xleft, ycenter - YSPAN,
            xright, ycenter + YSPAN
        )
        full_waveguide_box = (
            0, ycenter - FULL_WG_YSPAN,
            xsize, ycenter + FULL_WG_YSPAN
        )

        # crop waveguide from orginal image
        wg_im_cropped = im.crop(cropped_waveguide_box).filter(
            ImageFilter.GaussianBlur)
        full_wg_im = im.crop(full_waveguide_box)

        # calculate propagation loss
        signal = np.log(np.array(wg_im_cropped).mean(axis=0))  # * LOSS_COEFF
        x = np.linspace(XLEFT*WIDTH, XRIGHT*WIDTH, signal.size)
        res = linregress(x, signal)
        def lin(x): return res.slope * x + res.intercept

    '''
    ###############################################################################
    ############################### Plot Figures ##################################
    ###############################################################################
    '''
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, tight_layout=True, figsize=(10, 3))
    ax1.set_ylabel(FILENAME.split('\\')[-1])
    # inverted image containing full length waveguide
    # part used for losses calculations  is highlighted in red
    ax1.imshow(
        ImageOps.invert(full_wg_im),
        cmap=mpl.colormaps['gray']
    )
    ax1.axvspan(xleft, xright, alpha=.15, color='red')
    ax1.axvline(xstart, color='red', ls='--')
    ax1.axvline(xend, color='red', ls='--')
    ax1.set_xticks(())
    ax1.set_yticks(())

    # inverted image of waveguide part used for losses calculations
    ax2.imshow(
        ImageOps.invert(wg_im_cropped),
        cmap=mpl.colormaps['gray']
    )
    ax2.set_xticks(())
    ax2.set_yticks(())

    # losses plot
    ax3.scatter(x, signal, marker='.', c='r', ls='')
    ax3.plot(x, lin(x), ls='--', c='k', lw=1.5)
    ax3.set_xlim((XLEFT*WIDTH, XRIGHT*WIDTH))
    ax3.text(
        .01, .95,
        f"Propagation loss: {res.slope * LOSS_COEFF:.2f} dB/cm",
        transform=ax3.transAxes,
        va='top'
    )
    ax3.set_xlabel("Distance [cm]")
    ax3.set_ylabel("Signal level [a.u.]")
    # fig.savefig(
    #     '.\\'+FILENAME.split('\\')[-2]
    #     +'\\'+FILENAME.split('\\')[-1].split('.')[0]
    #     +'_losses.png',
    #     dpi=300, facecolor='w'
    # )
    plt.show()
