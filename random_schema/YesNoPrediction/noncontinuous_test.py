from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d

def showOutputs():
        print('#============================================')
        A = np.arange(0, 3, 0.1)
        B = np.arange(0, 11, 0.5)
        
        Z = np.empty([len(B),len(A)])
        
        
        for x in range(len(A)):
            for y in range(len(B)):
                inpt = np.array([A[x] , B[y] ])
                inpt = inpt.reshape(1,2)
                Z[y][x] = model.predict(inpt)
                
        
        
        A,B = np.meshgrid(A,B)
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(A, B, Z)
        plt.show()
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(a_arr,b_arr,y_arr, 'r')
        plt.show()
    
        out = model.predict(x_arr)
        plt.plot(out)
        plt.plot(y_arr)
        plt.show()
        plt.plot(hist.history['loss'])
        plt.show()

a_arr = [0,1,3,0,1,3,0,1,3,0,1,3]
b_arr = [0,1,2,3,4,5,6,7,8,9,10,11]

x_arr = np.array(list(zip(a_arr,b_arr)))
y_arr = np.array([0,0.5,0,0,0.7,0,0,0.85,0,0,1,0])

x_arr = x_arr.reshape(12,2)
y_arr = y_arr.reshape(12,1)
model = Sequential()

model.add(Dense(8,input_dim = 2,activation='sigmoid'))
model.add(Dense(8))
model.add(Dense(1))

model.compile(loss = 'mse', optimizer = Adam(lr=0.001))

hist = model.fit(x_arr,y_arr,epochs=100,verbose=0)
showOutputs()
hist = model.fit(x_arr,y_arr,epochs=500,verbose=0)
showOutputs()

hist = model.fit(x_arr,y_arr,epochs=1000,verbose=0)
showOutputs()

