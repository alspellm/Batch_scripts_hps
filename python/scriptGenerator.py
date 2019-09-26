import subprocess

class scriptGenerator:

    # Members
    
    scriptFile = ""
    scriptFileName = ""
    scriptdir      = ""
    outputdir      = ""
    step           = "stdhep"
    #Readout steering file: /nfs/slac/g/hps2/pbutti/MC_basic_generation/readoutFiles/Test_readout.lcsim
    #Recon   steering file: steering-files/src/main/resources/org/hps/steering/production/Run2019ReconPlusDataQuality.lcsim
    
    steeringFile   = "/nfs/slac/g/hps2/pbutti/MC_basic_generation/readoutFiles/Test_readout.lcsim"
    jarFile        = "distribution/target/hps-distribution-4.4-2019-SNAPSHOT-bin.jar"

    #Methods

    def __init__(self, step, scriptdir,outputdir):
        self.step           = step
        self.scriptdir      = scriptdir
        self.outputdir      = outputdir

    def setupStep(self):
        pass

    def generateScript(self,fileID):
        self.scriptFileName = self.scriptdir+"/script_submit_job_"+fileID+".sh"
        self.scriptFile = open(self.scriptFileName,"w")
        self.wline("#! /bin/bash")
        self.wline('JOBFILEDIR=`mktemp -d /scratch/${LSB_JOBID}_JobWork.XXXXXX`')
        self.wline('echo "Job file directory: $JOBFILEDIR"')
        self.wline('export HOME=$JOBFILEDIR')
        self.wline('cd $HOME')
        self.wline('export OUTPUTDIR=$JOBFILEDIR/outputs_'+fileID+'_${LSB_JOBID}/; mkdir $OUTPUTDIR')
        self.wline('echo "Created $OUTPUTDIR"')
        self.wline('source /nfs/slac/g/hps3/software/setup.sh')
        self.wline('export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH')
        self.wline('hostname')
        
    def closeScript(self):
        self.wline('echo "Moving files to outputdir"')
        self.wline('mv $OUTPUTDIR ' + self.outputdir)
        self.wline('echo "Removing $JOBFILEDIR"')
        self.wline('rm -R $JOBFILEDIR')
        self.scriptFile.close()
        subprocess.call(["chmod","u+x",self.scriptFileName])


    def wline(self,line):
        self.scriptFile.write(line+"\n")
        
    def setupStdhepToSimul(self,stdhepFile,outFileName,detector,nEvents):
        #TODO-FIX THIS
        self.wline('cd /nfs/slac/g/hps2/pbutti/hps-java/')
        # Setup SLCIO
        self.wline('source /nfs/slac/g/hps/hps_soft/slic/build/slic-env.sh')
        self.runSlic(stdhepFile,outFileName,detector,nEvents)

    def setupBunchSpacing(self,slcioFile,outFileName,spacing=250,Ecut=0.05,wOption=2000000):
                
        #TODO-FIX THIS
        self.wline('cd /nfs/slac/g/hps2/pbutti/hps-java/')
        self.wline('java -DdisableSvtAlignmentConstants -XX:+UseSerialGC -Xmx1000m -cp '+ self.jarFile +' org.hps.util.FilterMCBunches -e'+str(spacing)+' '+slcioFile+' $OUTPUTDIR/'+ outFileName+'.slcio -d -E'+str(Ecut)+' -w'+str(wOption))
        

    def setupReadout(self,slcioFile,outFileName,detector,runNumber=9600):
        #TOD-FIX THIS
        self.wline('cd /nfs/slac/g/hps2/pbutti/hps-java/')
        self.wline('java -jar '+self.jarFile+" "+self.steeringFile + " -i " + slcioFile + " -DoutputFile=$OUTPUTDIR/"+outFileName+" -R "+str(runNumber) +" -d "+detector)
        

    def setupRecon(self,slcioFile,outFileName,nevents=-1):
        self.wline('cd /nfs/slac/g/hps2/pbutti/hps-java/')
        cmd = 'java -jar ' + self.jarFile + ' ' + self.steeringFile  +' -i ' + slcioFile + ' -DoutputFile=$OUTPUTDIR/'+outFileName
        if (nevents>0):
            cmd+=' -n ' + str(nevents)
        self.wline(cmd)


    def runHipster(self,slcioFile):
        self.wline('source /nfs/slac/g/hps2/pbutti/hipster/hpstr_env_init.sh')
        self.wline('hpstr /nfs/slac/g/hps2/pbutti/hipster/run/rawSvtHits_cfg_bsub.py ' + slcioFile)
            
    def runSlic(self,istdhep,ofile,det,nevs):
        self.wline('echo slic -g ' + det + ' -i ' + istdhep + ' -x -p $OUTPUTDIR/  -o ' + ofile + ' -r ' + str(nevs))
        self.wline('slic -g ' + det + " -i " + istdhep + " -x -p $OUTPUTDIR/ -o " + ofile + " -r " + str(nevs))
    
    
    def setSteeringFile(self, steeringFile):
        self.steeringFile = steeringFile
    
    def setJarFile(self, jarFile):
        self.jarFile = jarFile
