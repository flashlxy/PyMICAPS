import matplotlib.cbook as cbook
import numpy as np


@cbook.deprecated("2.2", alternative="scipy.interpolate.griddata")
def griddata(x, y, z, xi, yi, interp="nn"):
    """
    Interpolates from a nonuniformly spaced grid to some other grid.
    Fits a surface of the form z = f(`x`, `y`) to the data in the
    (usually) nonuniformly spaced vectors (`x`, `y`, `z`), then
    interpolates this surface at the points specified by
    (`xi`, `yi`) to produce `zi`.
    Parameters
    ----------
    x, y, z : 1d array_like
        Coordinates of grid points to interpolate from.
    xi, yi : 1d or 2d array_like
        Coordinates of grid points to interpolate to.
    interp : string key from {'nn', 'linear'}
        Interpolation algorithm, either 'nn' for natural neighbor, or
        'linear' for linear interpolation.
    Returns
    -------
    2d float array
        Array of values interpolated at (`xi`, `yi`) points.  Array
        will be masked is any of (`xi`, `yi`) are outside the convex
        hull of (`x`, `y`).
    Notes
    -----
    If `interp` is 'nn' (the default), uses natural neighbor
    interpolation based on Delaunay triangulation.  This option is
    only available if the mpl_toolkits.natgrid module is installed.
    This can be downloaded from https://github.com/matplotlib/natgrid.
    The (`xi`, `yi`) grid must be regular and monotonically increasing
    in this case.
    If `interp` is 'linear', linear interpolation is used via
    matplotlib.tri.LinearTriInterpolator.
    Instead of using `griddata`, more flexible functionality and other
    interpolation options are available using a
    matplotlib.tri.Triangulation and a matplotlib.tri.TriInterpolator.
    """
    # Check input arguments.
    x = np.asanyarray(x, dtype=np.float64)
    y = np.asanyarray(y, dtype=np.float64)
    z = np.asanyarray(z, dtype=np.float64)
    if x.shape != y.shape or x.shape != z.shape or x.ndim != 1:
        raise ValueError("x, y and z must be equal-length 1-D arrays")

    xi = np.asanyarray(xi, dtype=np.float64)
    yi = np.asanyarray(yi, dtype=np.float64)
    if xi.ndim != yi.ndim:
        raise ValueError("xi and yi must be arrays with the same number of "
                         "dimensions (1 or 2)")
    if xi.ndim == 2 and xi.shape != yi.shape:
        raise ValueError("if xi and yi are 2D arrays, they must have the same "
                         "shape")
    if xi.ndim == 1:
        xi, yi = np.meshgrid(xi, yi)

    if interp == "nn":
        use_nn_interpolation = True
    elif interp == "linear":
        use_nn_interpolation = False
    else:
        raise ValueError("interp keyword must be one of 'linear' (for linear "
                         "interpolation) or 'nn' (for natural neighbor "
                         "interpolation).  Default is 'nn'.")

    # Remove masked points.
    mask = np.ma.getmask(z)
    if mask is not np.ma.nomask:
        x = x.compress(~mask)
        y = y.compress(~mask)
        z = z.compressed()

    if use_nn_interpolation:
        try:
            from mpl_toolkits.natgrid import _natgrid
        except ImportError:
            raise RuntimeError(
                "To use interp='nn' (Natural Neighbor interpolation) in "
                "griddata, natgrid must be installed. Either install it "
                "from http://github.com/matplotlib/natgrid or use "
                "interp='linear' instead.")

        if xi.ndim == 2:
            # natgrid expects 1D xi and yi arrays.
            xi = xi[0, :]
            yi = yi[:, 0]

        # Override default natgrid internal parameters.
        _natgrid.seti(b"ext", 0)
        _natgrid.setr(b"nul", np.nan)

        if np.min(np.diff(xi)) < 0 or np.min(np.diff(yi)) < 0:
            raise ValueError("Output grid defined by xi,yi must be monotone "
                             "increasing")

        # Allocate array for output (buffer will be overwritten by natgridd)
        zi = np.empty((yi.shape[0], xi.shape[0]), np.float64)

        # Natgrid requires each array to be contiguous rather than e.g. a view
        # that is a non-contiguous slice of another array.  Use numpy.require
        # to deal with this, which will copy if necessary.
        x = np.require(x, requirements=["C"])
        y = np.require(y, requirements=["C"])
        z = np.require(z, requirements=["C"])
        xi = np.require(xi, requirements=["C"])
        yi = np.require(yi, requirements=["C"])
        _natgrid.natgridd(x, y, z, xi, yi, zi)

        # Mask points on grid outside convex hull of input data.
        if np.any(np.isnan(zi)):
            zi = np.ma.masked_where(np.isnan(zi), zi)
        return zi
    else:
        # Linear interpolation performed using a matplotlib.tri.Triangulation
        # and a matplotlib.tri.LinearTriInterpolator.
        from matplotlib.tri import Triangulation, LinearTriInterpolator
        triang = Triangulation(x, y)
        interpolator = LinearTriInterpolator(triang, z)
        return interpolator(xi, yi)
