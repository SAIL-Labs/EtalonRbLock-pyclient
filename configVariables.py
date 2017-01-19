import numpy as np
sos = np.asarray(
    [[5.80953794660816e-06, 1.16190758932163e-05, 5.80953794660816e-06, 1, -1.99516198526679, 0.995185223418579],
     [0.00240740227660535, 0.00240740227660535, 0, 1, -0.995185195446789, 0]])

samplescale=9.1604852488056226e-07 #nm per sample, 20hz, 20000 samples, DE_64, sweep amp 20, centre

decimation=64
aquisitionsize = 1280000//decimation
x = np.arange(aquisitionsize)

degperms=1/8200

starttemp=3.56
starttemp=3.891


#starttemp=0.4544
