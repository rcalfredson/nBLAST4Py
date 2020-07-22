library(here)
library(rgl)
library(nat.jrcbrains)
library(nat)
library(imager)
library(argparser, quietly=TRUE)

load('data\\brainSurfaces.RData')
p <- arg_parser("View Drosophila neurons along with 3D anatomical landmarks")

p <- add_argument(p, '--queryNeuron', help="path to query skeleton SWC file")
p <- add_argument(p, "targetNeuron", help="path to target skeleton SWC file")
argv <- parse_args(p)
targetNeuronPath = argv$targetNeuron
if (!is.null(argv$queryNeuron)) {
  queryNeuronPath = argv$queryNeuron
  queryNeuron = read.neuron(queryNeuronPath)
} else{
  queryNeuronPath = ''
}

targetNeuron = read.neuron(targetNeuronPath)
open3d()
plot3d(targetNeuron, col='magenta', add=TRUE)
if (nchar(queryNeuronPath) > 0){
  plot3d(queryNeuron, col='cyan', add=TRUE)
}
plot3d(al_R, add=TRUE, alpha=0.15)
plot3d(alPrime_R, add=TRUE, alpha=0.15)
plot3d(bl_R, add=TRUE, alpha=0.15)
plot3d(blPrime_R, add=TRUE, alpha=0.15)
plot3d(EB,  add=TRUE, alpha=0.15)
plot3d(lh_R, add=TRUE, alpha=0.15)
decorate3d(axes=TRUE)
par3d(windowRect = c(20, 30, 1000, 800))
legendArgs = c(tail(strsplit(targetNeuronPath,
  "\\\\")[[1]], n=1))
if (nchar(queryNeuronPath) > 0) {
  legendArgs = c(legendArgs, tail(strsplit(queryNeuronPath, "\\\\")[[1]], n=1))
}
legend3d("topright", legend = paste('Type', legendArgs),
  pch = 16, col = c("magenta", "cyan"), cex=1, inset=c(0.11))
filePrefix = strsplit(tail(strsplit(targetNeuronPath,
  "\\\\")[[1]], n=1), '.swc')[[1]]
if (nchar(queryNeuronPath) > 0) {
  filePrefix = paste0(filePrefix, "_vs_", strsplit(tail(strsplit(
    queryNeuronPath, "\\\\")[[1]], n=1), '.swc')[[1]])
}
filePrefix = paste0("imgs\\", filePrefix)
rgl.viewpoint(userMatrix=matrix(c(1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0,
  0, 1), nrow=4, ncol=4), zoom=0.5)
rgl.snapshot(paste0(filePrefix, "_front.png"), top=FALSE)
rgl.viewpoint(userMatrix=matrix(c(0, 0, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0,
  0, 1), nrow=4, ncol=4), zoom=0.5)
rgl.snapshot(paste0(filePrefix, "_side.png"), top=FALSE)

resizeImage <- function(suffix) {
    print("opening")
    inFile = paste0(filePrefix, suffix, ".png")
    print(inFile)
    im = load.image(inFile)
    if (file.exists(inFile)) 
        file.remove(inFile)
    print(im)
    thmb <- autocrop(im)
    print('save path')
    print(paste0(filePrefix, suffix))
    print(thmb)
    save.image(thmb, file = paste0(filePrefix, suffix, ".jpg"))
}

resizeImage("_front")
resizeImage("_side")