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
    plt.plot(Nperc,Nperc*slope+intercept,label=f"linear regression with std_err={std_err:.3e} \n and mse={mse:.3e}" )
    print(f"linear : {slope:.4e}x+{intercept:.4e}")
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
    plt.scatter(Nperc[0:8],deprate[0:8],c=Press[0:8],cmap="coolwarm",s=50,label="NING sample")
    plt.scatter(Nperc[8:],deprate[8:],c=Press[8:],cmap="coolwarm",s=50,marker='s',label="depostition test")
    plt.colorbar(label=r'$\text{Base pressure after pre-sputtering} \ [ 1E8Torr ]$')
    plt.xlabel(r"$P_N \ [\%]$")
    plt.ylabel("deposition rate [nm]")
    plt.title("depostition rate as a function of partial pressure of N \n for a total volume of 20sccm , power at 70% and 50nm width ")
    plt.xticks(Nperc)
    plt.grid(True)
    plt.legend(loc='best')
    plt.savefig("depostition_rate_N_concentration.pdf")
    plt.savefig("depostition_rate_N_concentration.png",dpi=600)
    if show==True:
        plt.show()


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
        plt.scatter(Ts[dT>0], Vn[dT>0], marker='^',s=15)
        plt.scatter(Ts[dT<0], Vn[dT<0], marker='v',s=15)
        # depend on the way but retrieve the value where it cross 0.5
        if(Vn[0]<0.5):
            firstbump=np.where(Vn >= 0.5)[0][0]
        else:
            firstbump=np.where(Vn <= 0.5)[0][0]
        lineaxis=np.mean(Ts[firstbump-1:firstbump+1])
        dic.append((sample,lineaxis))
        plt.axvline(x=lineaxis,label=f"x={lineaxis}",alpha=0.5)
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
    order=np.argsort(smple)
    smple=smple[order]*100
    press=press[order]
    deprate=deprate[order]
    tc=tc[order]
    plt.plot(smple,tc)
    plt.scatter(smple,tc,c=press,cmap="coolwarm",s=100*deprate**2,marker='o',label="sample")
    plt.colorbar(label=r'$\text{Base pressure of sputtering} \ [ Torr ]$')
    plt.xlabel(r"$P_N \ [\%]$")
    plt.ylabel("deposition rate [nm]")
    plt.title("$T_c$ as a function of partial pressure of N \n for a total volume of 20sccm , power at 70% and 50nm width ")
    plt.xticks(smple)
    plt.legend(loc='best')
    plt.savefig("Tc_Pn.pdf")
    plt.savefig("Tc_Pn.png",dpi=600)
    if show==True:
        plt.show()
Nperc_dep()
T_R()
Tc()
