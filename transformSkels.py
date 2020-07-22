import argparse, glob, os, subprocess

# note: the transformations used by this script need to be added separately to
# the project, and can be downloaded from
# https://www.janelia.org/open-science/jrc-2018-brain-templates

# Prerequisites:
#   - Jgo Python module (https://github.com/scijava/jgo#the-python-module)
#   - Saalfeld Lab template-building scripts (https://github.com/saalfeldlab/template-building)
#   - Teem, specifically its unu tool (http://teem.sourceforge.net/unrrdu/index.html)

def options():
  """Parse options for the skeleton converter and image compressor."""
  p = argparse.ArgumentParser(description='Transform NRRD image stacks from ' +
    'one space to another, optionally applying GZIP compression afterward.')
  p.add_argument('dirName', help='directory containing NRRD files to transform')
  return p.parse_args()

opts = options()
transformScript = 'org.scijava:saalfeldlab-template-building:0.1.2-SNAPSHOT:' +\
  'process.TransformImage'

skelsToTransform = glob.glob(opts.dirName +r'/*[0-9].nrrd')
# first transformation: JFRC2010 to JRC2018U
for skel in skelsToTransform:
  print('Transforming skel', skel)

  jrc2018F_filename = '%s_jrcF.nrrd'%skel.split('.nrrd')[0]
  jrc2018U_filename = '%s_jrcU.nrrd'%skel.split('.nrrd')[0]
  jrc2018U_compressed_filename = '%s_compressed.nrrd'%jrc2018U_filename.split(
    '.nrrd')[0]

  # transform JFRC2010 to JRC2018F
  subprocess.call(['py', '-3', '-m', 'pipenv', 'run', 'jgo', '-U',
    transformScript, '--interpolation=LINEAR', '--input=%s'%skel,
    '--output=%s'%jrc2018F_filename, '--transform=data\\JRC2018F_JFRC2010.h5',
    '--nThreads=7', '--outputImageSize=1652,768,479',
    '--output-resolution=0.38,0.38,0.38'])

  # transform JRC2018F to JRC2018U
  subprocess.call(['py', '-3', '-m', 'pipenv', 'run', 'jgo', '-U',
    transformScript, '--interpolation=LINEAR', '--input=%s'%jrc2018F_filename,
    '--output=%s'%jrc2018U_filename, '--transform=data\\JRC2018U_JRC2018F.h5',
    '--nThreads=7', '--outputImageSize=1652,773,456',
    '--output-resolution=0.38,0.38,0.38'])

  # compress the result using GZIP encoding
  # if the bin directory of Teem is not part of your path, an explicit path to
  # unu needs to be added here.
  subprocess.call(['unu', 'save', '-f', 'nrrd', '-e', 'gzip', '-i',
    jrc2018U_filename, '-o', jrc2018U_compressed_filename])

  # delete intermediate image stacks
  for fileName in (jrc2018F_filename, jrc2018U_filename):
    os.remove(fileName)
