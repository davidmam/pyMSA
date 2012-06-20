# Copyright (c) 2012 - N.P. de Klein
#
#     This file is part of Python Mass Spec Analyzer (PyMSA).
#
#     Python Mass Spec Analyzer (PyMSA) is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Python Mass Spec Analyzer (PyMSA) is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Python Mass Spec Analyzer (PyMSA).  If not, see <http://www.gnu.org/licenses/>.")


"""
Contains a Plot class which has functions for generic plots by R. Contains functions to easily plot histograms, boxplots, standard plots etc.
"""

# author: ndeklein
# date:08/02/2012
# summary: Different ways of plotting information

import rpy2.robjects as R
import rFunctions
import config
import compareFeatureXMLmzML
import sys 
# to be able to import pymzml from a locally installed pymzml
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass
import pymzml
import output
import warnings
import random


class Plots:
    """
    Contains functions for generic plots by R. Contains functions to easily plot histograms, boxplots, standard plots etc.
    """ 
    
    def __init__(self):
        """
        set some default values that are used by multiple functions, like png window size
        """
        # some default values, can be overridden in the functions by calling function(title='example') because of the **kargs
        self.title = ''
        self.xlab = 'x'
        self.ylab = 'y'
        self.pngWidth = 600
        self.pngHeight = 600
        self.log = 10
    
    # return a dictionary with the values for drawing plots. Uses the defaults from __init__, which can be overridden by arguments given to the **kwargs of a function
    def getParams(self, kwargsDict):
        """
        Has a dictionary with default values for all the plots which can be overriden by arguments given to kwargsDict. 
        The defaultdict looks like this (and these key value pairs can be given to kwargsDict):
        defaultDict = {'title':self.title, 'xlab':self.xlab, 'ylab':self.ylab, 'width':self.pngWidth, 'height':self.pngHeight, plotArgs:None}
        
            - title: Title of the graph
            - xlab: Description on the x-axis
            - ylab: Descripion on the x-axis
            - width: Width of the png
            - height: Height of the png
            - plotArgs: Additional arguments that can be given to the plot. Has to be a dictionary with as key the name of an option
                        (e.g. labels) and as value the value for that option (e.g. True). So in this case -> plotArgs = {'labels':True}
            - colors: The colors that will be used in the graph. Rgb numbers are used, and the first color in the list is used as the color
                      of the first vector, second for the second vector etc. So if you have one histogram that you want red give plotArgs = {'colors':[255,0,0]}
                      'red', 'blue', 'green' or 'yellow' is also accepted.
            - legend: Arguments given to make the legend of the plot
            
        @type kwargsDict: dictionary
        @param kwargsDict: A dictionary containing all the extra input given to a function, passed to **kwargs
        @rtype: dictionary
        @return: The keys and values of the default dictionary, only the values overriden that were given to kwargsDict         
        @raise TypeError: kwargsDict not of type dict 
        
        B{Example}:
        
        Overriding some default values and leaving some as they are:
        
        >>> def exampleFunction(**kwargs):
        ...    plots = Plots()
        ...    return plots.getParams(dict(kwargs))     # have to make a dictionary out of kwargs
        >>> print exampleFunction(title='example getParams', xlab = 'example 2 kwargs') # only override title and xlab, rest stay default
        {xlab': 'example 2 kwargs', 'title': 'example getParams', 'ylab': 'y', 'width': 600, 'legend':True,
                        'height': 600, plotArgs:None, colors='blue','red','yellow','green'}

        """
        # setting the default values and names of the parameters (the values can be overriden with kwargs)
        defaultDict = {'title':self.title, 'xlab':self.xlab, 'ylab':self.ylab, 'width':self.pngWidth, 'height':self.pngHeight,
                       'legend':None, 'plotArgs':None, 'colors':['blue','red','yellow','green','gold','brown','purple']}

    

        # controlling that kwargs and defaultDict are of the right type
        if not type(kwargsDict) == dict:
            raise TypeError, 'kwargsDict passed to getParams is not of type dict. Instead, it is of type: '+str(type(kwargsDict))
        # setting the default values and names of the parameters (the values can be overriden with kwargs)
        params = defaultDict    
        for key in kwargsDict:
            # check if the right name for the kwargs has been given (only the ones found in the params dict are allowed
            if params.has_key(key):
                # change the value in the dict to the value given to kwargs 
                params[key] = kwargsDict[key] 
            else:
                warnings.warn('Input param: \''+str(key)+'\' not used. The available input params are: '+str(params.keys()), UserWarning, stacklevel=2)
        
        return params
    
    # change the standard names (blue, red, yellow etc into hexidecimal value). Make them transparant if transparant = True 
    def getColor(self, color, transparant=True):
        """
        Converts a color name to their rgb numbers and by default makes them transparent. If a rgb number is given it only makes 
        them transparant (if transparant==True). The list of possible colors is::
             'blue','red','yellow','green'
        Any other colors can be added by giving an rgb color to getColor
        
        @type color: str or list
        @param color: Color name or rgb color code
        @type transparant: bool
        @param transparant: If set to True, the colors returned by getColors are made transparant (AA appended at the end)
        @rtype: dict
        @return: Dictionary with values for green, blue, red and alpha
        @raise TypeError: color is not a string or list
        @raise ValueError: Color is not in the list of standard colors       
        @raise ValueError: Not enough or too many values given to color
        
        B{Example:}
        
        Printing some rgb colors with transparancy:
        
        >>> for color in ['blue','red','yellow', ['244', '164','96']]:  # the last one is an rgb 
        ...     print plots.getColor(color)
        {'alpha': 125, 'blue': 255, 'green': 0, 'maxColorValue': 255, 'red': 0},
        {'alpha': 125, 'blue': 0, 'green': 0, 'maxColorValue': 255, 'red': 255},
        {'alpha': 125, 'blue': 0, 'green': 255, 'maxColorValue': 255, 'red': 255},
        {'alpha': 125, 'blue': 96 ,'green': 164,'maxColorValue': 255,'red': 244}]
        
        To use this color:
        
        >>> import rpy2.robjects as R
        >>> example_color = {'alpha': 125, 'blue': 255, 'green': 0, 'maxColorValue': 255, 'red': 0}
        >>> print R.r['rgb'](**example_color)[0]
        #0000FF7D
        
        """
        
        # typechecking
        if not type(color) == str and not type(color) == list:
            raise TypeError, 'color given to getColor has to be of type str. Instead, is of type: '+str(type(color))
        
        # check if rgb numbers are given the list is of the right length
        if type(color) == list:
            # if length of color isn't 3 or 4 (3 without transparancy given, 4 with)
            if len(color) <= 2 or len(color) >= 5:
                raise ValueError, 'Either too many values given to color rgb list or too little. Need 3 color values (red, green blue) and an optional transparancy value' 
            for index, value in enumerate(color):
                color[index] = int(value)
        # a map of the colors standard names and their hexidecimal values
        ['blue','red','yellow','green','gold','brown','purple']
        colorMap = {'blue':[0,0,255],'red':[255,0,0], 'yellow':[255,255,0], 'green':[0,255,0], 'gold':[255, 215, 0], 'brown':[165, 42, 42], 'purple':[160,32,240]}
        
        if type(color) == str:
            # because all the names in the colorMap are lowercase, make the input lowercase too
            color = color.lower()
            if not colorMap.has_key(color):
                raise ValueError, str(color)+' is not in the colors list. The list is: '+str(colorMap.keys())+'. You can add your own colors by providing rgb codes'
            color = colorMap[color]
                
        # if the colors have to be transparant
        if transparant == True:
            if len(color) == 3:
                color.append(125) # add half transparancy transparancy to rgb
        
        rgbDict = {'red':int(color[0]), 'green':int(color[1]), 'blue':int(color[2]), 'alpha':int(color[3]), 'maxColorValue':int(255)}
        return rgbDict
    
    
    def plot(self, outPath, x, y=None, **kwargs):
        """
        Generic X-Y plotting. Uses: http://stat.ethz.ch/R-manual/R-devel/library/graphics/html/plot.html
    
        @type outPath: string
        @param outPath: Path for the output file
        @type x: R object
        @param x: the coordinates of points in the plot. Alternatively, a single plotting structure, function or any R object with a plot method can be provided.
        @type y: R object
        @param y: the y coordinates of points in the plot, optional if x is an appropriate structure. (default = None)
        @param kwargs: Additional arguments. See defaultdict in getParams documentation for a full list of possible arguments.
        @raise TypeError: plotArgs not a dictionary
        
        B{Examples:}
        
        <TODO>
        """ 
        
        # getting the parameter values (the ones given to the function, or default if the param wasn't given to the function)
        params = self.getParams(dict(**kwargs))

        plot = R.r['plot']
        # open the png
        R.r.png(outPath, width=params['width'], height=params['height'])
        
        # because plotArgs cannot be given to hist when it is None (gives an error), check if it has a value
        if params['plotArgs'] == None:
            if y:
                plot(x, y, main=params['title'], xlab=params['xlab'], ylab=params['ylab'])
            else:
                plot(x, main=params['title'], xlab=params['xlab'], ylab=params['ylab'])
        else:
            if not type(params['plotArgs']) == dict:
                raise TypeError, 'plotArgs given to rFeaturePerIntensityHistogram has to be of type dict. Instead, is of type: '+str(type(params['plotArgs']))
            if y:
                plot(x, y, main=params['title'], xlab=params['xlab'], ylab=params['ylab'], **params['plotArgs'])
            else:
                plot(x, main=params['title'], xlab=params['xlab'], ylab=params['ylab'], **params['plotArgs'])
        R.r['dev.off']()
          
    # standard function for drawing a histogram or overlapping histogram
    def histogram(self, outPath, *args, **kwargs):
        """
        Draw a histogram based on n amount of vectors (standard max 12 because of color limitations). 
        Uses: http://www.stat.ucl.ac.be/ISdidactique/Rhelp/library/base/html/hist.html
     
        @type outPath: string
        @param outPath: Path for the output file
        @type args: rpy2.robjects.vectors.IntVector or rpy2.robjects.vectors.FloatVector
        @param args: n amount of Float- or IntVectors to be used to draw the histogram
        @param kwargs: Additional arguments. See defaultdict in getParams documentation for a full list of possible arguments.
        @raise TypeError: plotArgs not a dictionary
        @raise TypeError: dataframe is not of type dataframe
        @raise TypeError: No arguments given to *args
        @raise TypeError: One or more of the argumetns given to *args is not of type rpy2.robjects.vectors.IntVector or of type rpy2.robjects.vectors.FloatVector

        B{Examples:}
        
        Plotting one histogram:
        
        >>> vector = R.IntVector((1,2,2,3,3,3,4,4,5))        # example vector 1
        >>> histogram('example_output.png', vector1, vector2, 'Test png', 'x-axis example', 'y-axis example')
        
        Plotting two histograms in one figure:
        
        >>> vector1 = R.IntVector((1,2,2,3,3,3,4,4,5))        # example vector 1
        >>> vector2 = R.IntVector((3,4,4,5,5,5,6,6,7))        # example vector 2
        >>> histogram('example_output.png', vector1, vector2, 'Test png', 'x-axis example', 'y-axis example', 
        ...            legend= {'x':'topright','legend':R.StrVector(['features', 'MS/MS precursors']), 'lty':R.IntVector([1,1]), 'lwd':R.IntVector([2.5,2.5])})
        >>> R.r['dev.off']() 
        """
        # getting the parameter values (the ones given to the function, or default if the param wasn't given to the function)
        params = self.getParams(dict(**kwargs))
        
        # need at least one argument to *args because these are the vector(s) that the histogram will be made out of
        if len(args) == 0:
            raise TypeError, 'No vectors given to *args'
        
        # argCount for error reporting
        argCount = 0
        for arg in args:
            argCount += 1
            if not isinstance(arg, R.vectors.IntVector) and not isinstance(arg, R.vectors.FloatVector):
                raise TypeError, 'Argument '+str(argCount)+' given to *args is not of type rpy2.robjects.vectors.IntVector or of type rpy2.robjects.vectors.FloatVector. Instead, is of type: '+str(type(arg))
        
        
        # using na.rm (to filter out the NA's (not availables) out of the vectors
        narm = {'na.rm':True}
        # get the min and max value of both vectors (later be used for xlim)
        # the min and max to keep track of what the min and the max are. -1 is the starting point, because the values will always be above that
        xMin = -1
        xMax = -1
        for arg in args:
            # setting the start values
            if xMin == -1:
                xMin = R.r['floor'](R.r['min'](arg, **narm))[0]
            if xMax == -1:
                xMax = R.r['ceiling'](R.r['max'](arg, **narm))[0]
            
            if R.r['floor'](R.r['min'](arg, **narm))[0] < xMin:
                xMin = R.r['floor'](R.r['min'](arg, **narm))[0]
            if R.r['ceiling'](R.r['max'](arg, **narm))[0] > xMax:
                xMax = R.r['ceiling'](R.r['max'](arg, **narm))[0]
        
        # moving the marges for xlim by one so that the graph doesn't fall off
        xMin -= 1
        xMax += 1

        # looping through all the vectors given to *args. The first vector is used as the 'main' histogram, the rest is added later
        # counter to know when it is the first argument
        argCount = 0
        
        # a dict to keep track of what colors, names etc are used incase it's needed for the legend
        plotMetaInfo = {'col':[]}
        # open the png
        R.r.png(outPath, width=params['width'], height=params['height'])
        #R.r.png(outPath, width=params['width'], height=params['height']) 
        for arg in args:
            color = R.r['rgb'](**self.getColor(params['colors'][argCount]))
            if argCount == 0:
                # plot a red and a blue histogram with the overlap being purple
                if params['plotArgs'] == None:
                    # the colors get added by rgb which is a dictionary with red, blue,green and alpha keys and corresponding values (see getColors for more details)
                    R.r['hist']( arg, col=color, xlim=R.IntVector((xMin,xMax)), main=params['title'], xlab=params['xlab'], ylab=params['ylab'])  # first histogram
                else:
                    R.r['hist']( arg, col=color, xlim=R.IntVector((xMin,xMax)), main=params['title'], xlab=params['xlab'], ylab=params['ylab'], **params['plotArgs'])  # first histogram
            else:
                R.r['hist']( arg, xlim=R.IntVector((xMin,xMax)), add=True, col=color)  # rest
            # save the colors used
            plotMetaInfo['col'].append(color[0]) # the 0 is because it saves it as python object, this gets the hexidecimal number
            argCount += 1
            

               

        
    
    # barplot
    def barplot(self, outPath, table, **kwargs):
        r"""
        Plot a barplot of MS/MS per feature.
        Uses: http://stat.ethz.ch/R-manual/R-devel/library/graphics/html/barplot.html
        
        @type outPath: string
        @param outPath: Path for the output file        
        @type table: rpy2.robjects.vectors.Array
        @param table: An R table. The column names will be used as x-axis names and column values to make the bars.
        @param kwargs: Additional arguments. See defaultdict in getParams documentation for a full list of possible arguments.
        @raise TypeError: plotArgs is not of type dict
        @raise TypeError: precursorVector is not of type rpy2.robjects.vectors.IntVector
       
        B{Example}:

        Plotting a barplot:
       
        >>> import rpy2.robjects as R                                             
        >>> intVector = R.vectors.IntVector((0,0,0,0,1,1,1,1,1,2,3,3,4,4,4,4,5))    # example IntVector
        >>> table = R.r['table'](intVector)                                         # making a table out of the IntVector. It counts the occurence of each number and takes that number as bar name
        >>> plots = rPlots.Plots()
        >>> plots.barplot('example_output.png',table, width=400, height=400, 
        ...                                        title='a barplot', xlab='an x-axis name', ylab='an y-axis name')
        R.r['dev.off']() 
        """
        if not isinstance(table, R.vectors.Array):
            raise TypeError, 'table given to rMSMSperFeatureBarplot is not of type py2.robjects.vectors.Array (with rpy2: rpy2.robjects[\'table\']. Instead is of type: '+str(type(table))
        # getting the parameter values (the ones given to the function, or default if the param wasn't given to the function)
        params = self.getParams(dict(**kwargs))
        barplot = R.r.barplot
        # open the png
        R.r.png(outPath, width=params['width'], height=params['height'])
        
        # because plotArgs cannot be given to hist when it is None (gives an error), check if it has a value
        if params['plotArgs'] == None:
            barplot(table, main=params['title'], xlab=params['xlab'], ylab=params['ylab'])
        else:
            if not type(params['plotArgs']) == dict:
                raise TypeError, 'plotArgs given to rFeaturePerIntensityHistogram has to be of type dict. Instead, is of type: '+str(type(params['plotArgs']))
            barplot(R.r['table'](table), main=params['title'], xlab=params['xlab'], ylab=params['ylab'], **params['plotArgs'])
      
    
        
    # boxplot from a dataframe
    def boxplotDataframe(self, outPath, dataframe, **kwargs):
        """
        Makes a boxplot out of a dataframe.
        Uses: http://stat.ethz.ch/R-manual/R-devel/library/graphics/html/boxplot.html
        
        @type outPath: string
        @param outPath: Path for the output file 
        @type dataframe: rpy2.robjects.DataFrame
        @param dataframe: An R dataframe with in the columns the values for each boxplot and as column name the name for the x-axis       
        @param kwargs: Additional arguments. See defaultdict in getParams documentation for a full list of possible arguments.
        @raise TypeError: plotArgs not a dictionary
        @raise TypeError: dataframe is not of type dataframe
       
        B{Example}:

        Plotting a boxplot
       
        >>> import rpy2.robjects as R
        >>> dataframe = R.DataFrame({'a':R.IntVector([1,1,4,0,3]),'b':R.IntVector([0,0,4,3,2]), 'c':R.IntVector([2,3,4,2,1])'})
        >>> plots = rPlots.Plots()
        >>> plots.boxplotDataframe('example_output.png', dataframe, width=400, height=400, title='feature and ms/ms per intensity',
        ...                         xlab = 'log 10 of intensity', ylab = '# of MS/MS per feature')
        >>> R.r['dev.off']() 
        """
        if not isinstance(dataframe, R.DataFrame):
            raise TypeError, 'dataframe is not of type rpy2.robjects.DataFrame. Instead, is of type: '+str(type(dataframe))
        # getting the parameter values (the ones given to the function, or default if the param wasn't given to the function)
        params = self.getParams(dict(**kwargs))

        R.r.png(outPath, width=params['width'], height=params['height'])    
        # because plotArgs cannot be given to hist when it is None (gives an error), check if it has a value
        if params['plotArgs'] == None:
            R.r['boxplot'](dataframe, main = params['title'], ylab = params['ylab'], xlab = params['xlab'])
        else:
            if not type(params['plotArgs']) == dict:
                raise TypeError, 'plotArgs given to rFeaturePerIntensityHistogram has to be of type dict. Instead, is of type: '+str(type(params['plotArgs']))
            R.r['boxplot'](dataframe, main = params['title'], ylab = params['ylab'], xlab = params['xlab'], **params['plotArgs'])
        


    # boxplot from a formulae
    def boxplotFormulae(self, outPath, x, y, dataframe, **kwargs):
        """
        Makes a boxplot out of an x and y formulae and a dataframe.
        Uses: http://stat.ethz.ch/R-manual/R-devel/library/graphics/html/boxplot.html

        @type outPath: string
        @param outPath: Path for the output file
        @type x: rpy2.robjects.vectors.FloatVector or rpy2.robjects.vectors.IntVector
        @param x: First argument given to R.Formula (see  http://rpy.sourceforge.net/rpy2/doc-2.2/html/robjects_formulae.html for details)
        @type y: rpy2.robjects.vectors.FloatVector or rpy2.robjects.vectors.IntVector
        @param y: Second argument given to R.Formula (see  http://rpy.sourceforge.net/rpy2/doc-2.2/html/robjects_formulae.html for details)
        @type dataframe: rpy2.robjects.DataFrame
        @param dataframe: An R dataframe with in the columns the values for each boxplot and as column name the name for the x-axis
        @param kwargs: Additional arguments. See defaultdict in getParams documentation for a full list of possible arguments.
        @raise TypeError: plotArgs not a dictionary
        @raise TypeError: dataframe is not of type dataframe
        @raise TypeError: x is not of type rpy2.robjects.vectors.FloatVector or of type rpy2.robjects.vectors.IntVector
        @raise TypeError: y is not of type rpy2.robjects.vectors.FloatVector or of type rpy2.robjects.vectors.IntVector      
        
        B{Example}:

        Plotting a boxplot. The boxplot from dataframe is easier to use. 
       
        >>> import rpy2.robjects as R
        >>> x = R.IntVector([1,1,4,0,3])
        >>> y = R.IntVector([0,0,4,3,2])
        >>> dataframe = R.DataFrame({'a':R.IntVector([1,1,4,0,3]),'b':R.IntVector([0,0,4,3,2]), 'c':R.IntVector([2,3,4,2,1])'})
        >>> plots = rPlots.Plots()
        >>> plots.boxplotDataframe('example_output.png', x, y, dataframe, width=400, height=400, 
        ...                        title='feature and ms/ms per intensity', xlab = 'log 10 of intensity', ylab = '# of MS/MS per feature' )
        >>> R.r['dev.off']() 
        """
        if not isinstance(dataframe, R.DataFrame):
            raise TypeError, 'dataframe is not of type rpy2.robjects.DataFrame. Instead, is of type: '+str(type(dataframe))
        
        if not isinstance(x, R.IntVector) and not isinstance(x, R.FloatVector):
            raise TypeError, 'x given to boxplotFormulae is not of type rpy2.robjects.vectors.FloatVector or of type rpy2.robjects.vectors.IntVector. Instead, is of type: '+str(type(x))
        if not isinstance(y, R.IntVector) and not isinstance(y, R.FloatVector):
            raise TypeError, 'y given to boxplotFormulae is not of type rpy2.robjects.vectors.FloatVector or of type rpy2.robjects.vectors.IntVector. Instead, is of type: '+str(type(y))
   
        # getting the parameter values (the ones given to the function, or default if the param wasn't given to the function)
        params = self.getParams(dict(**kwargs))
        
        formula = R.Formula('x ~ y')
        env = formula.environment
        env['x'] = x
        env['y'] = y
        
        boxplot = R.r['boxplot']
        R.r.png(outPath, width=params['width'], height=params['height'])    
        boxplot(formula, data = dataframe)
#         because plotArgs cannot be given to hist when it is None (gives an error), check if it has a value
        if params['plotArgs'] == None:
            R.r['boxplot'](formula, data = dataframe, main = params['title'], ylab = params['ylab'], xlab = params['xlab'])
        else:
            if not type(params['plotArgs']) == dict:
                raise TypeError, 'plotArgs given to rFeaturePerIntensityHistogram has to be of type dict. Instead, is of type: '+str(type(params['plotArgs']))
            R.r['boxplot'](formula, data = dataframe, main = params['title'], ylab = params['ylab'], xlab = params['xlab'], **params['plotArgs'])
            
