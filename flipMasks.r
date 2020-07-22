library(flycircuit)
library(cmtkr)
library(nat.templatebrains)
library(nat.flybrains)
library(imager)
thIDs = readLines("data/thGal4Neurons.txt")
# source of left-hand neuron detector:
# http://natverse.org/flycircuit/reference/fc_read_neurons.html#examples
left.somas <- function(neuron, surf = FCWB.surf) {
  bb=boundingbox(surf)
  midline=(bb[1,1]+bb[2,1])/2
  r = nat::rootpoints(neuron)
  somaposition = nat::xyzmatrix(neuron$d[r,])
  somaposition[,"X"]>midline
}

for (id in thIDs) {
  print('checking neuron ID')
  print(id)
  imageFileNames = Sys.glob(c(paste0("data/fc_th/masks/", id, "*")))
  if (length(imageFileNames) < 1) {
    next
  }
  myN = fc_read_neurons(id)
  leftsomas = unlist(nat::nlapply(myN,left.somas))
  if (length(myN[leftsomas]) > 0) {
    for (imageFile in imageFileNames) {
      neuronImg = load.image(imageFile)
      mirrored = mirror(neuronImg, 'x')
      pathAndExt = strsplit(imageFile, "\\.")
      beforeExt = paste(pathAndExt[[1]][1:length(pathAndExt[[1]]) - 1], collapse='')
      save.image(mirrored, paste0(beforeExt, "_asjpeg.jpg"))
      file.rename(imageFile, paste0("data/fc_th/unflippedmasks/", basename(imageFile)))
    }
  }
}
