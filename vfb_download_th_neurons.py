import csv
import os
import requests
from collections import Counter

neuron_data = []
with open('data/vfb_fc_neurons.csv', 'r') as myData:
  reader = csv.reader(myData)
  for row in reader:
    neuron_data.append(row)

has_new_url = []
for datum in neuron_data:
  if datum[1].startswith('TH-') and 'VFB_00101567' in datum[4]:
    has_new_url.append(datum[1])

pruned_neurons = []
for datum in neuron_data:
  if datum[1].startswith('TH-') and ((datum[1] in has_new_url and \
      'VFB_00101567' in datum[4]) or (datum[1] not in has_new_url)):
    pruned_neurons.append(datum)

neuron_names = [entry[1] for entry in pruned_neurons]
thCounter = Counter(neuron_names)
print('neuron names sorted by occurrence:', thCounter)
for neuron in pruned_neurons:
  download_url = '/'.join(neuron[-1].split('/')[:-1]) + 'volume.nrrd'
  print('downloading from', download_url)
  nrrdFile = requests.get(download_url)
  with open('data/fc_th/%s.nrrd'%neuron[1], 'wb') as myFile:
    myFile.write(nrrdFile.content)
