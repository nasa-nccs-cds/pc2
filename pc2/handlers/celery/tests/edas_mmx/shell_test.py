from pc2.app.shell import PC2Shell
import os

HERE = os.path.dirname(__file__)
SETTINGS = os.path.join(HERE, 'edas_test_settings.ini')

shell = PC2Shell( SETTINGS )
shell.cmdloop()




#    context['observation']=os.path.join( DATA_DIR, 'csv','ebd_Cassins_2016.csv' )
#   context['species']='Cassins Sparrow'
#    context['outDir']=DATA_DIR
#   context['numTrials']=3
#    context['numPredictors']=2
#    context['imageDir']=os.path.join( DATA_DIR, 'merra' )    #path to NetCDF files