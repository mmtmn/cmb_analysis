import matplotlib
import numpy as np
from astropy.coordinates import CartesianRepresentation
import healpy.projaxes as PA
import healpy.rotator as R

from . import pixfunc

def vec2pix(res, x, y, z):
    c = CartesianRepresentation(x, y, z)
    return pixfunc._uv2pix(c, res=res)

class QcGnomonicAxes(PA.GnomonicAxes):
    def projmap(self, map, **kwds):
        res = pixfunc.npix2res(pixfunc.get_map_size(map))
        f = lambda x, y, z: vec2pix(res, x, y, z)
        xsize = kwds.pop("xsize", 200)
        ysize = kwds.pop("ysize", None)
        reso = kwds.pop("reso", 1.5)
        return super(QcGnomonicAxes, self).projmap(
            map, f, xsize=xsize, ysize=ysize, reso=reso, **kwds
        )

class QcMollweideAxes(PA.MollweideAxes):
    def projmap(self, map, **kwds):
        res = pixfunc.npix2res(pixfunc.get_map_size(map))
        f = lambda x, y, z: vec2pix(res, x, y, z)
        return super(QcMollweideAxes, self).projmap(map, f, **kwds)

    def projquiver(self, *args, **kwds):
        """projquiver is a wrapper around :func:`matplotlib.Axes.quiver` to take
        into account the spherical projection.

        You can call this function as::

           projquiver([X, Y], U, V, [C], **kw)
           projquiver([theta, phi], mag, ang, [C], **kw)

        Parameters
        ----------

        Notes
        -----
        Other keywords are transmitted to :func:`matplotlib.Axes.quiver`

        See Also
        --------
        projplot, projscatter, projtext
        """

        '''
        Qmap = args[0][0]
        Umap = args[0][1]

        npix_in = len(Qmap)
        nside_in = pixfunc.npix2nside(npix_in)

        Qmap = pixfunc.ud_grade(Qmap, nside)
        Umap = pixfunc.ud_grade(Umap, nside)

        mag = np.sqrt(Qmap**2 + Umap**2)
        ang = np.arctan2(Umap, Qmap) / 2.0

        max_mag = np.max(mag)
        mag /= max_mag

        npix = H.nside2npix(nside)
        pix = np.arange(npix)

        theta, phi = pixfunc.pix2ang(nside, pix)
        '''

        #Work on input signature
        c = None
        if len(args) < 2:
            raise ValueError("Not enough arguments given")
        if len(args) == 2:
            mag, ang = np.asarray(args[0]), np.asarray(args[1])
            raise ValueError("Not calculating theta, phi yet")
        elif len(args) == 4:
            theta, phi = np.asarray(args[0]), np.asarray(args[1])
            mag, ang = np.asarray(args[2]), np.asarray(args[3])
        elif len(args) == 5:
            theta, phi = np.asarray(args[0]), np.asarray(args[1])
            mag, ang = np.asarray(args[2]), np.asarray(args[3])
            c = np.asarray(args[4])
        else:
            raise TypeError("Wrong number of arguments given")

        save_input_data = hasattr(self.figure, "zoomtool")
        if save_input_data:
            input_data = (theta, phi, mag, ang, args, kwds.copy())

        rot = kwds.pop("rot", None)
        if rot is not None:
            rot = np.array(np.atleast_1d(rot), copy=1)
            rot.resize(3)
            rot[1] = rot[1] - 90.

        coord = self.proj.mkcoord(kwds.pop("coord", None))[::-1]
        lonlat = kwds.pop("lonlat", False)
    
        vec = R.dir2vec(theta, phi, lonlat=lonlat)
        vec = (R.Rotator(rot=rot, coord=coord, eulertype="Y")).I(vec)
        x, y = self.proj.vec2xy(vec, direct=kwds.pop("direct", False))
   
        lat = np.pi/2 - theta
        lon = np.pi - phi

        ang_off = -np.pi/2*np.sin(lat)*np.sin(lon)
    
        #ang_off = np.zeros_like(ang)

        u = 1e-10*mag*np.cos(ang + ang_off)
        v = 1e-10*mag*np.sin(ang + ang_off)

        #x = np.linspace(-2.0, 2.0, num=10)
        #y = np.zeros_like(x)
        #u = 1e-5
        #v = 1e-5

        #s = self.quiver(x, y, u, v, c, *args, headwidth=0, width=0.001, pivot='mid', **kwds)
        #s = self.quiver(x, y, u, v, c, *args, headwidth=0, width=0.01, pivot='mid', **kwds)
        if c is not None:
            s = self.quiver(x, y, u, v, c, headwidth=0, width=0.001, pivot='mid', **kwds)
        else:
            s = self.quiver(x, y, u, v, headwidth=0, width=0.001, pivot='mid', **kwds)

        '''
        theta = 0.0
        phi = 0.0
        
        s = self.projtext(theta, phi, 'AA')
        vec = R.dir2vec(theta, phi, lonlat=lonlat)
        vec = (R.Rotator(rot=rot, coord=None, eulertype="Y")).I(vec)
        x, y = self.proj.vec2xy(vec, direct=kwds.pop("direct", False))
        print("TEST:", x, y)
        '''

        if save_input_data:
            if not hasattr(self, "_quiver_data"):
                self._quiver_data = []
            self._quiver_data.append((s, input_data))
        return s
    

class QcCartesianAxes(PA.CartesianAxes):
    def projmap(self, map, nest=False, **kwds):
        res = pixfunc.npix2res(pixfunc.get_map_size(map))
        f = lambda x, y, z: vec2pix(res, x, y, z)
        return super(QcCartesianAxes, self).projmap(map, f, **kwds)

class QcOrthographicAxes(PA.OrthographicAxes):
    def projmap(self, map, nest=False, **kwds):
        res = pixfunc.npix2res(pixfunc.get_map_size(map))
        f = lambda x, y, z: vec2pix(res, x, y, z)
        return super(QcOrthographicAxes, self).projmap(map, f, **kwds)

class QcAzimuthalAxes(PA.AzimuthalAxes):
    def projmap(self, map, nest=False, **kwds):
        res = pixfunc.npix2res(pixfunc.get_map_size(map))
        f = lambda x, y, z: vec2pix(res, x, y, z)
        xsize = kwds.pop("xsize", 800)
        ysize = kwds.pop("ysize", None)
        reso = kwds.pop("reso", 1.5)
        lamb = kwds.pop("lamb", True)
        return super(QcAzimuthalAxes, self).projmap(
            map, f, xsize=xsize, ysize=ysize, reso=reso, lamb=lamb, **kwds
        )

def mollview(
    map=None,
    fig=None,
    rot=None,
    coord=None,
    unit="",
    xsize=800,
    title="Mollweide view",
    min=None,
    max=None,
    flip="astro",
    remove_dip=False,
    remove_mono=False,
    gal_cut=0,
    format="%g",
    format2="%g",
    cbar=True,
    cmap=None,
    badcolor="gray",
    bgcolor="white",
    notext=False,
    norm=None,
    hold=False,
    margins=None,
    sub=None,
    nlocs=2,
    return_projected_map=False,
):
    """Plot a COBE Quadcube map (given as an array) in Mollweide projection.
    
    Parameters
    ----------
    map : float, array-like or None
      An array containing the map, supports masked maps, see the `ma` function.
      If None, will display a blank map, useful for overplotting.
    fig : int or None, optional
      The figure number to use. Default: create a new figure
    rot : scalar or sequence, optional
      Describe the rotation to apply.
      In the form (lon, lat, psi) (unit: degrees) : the point at
      longitude *lon* and latitude *lat* will be at the center. An additional rotation
      of angle *psi* around this direction is applied.
    coord : sequence of character, optional
      Either one of 'G', 'E' or 'C' to describe the coordinate
      system of the map, or a sequence of 2 of these to rotate
      the map from the first to the second coordinate system.
    unit : str, optional
      A text describing the unit of the data. Default: ''
    xsize : int, optional
      The size of the image. Default: 800
    title : str, optional
      The title of the plot. Default: 'Mollweide view'
    min : float, optional
      The minimum range value
    max : float, optional
      The maximum range value
    flip : {'astro', 'geo'}, optional
      Defines the convention of projection : 'astro' (default, east towards left, west towards right)
      or 'geo' (east towards right, west towards left)
    remove_dip : bool, optional
      If :const:`True`, remove the dipole+monopole
    remove_mono : bool, optional
      If :const:`True`, remove the monopole
    gal_cut : float, scalar, optional
      Symmetric galactic cut for the dipole/monopole fit.
      Removes points in latitude range [-gal_cut, +gal_cut]
    format : str, optional
      The format of the scale label. Default: '%g'
    format2 : str, optional
      Format of the pixel value under mouse. Default: '%g'
    cbar : bool, optional
      Display the colorbar. Default: True
    notext : bool, optional
      If True, no text is printed around the map
    norm : {'hist', 'log', None}
      Color normalization, hist= histogram equalized color mapping,
      log= logarithmic color mapping, default: None (linear color mapping)
    cmap : a color map
       The colormap to use (see matplotlib.cm)
    badcolor : str
      Color to use to plot bad values
    bgcolor : str
      Color to use for background
    hold : bool, optional
      If True, replace the current Axes by a MollweideAxes.
      use this if you want to have multiple maps on the same
      figure. Default: False
    sub : int, scalar or sequence, optional
      Use only a zone of the current figure (same syntax as subplot).
      Default: None
    margins : None or sequence, optional
      Either None, or a sequence (left,bottom,right,top)
      giving the margins on left,bottom,right and top
      of the axes. Values are relative to figure (0-1).
      Default: None
    return_projected_map : bool
      if True returns the projected map in a 2d numpy array

    See Also
    --------
    gnomview, cartview, orthview, azeqview
    """
    # Create the figure
    import pylab

    if len(map) == 3:
        Qmap, Umap = map[1], map[2]
        map = map[0]

    # Ensure that the resolution is valid
    res = pixfunc.get_res(map)

    if not (hold or sub):
        f = pylab.figure(fig, figsize=(8.5, 5.4))
        extent = (0.02, 0.05, 0.96, 0.9)
    elif hold:
        f = pylab.gcf()
        left, bottom, right, top = np.array(f.gca().get_position()).ravel()
        extent = (left, bottom, right - left, top - bottom)
        f.delaxes(f.gca())
    else:  # using subplot syntax
        f = pylab.gcf()
        if hasattr(sub, "__len__"):
            nrows, ncols, idx = sub
        else:
            nrows, ncols, idx = sub // 100, (sub % 100) // 10, (sub % 10)
        if idx < 1 or idx > ncols * nrows:
            raise ValueError("Wrong values for sub: %d, %d, %d" % (nrows, ncols, idx))
        c, r = (idx - 1) % ncols, (idx - 1) // ncols
        if not margins:
            margins = (0.01, 0.0, 0.0, 0.02)
        extent = (
            c * 1.0 / ncols + margins[0],
            1.0 - (r + 1) * 1.0 / nrows + margins[1],
            1.0 / ncols - margins[2] - margins[0],
            1.0 / nrows - margins[3] - margins[1],
        )
        extent = (
            extent[0] + margins[0],
            extent[1] + margins[1],
            extent[2] - margins[2] - margins[0],
            extent[3] - margins[3] - margins[1],
        )
        # extent = (c*1./ncols, 1.-(r+1)*1./nrows,1./ncols,1./nrows)
    # f=pylab.figure(fig,figsize=(8.5,5.4))

    # Starting to draw : turn interactive off
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        if map is None:
            map = np.zeros(12) + np.inf
            cbar = False
        #map = pixelfunc.ma_to_array(map)
        ax = QcMollweideAxes(
            f, extent, coord=coord, rot=rot, format=format2, flipconv=flip
        )
        f.add_axes(ax)
        #if remove_dip:
        #    map = pixelfunc.remove_dipole(
        #        map, gal_cut=gal_cut, nest=nest, copy=True, verbose=True
        #    )
        #elif remove_mono:
        #    map = pixelfunc.remove_monopole(
        #        map, gal_cut=gal_cut, nest=nest, copy=True, verbose=True
        #    )
        img = ax.projmap(
            map,
            xsize=xsize,
            coord=coord,
            vmin=min,
            vmax=max,
            cmap=cmap,
            badcolor=badcolor,
            bgcolor=bgcolor,
            norm=norm,
        )

        if 'Qmap' in locals():
            resQ = pixfunc.npix2res(len(Qmap))
            pixQ = np.arange(len(Qmap))
            c = pixfunc.pix2coord(pixQ, res=resQ, coord='G')
            theta = 90.0 - c.b.value
            phi = c.l.value
            #theta, phi = pixfunc.pix2ang(nsideQ, pixQ)

            mag = np.sqrt(Qmap**2 + Umap**2)
            ang = np.arctan2(Umap, Qmap) / 2.0

            mag_max = np.max(mag)
            mag /= mag_max
        
            img = ax.projquiver(theta, phi, mag, ang)
        
        if cbar:
            im = ax.get_images()[0]
            b = im.norm.inverse(np.linspace(0, 1, im.cmap.N + 1))
            v = np.linspace(im.norm.vmin, im.norm.vmax, im.cmap.N)
            if matplotlib.__version__ >= "0.91.0":
                cb = f.colorbar(
                    im,
                    ax=ax,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(nlocs, norm),
                    pad=0.05,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            else:
                # for older matplotlib versions, no ax kwarg
                cb = f.colorbar(
                    im,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(nlocs, norm),
                    pad=0.05,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            cb.solids.set_rasterized(True)
        ax.set_title(title)
        if not notext:
            ax.text(
                0.86,
                0.05,
                ax.proj.coordsysstr,
                fontsize=14,
                fontweight="bold",
                transform=ax.transAxes,
            )
        if cbar:
            cb.ax.text(
                0.5,
                -1.0,
                unit,
                fontsize=14,
                transform=cb.ax.transAxes,
                ha="center",
                va="center",
            )
        f.sca(ax)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
    if return_projected_map:
        return img

def gnomview(
    map=None,
    fig=None,
    rot=None,
    coord=None,
    unit="",
    xsize=200,
    ysize=None,
    reso=1.5,
    title="Gnomonic view",
    remove_dip=False,
    remove_mono=False,
    gal_cut=0,
    min=None,
    max=None,
    flip="astro",
    format="%.3g",
    cbar=True,
    cmap=None,
    badcolor="gray",
    bgcolor="white",
    norm=None,
    hold=False,
    sub=None,
    margins=None,
    notext=False,
    return_projected_map=False,
    no_plot=False,
):
    """Plot a healpix map (given as an array) in Gnomonic projection.

    Parameters
    ----------
    map : array-like
      The map to project, supports masked maps, see the `ma` function.
      If None, use a blank map, useful for
      overplotting.
    fig : None or int, optional
      A figure number. Default: None= create a new figure
    rot : scalar or sequence, optional
      Describe the rotation to apply.
      In the form (lon, lat, psi) (unit: degrees) : the point at
      longitude *lon* and latitude *lat* will be at the center. An additional rotation
      of angle *psi* around this direction is applied.
    coord : sequence of character, optional
      Either one of 'G', 'E' or 'C' to describe the coordinate
      system of the map, or a sequence of 2 of these to rotate
      the map from the first to the second coordinate system.
    unit : str, optional
      A text describing the unit of the data. Default: ''
    xsize : int, optional
      The size of the image. Default: 200
    ysize : None or int, optional
      The size of the image. Default: None= xsize
    reso : float, optional
      Resolution (in arcmin). Default: 1.5 arcmin
    title : str, optional
      The title of the plot. Default: 'Gnomonic view'
    min : float, scalar, optional
      The minimum range value
    max : float, scalar, optional
      The maximum range value
    flip : {'astro', 'geo'}, optional
      Defines the convention of projection : 'astro' (default, east towards left, west towards right)
      or 'geo' (east towards roght, west towards left)
    remove_dip : bool, optional
      If :const:`True`, remove the dipole+monopole
    remove_mono : bool, optional
      If :const:`True`, remove the monopole
    gal_cut : float, scalar, optional
      Symmetric galactic cut for the dipole/monopole fit.
      Removes points in latitude range [-gal_cut, +gal_cut]
    format : str, optional
      The format of the scale label. Default: '%g'
    cmap : a color map
       The colormap to use (see matplotlib.cm)
    badcolor : str
      Color to use to plot bad values
    bgcolor : str
      Color to use for background
    hold : bool, optional
      If True, replace the current Axes by a MollweideAxes.
      use this if you want to have multiple maps on the same
      figure. Default: False
    sub : int or sequence, optional
      Use only a zone of the current figure (same syntax as subplot).
      Default: None
    margins : None or sequence, optional
      Either None, or a sequence (left,bottom,right,top)
      giving the margins on left,bottom,right and top
      of the axes. Values are relative to figure (0-1).
      Default: None
    notext: bool, optional
      If True: do not add resolution info text. Default=False
    return_projected_map : bool, optional
      if True returns the projected map in a 2d numpy array
    no_plot : bool, optional
      if True no figure will be created      

    See Also
    --------
    mollview, cartview, orthview, azeqview
    """
    import pylab

    # Ensure that the res is valid
    res = pixfunc.get_res(map)

    if not (hold or sub):
        f = pylab.figure(fig, figsize=(5.8, 6.4))
        if not margins:
            margins = (0.075, 0.05, 0.075, 0.05)
        extent = (0.0, 0.0, 1.0, 1.0)
    elif hold:
        f = pylab.gcf()
        left, bottom, right, top = np.array(pylab.gca().get_position()).ravel()
        if not margins:
            margins = (0.0, 0.0, 0.0, 0.0)
        extent = (left, bottom, right - left, top - bottom)
        f.delaxes(pylab.gca())
    else:  # using subplot syntax
        f = pylab.gcf()
        if hasattr(sub, "__len__"):
            nrows, ncols, idx = sub
        else:
            nrows, ncols, idx = sub // 100, (sub % 100) // 10, (sub % 10)
        if idx < 1 or idx > ncols * nrows:
            raise ValueError("Wrong values for sub: %d, %d, %d" % (nrows, ncols, idx))
        c, r = (idx - 1) % ncols, (idx - 1) // ncols
        if not margins:
            margins = (0.01, 0.0, 0.0, 0.02)
        extent = (
            c * 1.0 / ncols + margins[0],
            1.0 - (r + 1) * 1.0 / nrows + margins[1],
            1.0 / ncols - margins[2] - margins[0],
            1.0 / nrows - margins[3] - margins[1],
        )
    extent = (
        extent[0] + margins[0],
        extent[1] + margins[1],
        extent[2] - margins[2] - margins[0],
        extent[3] - margins[3] - margins[1],
    )
    # f=pylab.figure(fig,figsize=(5.5,6))

    # Starting to draw : turn interactive off
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        if map is None:
            map = np.zeros(12) + np.inf
            cbar = False
        #map = pixelfunc.ma_to_array(map)
        ax = QcGnomonicAxes(
            f, extent, coord=coord, rot=rot, format=format, flipconv=flip
        )
        f.add_axes(ax)
        #if remove_dip:
        #    map = pixelfunc.remove_dipole(map, gal_cut=gal_cut, copy=True)
        #elif remove_mono:
        #    map = pixelfunc.remove_monopole(map, gal_cut=gal_cut, copy=True)
        img = ax.projmap(
            map,
            coord=coord,
            vmin=min,
            vmax=max,
            xsize=xsize,
            ysize=ysize,
            reso=reso,
            cmap=cmap,
            norm=norm,
            badcolor=badcolor,
            bgcolor=bgcolor,
        )
        if cbar:
            im = ax.get_images()[0]
            b = im.norm.inverse(np.linspace(0, 1, im.cmap.N + 1))
            v = np.linspace(im.norm.vmin, im.norm.vmax, im.cmap.N)
            if matplotlib.__version__ >= "0.91.0":
                cb = f.colorbar(
                    im,
                    ax=ax,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.08,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            else:
                cb = f.colorbar(
                    im,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.08,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            cb.solids.set_rasterized(True)
        ax.set_title(title)
        if not notext:
            ax.text(
                -0.07,
                0.02,
                "%g '/pix,   %dx%d pix"
                % (
                    ax.proj.arrayinfo["reso"],
                    ax.proj.arrayinfo["xsize"],
                    ax.proj.arrayinfo["ysize"],
                ),
                fontsize=12,
                verticalalignment="bottom",
                transform=ax.transAxes,
                rotation=90,
            )
            ax.text(
                -0.07,
                0.6,
                ax.proj.coordsysstr,
                fontsize=14,
                fontweight="bold",
                rotation=90,
                transform=ax.transAxes,
            )
            lon, lat = np.around(ax.proj.get_center(lonlat=True), ax._coordprec)
            ax.text(
                0.5,
                -0.03,
                "(%g,%g)" % (lon, lat),
                verticalalignment="center",
                horizontalalignment="center",
                transform=ax.transAxes,
            )
        if cbar:
            cb.ax.text(
                1.05,
                0.30,
                unit,
                fontsize=14,
                fontweight="bold",
                transform=cb.ax.transAxes,
                ha="left",
                va="center",
            )
        f.sca(ax)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
        if no_plot:
            pylab.close(f)
            f.clf()
            ax.cla()
    if return_projected_map:
        return img

def cartview(
    map=None,
    fig=None,
    rot=None,
    zat=None,
    coord=None,
    unit="",
    xsize=800,
    ysize=None,
    lonra=None,
    latra=None,
    title="Cartesian view",
    remove_dip=False,
    remove_mono=False,
    gal_cut=0,
    min=None,
    max=None,
    flip="astro",
    format="%.3g",
    cbar=True,
    cmap=None,
    badcolor="gray",
    bgcolor="white",
    norm=None,
    aspect=None,
    hold=False,
    sub=None,
    margins=None,
    notext=False,
    return_projected_map=False,
):
    """Plot a healpix map (given as an array) in Cartesian projection.

    Parameters
    ----------
    map : float, array-like or None
      An array containing the map, 
      supports masked maps, see the `ma` function.
      If None, will display a blank map, useful for overplotting.
    fig : int or None, optional
      The figure number to use. Default: create a new figure
    rot : scalar or sequence, optional
      Describe the rotation to apply.
      In the form (lon, lat, psi) (unit: degrees) : the point at
      longitude *lon* and latitude *lat* will be at the center. An additional rotation
      of angle *psi* around this direction is applied.
    coord : sequence of character, optional
      Either one of 'G', 'E' or 'C' to describe the coordinate
      system of the map, or a sequence of 2 of these to rotate
      the map from the first to the second coordinate system.
    unit : str, optional
      A text describing the unit of the data. Default: ''
    xsize : int, optional
      The size of the image. Default: 800
    lonra : sequence, optional
      Range in longitude. Default: [-180,180]
    latra : sequence, optional
      Range in latitude. Default: [-90,90]
    title : str, optional
      The title of the plot. Default: 'Mollweide view'
    min : float, optional
      The minimum range value
    max : float, optional
      The maximum range value
    flip : {'astro', 'geo'}, optional
      Defines the convention of projection : 'astro' (default, east towards left, west towards right)
      or 'geo' (east towards roght, west towards left)
    remove_dip : bool, optional
      If :const:`True`, remove the dipole+monopole
    remove_mono : bool, optional
      If :const:`True`, remove the monopole
    gal_cut : float, scalar, optional
      Symmetric galactic cut for the dipole/monopole fit.
      Removes points in latitude range [-gal_cut, +gal_cut]
    format : str, optional
      The format of the scale label. Default: '%g'
    cbar : bool, optional
      Display the colorbar. Default: True
    notext : bool, optional
      If True, no text is printed around the map
    norm : {'hist', 'log', None}, optional
      Color normalization, hist= histogram equalized color mapping,
      log= logarithmic color mapping, default: None (linear color mapping)
    cmap : a color map
       The colormap to use (see matplotlib.cm)
    badcolor : str
      Color to use to plot bad values
    bgcolor : str
      Color to use for background
    hold : bool, optional
      If True, replace the current Axes by a CartesianAxes.
      use this if you want to have multiple maps on the same
      figure. Default: False
    sub : int, scalar or sequence, optional
      Use only a zone of the current figure (same syntax as subplot).
      Default: None
    margins : None or sequence, optional
      Either None, or a sequence (left,bottom,right,top)
      giving the margins on left,bottom,right and top
      of the axes. Values are relative to figure (0-1).
      Default: None
    return_projected_map : bool
      if True returns the projected map in a 2d numpy array

    See Also
    --------
    mollview, gnomview, orthview, azeqview
    """
    import pylab

    # Ensure that the nside is valid
    res = pixfunc.get_res(map)

    if not (hold or sub):
        f = pylab.figure(fig, figsize=(8.5, 5.4))
        if not margins:
            margins = (0.075, 0.05, 0.075, 0.05)
        extent = (0.0, 0.0, 1.0, 1.0)
    elif hold:
        f = pylab.gcf()
        left, bottom, right, top = np.array(pylab.gca().get_position()).ravel()
        if not margins:
            margins = (0.0, 0.0, 0.0, 0.0)
        extent = (left, bottom, right - left, top - bottom)
        f.delaxes(pylab.gca())
    else:  # using subplot syntax
        f = pylab.gcf()
        if hasattr(sub, "__len__"):
            nrows, ncols, idx = sub
        else:
            nrows, ncols, idx = sub // 100, (sub % 100) // 10, (sub % 10)
        if idx < 1 or idx > ncols * nrows:
            raise ValueError("Wrong values for sub: %d, %d, %d" % (nrows, ncols, idx))
        c, r = (idx - 1) % ncols, (idx - 1) // ncols
        if not margins:
            margins = (0.01, 0.0, 0.0, 0.02)
        extent = (
            c * 1.0 / ncols + margins[0],
            1.0 - (r + 1) * 1.0 / nrows + margins[1],
            1.0 / ncols - margins[2] - margins[0],
            1.0 / nrows - margins[3] - margins[1],
        )
    extent = (
        extent[0] + margins[0],
        extent[1] + margins[1],
        extent[2] - margins[2] - margins[0],
        extent[3] - margins[3] - margins[1],
    )

    # f=pylab.figure(fig,figsize=(5.5,6))
    # Starting to draw : turn interactive off
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        if map is None:
            map = np.zeros(12) + np.inf
            cbar = False
        #map = pixelfunc.ma_to_array(map)
        if zat and rot:
            raise ValueError("Only give rot or zat, not both")
        if zat:
            rot = np.array(zat, dtype=np.float64)
            rot.resize(3)
            rot[1] -= 90
        ax = QcCartesianAxes(
            f, extent, coord=coord, rot=rot, format=format, flipconv=flip
        )
        f.add_axes(ax)
        #if remove_dip:
        #    map = pixelfunc.remove_dipole(map, gal_cut=gal_cut, copy=True)
        #elif remove_mono:
        #    map = pixelfunc.remove_monopole(map, gal_cut=gal_cut, copy=True)
        img = ax.projmap(
            map,
            coord=coord,
            vmin=min,
            vmax=max,
            xsize=xsize,
            ysize=ysize,
            lonra=lonra,
            latra=latra,
            cmap=cmap,
            badcolor=badcolor,
            bgcolor=bgcolor,
            norm=norm,
            aspect=aspect,
        )
        if cbar:
            im = ax.get_images()[0]
            b = im.norm.inverse(np.linspace(0, 1, im.cmap.N + 1))
            v = np.linspace(im.norm.vmin, im.norm.vmax, im.cmap.N)
            if matplotlib.__version__ >= "0.91.0":
                cb = f.colorbar(
                    im,
                    ax=ax,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.08,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            else:
                cb = f.colorbar(
                    im,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.08,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            cb.solids.set_rasterized(True)
        ax.set_title(title)
        if not notext:
            ax.text(
                -0.07,
                0.6,
                ax.proj.coordsysstr,
                fontsize=14,
                fontweight="bold",
                rotation=90,
                transform=ax.transAxes,
            )
        if cbar:
            cb.ax.text(
                1.05,
                0.30,
                unit,
                fontsize=14,
                fontweight="bold",
                transform=cb.ax.transAxes,
                ha="left",
                va="center",
            )
        f.sca(ax)
    finally:
        if wasinteractive:
            pylab.ion()
            pylab.draw()
            # pylab.show()
    if return_projected_map:
        return img


def orthview(
    map=None,
    fig=None,
    rot=None,
    coord=None,
    unit="",
    xsize=800,
    half_sky=False,
    title="Orthographic view",
    min=None,
    max=None,
    flip="astro",
    remove_dip=False,
    remove_mono=False,
    gal_cut=0,
    format="%g",
    format2="%g",
    cbar=True,
    cmap=None,
    badcolor="gray",
    bgcolor="white",
    notext=False,
    norm=None,
    hold=False,
    margins=None,
    sub=None,
    return_projected_map=False,
):
    """Plot a healpix map (given as an array) in Orthographic projection.
    
    Parameters
    ----------
    map : float, array-like or None
      An array containing the map.
      If None, will display a blank map, useful for overplotting.
    fig : int or None, optional
      The figure number to use. Default: create a new figure
    rot : scalar or sequence, optional
      Describe the rotation to apply.
      In the form (lon, lat, psi) (unit: degrees) : the point at
      longitude *lon* and latitude *lat* will be at the center. An additional rotation
      of angle *psi* around this direction is applied.
    coord : sequence of character, optional
      Either one of 'G', 'E' or 'C' to describe the coordinate
      system of the map, or a sequence of 2 of these to rotate
      the map from the first to the second coordinate system.
    half_sky : bool, optional
      Plot only one side of the sphere. Default: False
    unit : str, optional
      A text describing the unit of the data. Default: ''
    xsize : int, optional
      The size of the image. Default: 800
    title : str, optional
      The title of the plot. Default: 'Orthographic view'
    min : float, optional
      The minimum range value
    max : float, optional
      The maximum range value
    flip : {'astro', 'geo'}, optional
      Defines the convention of projection : 'astro' (default, east towards left, west towards right)
      or 'geo' (east towards roght, west towards left)
    remove_dip : bool, optional
      If :const:`True`, remove the dipole+monopole
    remove_mono : bool, optional
      If :const:`True`, remove the monopole
    gal_cut : float, scalar, optional
      Symmetric galactic cut for the dipole/monopole fit.
      Removes points in latitude range [-gal_cut, +gal_cut]
    format : str, optional
      The format of the scale label. Default: '%g'
    format2 : str, optional
      Format of the pixel value under mouse. Default: '%g'
    cbar : bool, optional
      Display the colorbar. Default: True
    notext : bool, optional
      If True, no text is printed around the map
    norm : {'hist', 'log', None}
      Color normalization, hist= histogram equalized color mapping,
      log= logarithmic color mapping, default: None (linear color mapping)
    cmap : a color map
       The colormap to use (see matplotlib.cm)
    badcolor : str
      Color to use to plot bad values
    bgcolor : str
      Color to use for background
    hold : bool, optional
      If True, replace the current Axes by an OrthographicAxes.
      use this if you want to have multiple maps on the same
      figure. Default: False
    sub : int, scalar or sequence, optional
      Use only a zone of the current figure (same syntax as subplot).
      Default: None
    margins : None or sequence, optional
      Either None, or a sequence (left,bottom,right,top)
      giving the margins on left,bottom,right and top
      of the axes. Values are relative to figure (0-1).
      Default: None
    return_projected_map : bool
      if True returns the projected map in a 2d numpy array
    
    See Also
    --------
    mollview, gnomview, cartview, azeqview
    """
    # Create the figure
    import pylab

    # Ensure that the nside is valid
    res = pixfunc.get_res(map)

    if not (hold or sub):
        f = pylab.figure(fig, figsize=(8.5, 5.4))
        extent = (0.02, 0.05, 0.96, 0.9)
    elif hold:
        f = pylab.gcf()
        left, bottom, right, top = np.array(f.gca().get_position()).ravel()
        extent = (left, bottom, right - left, top - bottom)
        f.delaxes(f.gca())
    else:  # using subplot syntax
        f = pylab.gcf()
        if hasattr(sub, "__len__"):
            nrows, ncols, idx = sub
        else:
            nrows, ncols, idx = sub // 100, (sub % 100) // 10, (sub % 10)
        if idx < 1 or idx > ncols * nrows:
            raise ValueError("Wrong values for sub: %d, %d, %d" % (nrows, ncols, idx))
        c, r = (idx - 1) % ncols, (idx - 1) // ncols
        if not margins:
            margins = (0.01, 0.0, 0.0, 0.02)
        extent = (
            c * 1.0 / ncols + margins[0],
            1.0 - (r + 1) * 1.0 / nrows + margins[1],
            1.0 / ncols - margins[2] - margins[0],
            1.0 / nrows - margins[3] - margins[1],
        )
        extent = (
            extent[0] + margins[0],
            extent[1] + margins[1],
            extent[2] - margins[2] - margins[0],
            extent[3] - margins[3] - margins[1],
        )
        # extent = (c*1./ncols, 1.-(r+1)*1./nrows,1./ncols,1./nrows)
    # f=pylab.figure(fig,figsize=(8.5,5.4))

    # Starting to draw : turn interactive off
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        if map is None:
            map = np.zeros(12) + np.inf
            cbar = False
        ax = QcOrthographicAxes(
            f, extent, coord=coord, rot=rot, format=format2, flipconv=flip
        )
        f.add_axes(ax)
        #if remove_dip:
        #    map = pixelfunc.remove_dipole(
        #        map, gal_cut=gal_cut, nest=nest, copy=True, verbose=True
        #    )
        #elif remove_mono:
        #    map = pixelfunc.remove_monopole(
        #        map, gal_cut=gal_cut, nest=nest, copy=True, verbose=True
        #    )
        img = ax.projmap(
            map,
            xsize=xsize,
            half_sky=half_sky,
            coord=coord,
            vmin=min,
            vmax=max,
            cmap=cmap,
            badcolor=badcolor,
            bgcolor=bgcolor,
            norm=norm,
        )
        if cbar:
            im = ax.get_images()[0]
            b = im.norm.inverse(np.linspace(0, 1, im.cmap.N + 1))
            v = np.linspace(im.norm.vmin, im.norm.vmax, im.cmap.N)
            if matplotlib.__version__ >= "0.91.0":
                cb = f.colorbar(
                    im,
                    ax=ax,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.05,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            else:
                # for older matplotlib versions, no ax kwarg
                cb = f.colorbar(
                    im,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.05,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            cb.solids.set_rasterized(True)
        ax.set_title(title)
        if not notext:
            ax.text(
                0.86,
                0.05,
                ax.proj.coordsysstr,
                fontsize=14,
                fontweight="bold",
                transform=ax.transAxes,
            )
        if cbar:
            cb.ax.text(
                0.5,
                -1.0,
                unit,
                fontsize=14,
                transform=cb.ax.transAxes,
                ha="center",
                va="center",
            )
        f.sca(ax)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
    if return_projected_map:
        return img


def azeqview(
    map=None,
    fig=None,
    rot=None,
    zat=None,
    coord=None,
    unit="",
    xsize=800,
    ysize=None,
    reso=1.5,
    lamb=False,
    half_sky=False,
    title=None,
    remove_dip=False,
    remove_mono=False,
    gal_cut=0,
    min=None,
    max=None,
    flip="astro",
    format="%.3g",
    cbar=True,
    cmap=None,
    badcolor="gray",
    bgcolor="white",
    norm=None,
    aspect=None,
    hold=False,
    sub=None,
    margins=None,
    notext=False,
    return_projected_map=False,
):
    """Plot a healpix map (given as an array) in Azimuthal equidistant projection
    or Lambert azimuthal equal-area projection.

    Parameters
    ----------
    map : float, array-like or None
      An array containing the map,
      supports masked maps, see the `ma` function.
      If None, will display a blank map, useful for overplotting.
    fig : int or None, optional
      The figure number to use. Default: create a new figure
    rot : scalar or sequence, optional
      Describe the rotation to apply.
      In the form (lon, lat, psi) (unit: degrees) : the point at
      longitude *lon* and latitude *lat* will be at the center. An additional rotation
      of angle *psi* around this direction is applied.
    coord : sequence of character, optional
      Either one of 'G', 'E' or 'C' to describe the coordinate
      system of the map, or a sequence of 2 of these to rotate
      the map from the first to the second coordinate system.
    unit : str, optional
      A text describing the unit of the data. Default: ''
    xsize : int, optional
      The size of the image. Default: 800
    ysize : None or int, optional
      The size of the image. Default: None= xsize
    reso : float, optional
      Resolution (in arcmin). Default: 1.5 arcmin
    lamb : bool, optional
      If True, plot Lambert azimuthal equal area instead of azimuthal
      equidistant. Default: False (az equidistant)
    half_sky : bool, optional
      Plot only one side of the sphere. Default: False
    title : str, optional
      The title of the plot. Default: 'Azimuthal equidistant view'
      or 'Lambert azimuthal equal-area view' (if lamb is True)
    min : float, optional
      The minimum range value
    max : float, optional
      The maximum range value
    flip : {'astro', 'geo'}, optional
      Defines the convention of projection : 'astro' (default, east towards left, west towards right)
      or 'geo' (east towards roght, west towards left)
    remove_dip : bool, optional
      If :const:`True`, remove the dipole+monopole
    remove_mono : bool, optional
      If :const:`True`, remove the monopole
    gal_cut : float, scalar, optional
      Symmetric galactic cut for the dipole/monopole fit.
      Removes points in latitude range [-gal_cut, +gal_cut]
    format : str, optional
      The format of the scale label. Default: '%g'
    cbar : bool, optional
      Display the colorbar. Default: True
    notext : bool, optional
      If True, no text is printed around the map
    norm : {'hist', 'log', None}
      Color normalization, hist= histogram equalized color mapping,
      log= logarithmic color mapping, default: None (linear color mapping)
    cmap : a color map
       The colormap to use (see matplotlib.cm)
    badcolor : str
      Color to use to plot bad values
    bgcolor : str
      Color to use for background
    hold : bool, optional
      If True, replace the current Axes by an Equidistant AzimuthalAxes.
      use this if you want to have multiple maps on the same
      figure. Default: False
    sub : int, scalar or sequence, optional
      Use only a zone of the current figure (same syntax as subplot).
      Default: None
    margins : None or sequence, optional
      Either None, or a sequence (left,bottom,right,top)
      giving the margins on left,bottom,right and top
      of the axes. Values are relative to figure (0-1).
      Default: None
    return_projected_map : bool
      if True returns the projected map in a 2d numpy array

    See Also
    --------
    mollview, gnomview, cartview, orthview
    """
    # Create the figure
    import pylab

    # Ensure that the nside is valid
    res = pixfunc.get_res(map)

    if not (hold or sub):
        f = pylab.figure(fig, figsize=(8.5, 5.4))
        extent = (0.02, 0.05, 0.96, 0.9)
    elif hold:
        f = pylab.gcf()
        left, bottom, right, top = np.array(f.gca().get_position()).ravel()
        extent = (left, bottom, right - left, top - bottom)
        f.delaxes(f.gca())
    else:  # using subplot syntax
        f = pylab.gcf()
        if hasattr(sub, "__len__"):
            nrows, ncols, idx = sub
        else:
            nrows, ncols, idx = sub // 100, (sub % 100) // 10, (sub % 10)
        if idx < 1 or idx > ncols * nrows:
            raise ValueError("Wrong values for sub: %d, %d, %d" % (nrows, ncols, idx))
        c, r = (idx - 1) % ncols, (idx - 1) // ncols
        if not margins:
            margins = (0.01, 0.0, 0.0, 0.02)
        extent = (
            c * 1.0 / ncols + margins[0],
            1.0 - (r + 1) * 1.0 / nrows + margins[1],
            1.0 / ncols - margins[2] - margins[0],
            1.0 / nrows - margins[3] - margins[1],
        )
        extent = (
            extent[0] + margins[0],
            extent[1] + margins[1],
            extent[2] - margins[2] - margins[0],
            extent[3] - margins[3] - margins[1],
        )
        # extent = (c*1./ncols, 1.-(r+1)*1./nrows,1./ncols,1./nrows)
    # f=pylab.figure(fig,figsize=(8.5,5.4))

    # Starting to draw : turn interactive off
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        if map is None:
            map = np.zeros(12) + np.inf
            cbar = False
        ax = QcAzimuthalAxes(
            f, extent, coord=coord, rot=rot, format=format, flipconv=flip
        )
        f.add_axes(ax)
        #if remove_dip:
        #    map = pixelfunc.remove_dipole(
        #        map, gal_cut=gal_cut, nest=nest, copy=True, verbose=True
        #    )
        #elif remove_mono:
        #    map = pixelfunc.remove_monopole(
        #        map, gal_cut=gal_cut, nest=nest, copy=True, verbose=True
        #    )
        img = ax.projmap(
            map,
            xsize=xsize,
            ysize=ysize,
            reso=reso,
            lamb=lamb,
            half_sky=half_sky,
            coord=coord,
            vmin=min,
            vmax=max,
            cmap=cmap,
            badcolor=badcolor,
            bgcolor=bgcolor,
            norm=norm,
        )
        if cbar:
            im = ax.get_images()[0]
            b = im.norm.inverse(np.linspace(0, 1, im.cmap.N + 1))
            v = np.linspace(im.norm.vmin, im.norm.vmax, im.cmap.N)
            if matplotlib.__version__ >= "0.91.0":
                cb = f.colorbar(
                    im,
                    ax=ax,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.05,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            else:
                # for older matplotlib versions, no ax kwarg
                cb = f.colorbar(
                    im,
                    orientation="horizontal",
                    shrink=0.5,
                    aspect=25,
                    ticks=PA.BoundaryLocator(),
                    pad=0.05,
                    fraction=0.1,
                    boundaries=b,
                    values=v,
                    format=format,
                )
            cb.solids.set_rasterized(True)
        if title is None:
            if lamb:
                title = "Lambert azimuthal equal-area view"
            else:
                title = "Azimuthal equidistant view"
        ax.set_title(title)
        if not notext:
            ax.text(
                0.86,
                0.05,
                ax.proj.coordsysstr,
                fontsize=14,
                fontweight="bold",
                transform=ax.transAxes,
            )
        if cbar:
            cb.ax.text(
                0.5,
                -1.0,
                unit,
                fontsize=14,
                transform=cb.ax.transAxes,
                ha="center",
                va="center",
            )
        f.sca(ax)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
    if return_projected_map:
        return img


def graticule(dpar=None, dmer=None, coord=None, local=None, **kwds):
    """Draw a graticule on the current Axes.

    Parameters
    ----------
    dpar, dmer : float, scalars
      Interval in degrees between meridians and between parallels
    coord : {'E', 'G', 'C'}
      The coordinate system of the graticule (make rotation if needed,
      using coordinate system of the map if it is defined).
    local : bool
      If True, draw a local graticule (no rotation is performed, useful for
      a gnomonic view, for example)

    Notes
    -----
    Other keyword parameters will be transmitted to the projplot function.

    See Also
    --------
    delgraticules
    """
    import pylab

    f = pylab.gcf()
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        if len(f.get_axes()) == 0:
            ax = QcMollweideAxes(f, (0.02, 0.05, 0.96, 0.9), coord=coord)
            f.add_axes(ax)
            ax.text(
                0.86,
                0.05,
                ax.proj.coordsysstr,
                fontsize=14,
                fontweight="bold",
                transform=ax.transAxes,
            )
        for ax in f.get_axes():
            if isinstance(ax, PA.SphericalProjAxes):
                ax.graticule(dpar=dpar, dmer=dmer, coord=coord, local=local, **kwds)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()


def delgraticules():
    """Delete all graticules previously created on the Axes.

    See Also
    --------
    graticule
    """
    import pylab

    f = pylab.gcf()
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    try:
        for ax in f.get_axes():
            if isinstance(ax, PA.SphericalProjAxes):
                ax.delgraticules()
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()


def projplot(*args, **kwds):
    import pylab

    f = pylab.gcf()
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    ret = None
    try:
        for ax in f.get_axes():
            if isinstance(ax, PA.SphericalProjAxes):
                ret = ax.projplot(*args, **kwds)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
    return ret


projplot.__doc__ = PA.SphericalProjAxes.projplot.__doc__


def projscatter(*args, **kwds):
    import pylab

    f = pylab.gcf()
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    ret = None
    try:
        for ax in f.get_axes():
            if isinstance(ax, PA.SphericalProjAxes):
                ret = ax.projscatter(*args, **kwds)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
    return ret


projscatter.__doc__ = PA.SphericalProjAxes.projscatter.__doc__


def projtext(*args, **kwds):
    import pylab

    f = pylab.gcf()
    wasinteractive = pylab.isinteractive()
    pylab.ioff()
    ret = None
    try:
        for ax in f.get_axes():
            if isinstance(ax, PA.SphericalProjAxes):
                ret = ax.projtext(*args, **kwds)
    finally:
        pylab.draw()
        if wasinteractive:
            pylab.ion()
            # pylab.show()
    return ret


projtext.__doc__ = PA.SphericalProjAxes.projtext.__doc__
