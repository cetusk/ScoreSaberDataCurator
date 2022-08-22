import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

INPUT_LOG_FILENAME = "info.log"

def ppWeight ( rank:int ):
    return 0.965**( rank-1 )

def ppCorrection ( accuracy:float ):
    assert accuracy >= 0
    weight = lambda x,x0,y0,x1,y1: ( y1-y0 )/( x1-x0 )*( x-x0 ) + y0
    if accuracy <  40.0: return weight ( accuracy,   0.0, 0.000,  40.0, 0.080 )
    if accuracy <  50.0: return weight ( accuracy,  40.0, 0.080,  50.0, 0.150 )
    if accuracy <  69.0: return weight ( accuracy,  50.0, 0.150,  69.0, 0.250 )
    if accuracy <  75.0: return weight ( accuracy,  69.0, 0.250,  75.0, 0.425 )
    if accuracy <  82.0: return weight ( accuracy,  75.0, 0.425,  82.0, 0.560 )
    if accuracy <  84.5: return weight ( accuracy,  82.0, 0.560,  84.5, 0.630 )
    if accuracy <  86.0: return weight ( accuracy,  84.5, 0.630,  86.0, 0.720 )
    if accuracy <  88.0: return weight ( accuracy,  86.0, 0.720,  88.0, 0.766 )
    if accuracy <  90.0: return weight ( accuracy,  88.0, 0.766,  90.0, 0.815 )
    if accuracy <  91.0: return weight ( accuracy,  90.0, 0.815,  91.0, 0.850 )
    if accuracy <  92.0: return weight ( accuracy,  91.0, 0.850,  92.0, 0.885 )
    if accuracy <  93.0: return weight ( accuracy,  92.0, 0.885,  93.0, 0.920 )
    if accuracy <  94.0: return weight ( accuracy,  93.0, 0.920,  94.0, 0.974 )
    if accuracy <  95.0: return weight ( accuracy,  94.0, 0.974,  95.0, 1.036 )
    if accuracy < 100.0: return weight ( accuracy,  95.0, 1.036, 100.0, 1.100 )
    if accuracy < 110.0: return weight ( accuracy, 100.0, 1.100, 110.0, 1.150 )
    if accuracy < 114.0: return weight ( accuracy, 110.0, 1.150, 114.0, 1.200 )

def plotPpCorrection ( file_name:str="ppCorrection.png", ndivs:int=100 ):
    assert ndivs > 0
    # division
    dx = 1.0 / float ( ndivs )
    # aspect ratio and width
    ry = 1.0 / np.sqrt ( 2.0 )
    w = 7

    # data
    x = [ dx*ix for ix in range ( 0, 114*ndivs ) ]
    y = [ ppCorrection ( ix ) for ix in x ]

    # create figure
    fig = plt.figure (
        figsize = ( w, ry*w ), dpi = 72
    )
    fig.tight_layout ()
    plt.rcParams [ "font.size" ] = 16
    plt.rcParams [ "text.usetex" ] = True
    plt.rcParams [ "figure.constrained_layout.use" ] = True
    plt.subplots_adjust ( left=0.15, right=0.95, top=0.95, bottom=0.15 )
    ax = fig.add_subplot ( 1, 1, 1 )
    ax.set_xlabel ( r"${\rm Score}\,[\%]$", labelpad=10 )
    ax.set_ylabel ( r"${\rm PP\ Given\ ratio}$", labelpad=15 )
    [ axj.set_linewidth ( 1.0 ) for axj in ax.spines.values () ]
    ax.set_xlim ( 0-10, 115+10 )
    ax.set_ylim ( 0-0.1, 1.2+0.1 )
    ax.minorticks_on ()
    ax.plot ( x, y, c="#292929", linewidth=2.0 )
    ax.scatter (
        [
            0.0, 40.0, 50.0, 69.0, 75.0,
            82.0, 84.5, 86.0, 88.0, 90.0,
            91.0, 92.0, 93.0, 94.0, 95.0,
            100.0, 110.0, 114.0
        ],
        [
            0.0, 0.080, 0.150, 0.250, 0.425,
            0.560, 0.630, 0.720, 0.766, 0.815,
            0.850, 0.885, 0.920, 0.974, 1.036,
            1.100, 1.150, 1.200
        ],
        s=50.0, c="#292929"
    )
    plt.savefig ( file_name )

def makeSegments ( x, y ):
    points = np.array ( [ x, y ] ).T.reshape ( -1, 1, 2 )
    return np.concatenate ( [ points [ : -1 ], points [ 1 : ] ], axis=1 )

if __name__ == "__main__":

    # plotPpCorrection ()
    # exit ()
    
    # load data
    lines = None
    with open ( INPUT_LOG_FILENAME, "r" ) as fh:
        lines = fh.readlines ()
    
    # parse
    ranks = []
    stars = []
    accuracies = []
    pp_givs = []
    pp_effs = []
    for line in lines [ 1 : ]:
        buf = line.split ( "," )
        # rank, difficulty, star, acc, pp_raw, pp_eff, weight, mod, name, artist, mapper
        if float ( buf [ 3 ] ) < 0: break
        # NF: TBD ( to distinct lose or not )
        if buf [ 7 ] == "NF": continue
        # SS
        if buf [ 7 ] == "SS":
            accuracies.append ( 0.85*float ( buf [ 3 ] ) )
        else:
            accuracies.append ( float ( buf [ 3 ] ) )       
        ranks.append ( float ( buf [ 0 ] ) )
        stars.append ( float ( buf [ 2 ] ) )
        pp_givs.append ( float ( buf [ 4 ] ) )
        pp_effs.append ( float ( buf [ 5 ] ) )

    # convert list to numpy array
    ranks = np.array ( ranks )
    stars = np.array ( stars )
    accuracies = np.array ( accuracies )
    pp_givs = np.array ( pp_givs )
    pp_effs = np.array ( pp_effs )
    pp_raws = np.array ( [ p / ppCorrection ( a ) for ( p, a ) in zip ( pp_givs, accuracies ) ] )

    # sorted indices
    idxStar = np.argsort ( stars )
    idxAcc = np.argsort ( accuracies )

    # aspect ratio and width
    ry = 1.0 / np.sqrt ( 2.0 )
    w = 10

    # create figures
    fig = plt.figure (
        figsize = ( w, ry*w ), dpi = 72
    )
    fig.tight_layout ()
    plt.rcParams [ "font.size" ] = 16
    plt.rcParams [ "text.usetex" ] = True
    plt.rcParams [ "figure.constrained_layout.use" ] = True
    plt.subplots_adjust ( left=0.15, right=0.95, top=0.95, bottom=0.15 )

    # rank vs pp
    ax = fig.add_subplot ( 3, 1, 1 )
    ax.plot ( ranks, pp_raws, linewidth=2.0, label=r"${\rm Raw}$", c="royalblue" )
    ax.plot ( ranks, pp_givs, linewidth=2.0, label=r"${\rm Given}$", c="#292929" )
    ax.plot ( ranks, pp_effs, linewidth=2.0, label=r"${\rm Effective}$", c="#33cc99" )
    ax.legend ( bbox_to_anchor=( 1, 1 ), loc="upper right", borderaxespad=1, fontsize=9 )
    ax.set_xlabel ( r"${\rm Rank}$", labelpad=10 )
    ax.set_ylabel ( r"${\rm PP}$", labelpad=15 )
    [ axj.set_linewidth ( 1.0 ) for axj in ax.spines.values () ]
    ax.set_xlim ( 0-10, 400 )
    ax.set_ylim ( 0-25, 475 )
    ax.minorticks_on ()

    # star vs raw pp
    ax = fig.add_subplot ( 3, 1, 2 )
    ax.set_xlabel ( r"${\rm Star}$", labelpad=10 )
    ax.set_ylabel ( r"${\rm Raw\ PP}$", labelpad=15 )
    ax.set_xlim ( 0.5, 11 )
    ax.set_ylim ( 0, 500 )
    ax.minorticks_on ()
    ax.plot ( stars [ idxStar ], pp_raws [ idxStar ], linewidth=2.0, c="#292929", linestyle="solid" )

    # acc vs raw pp
    ax = fig.add_subplot ( 3, 1, 3 )
    ax.set_xlabel ( r"${\rm Accuracy}$", labelpad=10 )
    ax.set_ylabel ( r"${\rm Raw\ PP}$", labelpad=15 )
    ax.set_xlim ( 68, 100 )
    ax.set_ylim ( 0, 600 )
    ax.minorticks_on ()
    ax.plot ( accuracies [ idxAcc ], pp_raws [ idxAcc ], linewidth=2.0, c="#292929", linestyle="solid" )

    fig.tight_layout ()
    plt.savefig ( "pp.png" )




