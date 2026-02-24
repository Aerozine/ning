import numpy as np 
from scipy import stats
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
import os
import glob
show=False
# report
# finish reading doc 
# import Tc as function of thickness and reference it 

def Nperc_dep():

    plt.figure(figsize=(10, 6))
    data = np.loadtxt("data/sample.csv",
				    delimiter=";", dtype=float)
    # dep rate , Ar % , N % , Bp , Pressure,Pow , Sample number , width 
    deprate=data[:,0]
    Nperc=data[:,2]*5
    Press=data[:,4]*1E8
    # dep_rate . % Ar . % N . Bp . Pressure . Power 
    Nconc=np.loadtxt("data/Nconcentration.csv",
                    delimiter=';',dtype=float)
    dep_rate=Nconc[:,0]
    N=Nconc[:,2]*5
    P=Nconc[:,4]*1E8
    Nperc =np.concatenate((Nperc , N))
    deprate=np.concatenate((deprate,dep_rate))
    Press=np.concatenate((Press,P))
    # dep_rate , % Ar , % N , Bp , total dep,P
    slope, intercept, r, p, std_err =stats.linregress(Nperc,deprate)
    mse = (np.square(deprate - Nperc*slope+intercept)).mean()
    plt.tick_params(direction='in')
    plt.plot(Nperc,Nperc*slope+intercept,label=f"Linear regression")#with std_err={std_err:.3e} \n and mse={mse:.3e}" )
    #print(f"linear : {slope:.4e}x+{intercept:.4e}")
    #def tanh_func(x, a, b, c, d):
    #    return a *x* np.tanh(b * x + c) + d
    #p0=[-0.17875140315532054,0.39563109526106366,7.138994098189606,0.8898857105085148]
    #params, covariance = curve_fit(tanh_func, Nperc,deprate,p0=p0)
    #a, b, c, d = params
    arr = np.linspace(0,15,50)
    # i dont know what else shoud i do
    #mse = (np.square(deprate - tanh_func(Nperc,*params))).mean()
    #std_err=mse
    #plt.plot(arr,tanh_func(arr,*params), label=f"Fitted tanh curve with mse={std_err:.3e}", color='red', linewidth=2)
    #print(f"tanh :{a:.4e}*tanh({b:.4e} * x + {c:.4e}) + {d:.4e} ")
    plt.scatter(Nperc[0:8],deprate[0:8],c='b',s=50,label="Sample")
    #plt.scatter(Nperc[8:],deprate[8:],c='b',s=50,marker='s',label="depostition test")

    #plt.rcParams.update({'font.size':50})
    plt.xlabel(r"$P_N \ [\%]$",fontsize=20)
    plt.ylabel("deposition rate [Å/s]",fontsize=20)
    #plt.title("depostition rate as a function of partial pressure of N \n for a total flow rate of 20sccm , power at 210W and 50 nm thickness ",fontsize=20)
    plt.xticks(Nperc,fontsize=18)

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    #plt.grid(True)
    plt.legend(loc='best',fontsize=18)
    plt.savefig("depostition_rate_N_concentration.pdf")
    plt.savefig("depostition_rate_N_concentration.png",dpi=600)
    if show==True:
        plt.show()
    plt.close()
    # select where Tc < 0.05 retrieve value 


def graphT_R():
    # rename all file NING-XX.dat
    # extract data 
    # determine the Tc line back and forth
    # store it on a file 
    # generate a NING / Tc graph 
    # generate a 

    maxtemp=15
    # glob glob glob !
    files = glob.glob('data/031125/NING-11.dat')
    plt.figure(figsize=(10,6 ))
    dic=[] 
    for file in files:
        filename=os.path.basename(file).replace('.dat', '')
        sample=int(filename.replace('NING-',''))
        i, t, Tp, Ts, V = np.genfromtxt(file, unpack=True)
        V=V[Ts<maxtemp]
        Vn=((V-np.amin(V))/np.amax(V-np.amin(V))) 
        Ts=Ts[Ts<maxtemp] 
        dT=np.gradient(Ts)
        # if back and forth , allow to distinct the two
        plt.plot(Ts, Vn, '--',linewidth=3)#, label=filename)
        plt.scatter(Ts[dT>0], Vn[dT>0], marker='^',s=100,color='blue')
        plt.scatter(Ts[dT<0], Vn[dT<0], marker='v',s=100,color='blue')
        # depend on the way but retrieve the value where it cross 0.5
        if(Vn[0]<0.5):
            firstbump=np.where(Vn >= 0.9)[0][0]
            lastbump=np.where(Vn >= 0.1)[0][0]
        else:
            firstbump=np.where(Vn <= 0.1)[0][0]
            lastbump=np.where(Vn <= 0.9)[0][0]
        err=np.abs(Ts[firstbump]-Ts[lastbump])
        plt.axvline(x=Ts[lastbump],label=f"Low band error",alpha=0.7,color='blue')
        #plt.axvline(x=Ts[firstbump],label=f"low band error",alpha=0.5)
        lineaxis=np.mean(Ts[firstbump-1:firstbump+1])

        plt.axvline(x=lineaxis,label=f"Taken value ({lineaxis})",alpha=0.7,color='green')
        dic.append((sample,lineaxis,err))
        #plt.axvline(x=lineaxis,label=f"x={lineaxis}",alpha=0.5)

    plt.tick_params(direction='in',length=10)#, width=2)
    plt.xlabel('T (K)',fontsize=22)
    plt.ylabel('R/R_max',fontsize=22)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlim(10, 12)
    #plt.title("resistivity as a function of temperature for the highest $T_c$ sample",fontsize=20)
    plt.legend(fontsize=20)
    plt.savefig("nice_res.pdf")
    plt.savefig("nice_res.png",dpi=600)
    
    if show==True:
        plt.show()
    plt.close()
    """
    to compute error bar
    retrieve 0.01 and 1-0.01 -> divide by two 
    """


def T_R():
    # rename all file NING-XX.dat
    # extract data 
    # determine the Tc line back and forth
    # store it on a file 
    # generate a NING / Tc graph 
    # generate a 

    maxtemp=15
    # glob glob glob !
    files = glob.glob('data/*/*.dat')
    plt.figure(figsize=(19,13 ))
    dic=[] 
    for file in files:
        filename=os.path.basename(file).replace('.dat', '')
        sample=int(filename.replace('NING-',''))
        i, t, Tp, Ts, V = np.genfromtxt(file, unpack=True)
        V=V[Ts<maxtemp]
        Vn=((V-np.amin(V))/np.amax(V-np.amin(V))) 
        Ts=Ts[Ts<maxtemp] 
        dT=np.gradient(Ts)
        # if back and forth , allow to distinct the two
        plt.scatter(Ts[dT>0], Vn[dT>0], marker='^',s=55)
        plt.scatter(Ts[dT<0], Vn[dT<0], marker='v',s=55)
        # depend on the way but retrieve the value where it cross 0.5
        if(Vn[0]<0.5):
            firstbump=np.where(Vn >= 0.9)[0][0]
            lastbump=np.where(Vn >= 0.1)[0][0]
        else:
            firstbump=np.where(Vn <= 0.1)[0][0]
            lastbump=np.where(Vn <= 0.9)[0][0]
        err=np.abs(Ts[firstbump]-Ts[lastbump])
        plt.axvline(x=Ts[lastbump],label=f"x={lastbump}",alpha=0.5,linewidth=2)
        plt.axvline(x=Ts[firstbump],label=f"x={firstbump}",alpha=0.5,linewidth=2)
        lineaxis=np.mean(Ts[firstbump-1:firstbump+1])

        dic.append((sample,lineaxis,err))
        #plt.axvline(x=lineaxis,label=f"x={lineaxis}",alpha=0.5)
        plt.plot(Ts, Vn, '--', label=filename)
    np.savetxt("data/tc.csv",np.array(dic),delimiter=';')
    plt.xlabel('T (K)')
    plt.ylabel('R/R_max')
    plt.title("resistivity as a function of temperature for the differents sample")
    plt.legend()
    plt.savefig("temperature_resistivity.pdf")
    plt.savefig("temperature_resistivity.png",dpi=600)
    
    if show==True:
        plt.show()
    plt.close()
    """
    to compute error bar
    retrieve 0.01 and 1-0.01 -> divide by two 
    """

def Tc():
    # contains ning sample ; tc
    data = np.loadtxt("data/tc.csv",
				    delimiter=";", dtype=float) 
    # contains dep rate ; ar ; n ; bp;press;pow;sample;width
    sampledata=np.loadtxt("data/sample.csv",delimiter=";",dtype=float)
    listsample=sampledata[:,6]
    #reorder data
    press=[]
    deprate=[]
    for sample in data:
        idx=np.where(listsample == sample[0])[0][0]
        sample[0]=sampledata[idx,2]
        press.append(sampledata[idx,4])
        deprate.append(sampledata[idx,0])
    # dividing by total SCCM
    press=np.array(press)
    deprate=np.array(deprate)
    smple=data[:,0]/20
    tc=data[:,1]
    err=data[:,2]
    order=np.argsort(smple)
    smple=smple[order]*100
    err=err[order]
    press=press[order]
    deprate=deprate[order]
    tc=tc[order]

    kalx=[0.5,4,8,16,20]
    kaly=[2.55,9.39,12.24,12.83,7.91]
    sugix=[4,6,8,10,12,14]
    sugiy=[6.1,10.2,12.4,13.6,13.6,13.2]

    plt.plot(smple,tc)
    plt.plot(kalx,kaly,color='orange')
    plt.plot(sugix,sugiy,color='green')
    plt.errorbar(smple,tc,yerr=err, capsize = 5, color = 'blue', marker = 'none', markersize = 10, markerfacecolor = 'blue', linestyle = 'none')
    plt.scatter(kalx,kaly,s=20,marker='o',color='orange',label='Kalal et al.')
    plt.scatter(sugix,sugiy,s=20,marker='o',color='green',label='Sugimoto et al.')
    plt.scatter(smple,tc,s=20,marker='o',label='0.1 onset result')

    plt.xlabel(r"$P_N \ [\%]$",fontsize=16)
    plt.ylabel("$T_c$ [K]",fontsize=16)
    plt.tick_params(direction='in')
    #plt.title("$T_c$ as a function of partial pressure of N \n for a total flow rate of 20sccm , power at 210W and 50nm thickness ",fontsize=18)
    plt.xticks(np.arange(0,22.5,2.5))
    plt.legend(loc='best',fontsize=14)
    plt.savefig("Tc_Pn.pdf")
    plt.savefig("Tc_Pn.png",dpi=600)
    if show==True:
        plt.show()
    plt.close()

Nperc_dep()
T_R()
Tc()

graphT_R()
