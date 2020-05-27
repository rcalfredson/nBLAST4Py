library(flycircuit)
library(cmtkr)
library(nat.templatebrains)
thIDs = readLines("data\\thGal4Neurons.txt")
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
    myN = fc_read_neurons(id)
    leftsomas = unlist(nat::nlapply(myN,left.somas))
    myN_left = nat.templatebrains::mirror_brain(myN[leftsomas], brain = FCWB)
    myN = c(myN[!names(myN)%in%names(myN_left)],myN_left)
    myN_as_JRC =  xform_brain(myN, reference="JRC2018F", sample="FCWB")

    write.neuron(myN_as_JRC[[1]], file=paste0(id, "_jrc"), dir='data\\fc_th',
      format='swc', Force=T)
}
