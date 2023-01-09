# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 13:08:54 2022

@author: u176198
"""
import pandas as pd
import math
import random
import matplotlib.pyplot as plt




def vaultFuturesStrategy(r0,r1,price,netVault0,netVault1,block,kStart,activeFuturePositions,conversionFrequency,alpha):
    
    r0new=math.sqrt(price*r0*r1)
    r1new=r0new/price
    
    vault0,vault1=0,0
    """"(r1-r1new)>0 means the token 1 has increased in value"""
    if (r1-r1new)>0:

        vault1=vault1+(r1-r1new)*(alpha)
        """"repay the arbitrageur"""
        r0=r0new+(r0-r0new)*(alpha)
        """"rebalance the pool"""
        r1=r0/price
        vault1=vault1+(r1new-r1)
    else:
        vault0=vault0+(r0-r0new)*(alpha)
        """"repay the arbitrageur"""
        r1=r1new+(r1-r1new)*(alpha)
        r0=r1*price
        vault0=vault0+(r0new-r0)
    """settles (1/conversionFrequency) of the active futures contracts"""
    if block % conversionFrequency==0:
        for i in range(0,conversionFrequency):
            valueToBeAdded=activeFuturePositions[i][0]*(price-activeFuturePositions[i][1])
            r0ValueAdd=(valueToBeAdded/2)
            r1ValueAdd=(valueToBeAdded/2)/price
            r0=r0+r0ValueAdd
            r1=r1+r1ValueAdd
        kStart=r0*r1
    if vault0<vault1*price:
        """ this implies price has gone up """
        """apply rebalancing fee to the amount needed to be rebalance, in token1 s"""
        vault1Additional=(vault1-(vault0/price))
        """creates a buy futures contract against the block producer"""
        activeFuturePositions[sim%conversionFrequency]=[vault1Additional/2,price]
        vault0=vault0+(vault1Additional/2)*price
        vault1=(vault1-vault1Additional/2)
        r0=r0+(vault0)
        r1=r1+(vault1)
        newK=r0*r1
        kOverNewK=math.sqrt(kStart/newK)
        netVault0=netVault0+r0*(1-kOverNewK)
        netVault1=netVault1+r1*(1-kOverNewK)
        """Keep the constant constant between blocks"""
        r0=r0*kOverNewK
        r1=r1*kOverNewK
        vault0=0
        vault1=0
    else:
        """ this implies price has gone down """
        """apply rebalancing fee to the amount needed to be rebalance"""
        vault0Additional=(vault0-vault1*price)
        """creates a sell futures contract against the block producer (minus sign) """
        activeFuturePositions[sim%conversionFrequency]=[-(vault0Additional/2)/price,price]
        vault1=vault1+(vault0Additional/2)/price
        vault0=(vault0-vault0Additional/2)
        r0=r0+(vault0)
        r1=r1+(vault1)
        newK=r0*r1
        kOverNewK=math.sqrt(kStart/newK)
        netVault0=netVault0+r0*(1-kOverNewK)
        netVault1=netVault1+r1*(1-kOverNewK)
        """Keep the constant constant between blocks"""
        r0=r0*kOverNewK
        r1=r1*kOverNewK
    return r0,r1,netVault0,netVault1,kStart,activeFuturePositions

def vaultLazyConversionStrategy(r0,r1,price,vault0,vault1,block,conversionFrequency,alpha):
    r0new=math.sqrt(price*r0*r1)
    r1new=r0new/price
    """"(r1-r1new)>0 means the token 1 has increased in value"""
    if (r1-r1new)>0:
        vault1=vault1+(r1-r1new)*(alpha)
        """"repay the arbitrageur"""
        r0=r0new+(r0-r0new)*(alpha)
        """"rebalance the pool"""
        r1=r0/price
        vault1=vault1+(r1new-r1)
        
    else:
        vault0=vault0+(r0-r0new)*(alpha)

        """"repay the arbitrageur"""
        r1=r1new+(r1-r1new)*(alpha)
        r0=r1*price
        vault0=vault0+(r0new-r0)
        
        
    """performs the conversion every conversionFrequency"""
    if block % conversionFrequency==0:
        if vault0<vault1*price:
            
            """ this implies price has gone up """
            vault1Additional=(vault1-(vault0/price))
            vault0=vault0+(vault1Additional/2)*price
            vault1=(vault1-vault1Additional/2)
            r0=r0+(vault0)
            r1=r1+(vault1)
            vault0=0
            vault1=0
        else:
            """ this implies price has gone down """
            """apply rebalancing fee to the amount needed to be rebalance"""
            vault0Additional=(vault0-vault1*price)
            vault1=vault1+(vault0Additional/2)/price
            vault0=(vault0-vault0Additional/2)
            r0=r0+(vault0)
            r1=r1+(vault1)
            vault0=0
            vault1=0
    return r0,r1,vault0,vault1

def addTXFees(r0,r1,transactionFee):
    return r0*(1+transactionFee),r1*(1+transactionFee)



numBlocksPerDay=10
numberOfSimsPerCombination=500

firstSet=[i for i in range(0,numberOfSimsPerCombination)]
secondSet=[i for i in range(numberOfSimsPerCombination,numberOfSimsPerCombination*2)]
thirdSet=[i for i in range(numberOfSimsPerCombination*2,numberOfSimsPerCombination*3)]

results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})

r0start=100000000
r1start=76336
numDaysSimulation=365



blocksForSim=numBlocksPerDay*numDaysSimulation
conversionFrequency=numBlocksPerDay

"""dailyFeesVsK=0.0003 is equiv to 10% TVL trading in a 0.3% fee pool"""
dailyFeesVsK=0

for dailyExpectedVol in [1.05]:
    for alpha in [0.5,0.95]:
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            """Futures Strategy Variables"""
            netVault0Futs=0
            netVault1Futs=0
            r0Futs=r0start
            r1Futs=r1start
            kStartFuts=r0Futs*r1Futs
            
            """Lazy Conversion Strategy Variables"""
            r0Lazy=r0start
            r1Lazy=r1start
            vault0Lazy=0
            vault1Lazy=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=dailyExpectedVol**(1/numBlocksPerDay)
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1))
                    
                r0Futs,r1Futs,netVault0Futs,netVault1Futs,kStartFuts,activeFuturePositions=vaultFuturesStrategy(r0Futs,r1Futs,price,netVault0Futs,netVault1Futs,block,kStartFuts,activeFuturePositions,conversionFrequency,alpha)
                r0Lazy,r1Lazy,vault0Lazy,vault1Lazy=vaultLazyConversionStrategy(r0Lazy,r1Lazy,price,vault0Lazy,vault1Lazy,block,conversionFrequency,alpha)
               
            vaultStrategyValueFuts=(r1Futs+netVault1Futs)*price + r0Futs+netVault0Futs
            vaultStrategyValueLazy=(r1Lazy+vault1Lazy)*price + r0Lazy+vault0Lazy
            
            results=results.append({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLazyConvert":vaultStrategyValueLazy,
                                       "vaultFutures":vaultStrategyValueFuts,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},ignore_index=True)


results["vaultLazyConvert"]=results["vaultLazyConvert"]/results["AMM"]
plt.figure(0)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=results["vaultLazyConvert"].loc[firstSet].values.tolist(),c="magenta",label="0.5")
plt.scatter(x=results["finalPrice"].loc[secondSet].values.tolist(),y=results["vaultLazyConvert"].loc[secondSet].values.tolist(),c="orange",label=" 0.95")
plt.legend(loc="upper left")
plt.title("alpha")
plt.ylabel("Diamond / CFMM")
plt.xlabel("final price")

plt.savefig('C:/Users/U176198/Documents/PhD/Projects/LVR/LVRAlphaComparison.png',dpi=500)

results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})

alpha=0.95
conversionFrequency=numBlocksPerDay
"""dailyFeesVsK=0.0003 is equiv to 10% TVL trading in a 0.3% fee pool"""


for dailyExpectedVol in [1.05]:
    for numDaysSimulation in [365,365*3]:
        blocksForSim=numBlocksPerDay*numDaysSimulation
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            """Futures Strategy Variables"""
            netVault0Futs=0
            netVault1Futs=0
            r0Futs=r0start
            r1Futs=r1start
            kStartFuts=r0Futs*r1Futs
            
            """Lazy Conversion Strategy Variables"""
            r0Lazy=r0start
            r1Lazy=r1start
            vault0Lazy=0
            vault1Lazy=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=dailyExpectedVol**(1/numBlocksPerDay)
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1))
                    
                r0Futs,r1Futs,netVault0Futs,netVault1Futs,kStartFuts,activeFuturePositions=vaultFuturesStrategy(r0Futs,r1Futs,price,netVault0Futs,netVault1Futs,block,kStartFuts,activeFuturePositions,conversionFrequency,alpha)
                r0Lazy,r1Lazy,vault0Lazy,vault1Lazy=vaultLazyConversionStrategy(r0Lazy,r1Lazy,price,vault0Lazy,vault1Lazy,block,conversionFrequency,alpha)
                
            vaultStrategyValueFuts=(r1Futs+netVault1Futs)*price + r0Futs+netVault0Futs
            vaultStrategyValueLazy=(r1Lazy+vault1Lazy)*price + r0Lazy+vault0Lazy
            
            results=results.append({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLazyConvert":vaultStrategyValueLazy,
                                       "vaultFutures":vaultStrategyValueFuts,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},ignore_index=True)


results["vaultLazyConvert"]=results["vaultLazyConvert"]/results["AMM"]
plt.figure(1)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=results["vaultLazyConvert"].loc[firstSet].values.tolist(),c="magenta",label="1 year")
plt.scatter(x=results["finalPrice"].loc[secondSet].values.tolist(),y=results["vaultLazyConvert"].loc[secondSet].values.tolist(),c="orange",label="3 years")
plt.legend(loc="upper left")
plt.title("Lifetime of Pool")
plt.ylabel("Diamond / CFMM")
plt.xlabel("final price")
 
plt.savefig('C:/Users/U176198/Documents/PhD/Projects/LVR/LVRRuntimeComparison.png',dpi=500)

results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})

alpha=0.95
conversionFrequency=numBlocksPerDay
"""dailyFeesVsK=0.0003 is equiv to 10% TVL trading in a 0.3% fee pool"""

results

for dailyExpectedVol in [1.05,1.1,1.15]:
    for numDaysSimulation in [365]:
        blocksForSim=numBlocksPerDay*numDaysSimulation
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            """Futures Strategy Variables"""
            netVault0Futs=0
            netVault1Futs=0
            r0Futs=r0start
            r1Futs=r1start
            kStartFuts=r0Futs*r1Futs
            
            """Lazy Conversion Strategy Variables"""
            r0Lazy=r0start
            r1Lazy=r1start
            vault0Lazy=0
            vault1Lazy=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=dailyExpectedVol**(1/numBlocksPerDay)
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1))
                r0Futs,r1Futs,netVault0Futs,netVault1Futs,kStartFuts,activeFuturePositions=vaultFuturesStrategy(r0Futs,r1Futs,price,netVault0Futs,netVault1Futs,block,kStartFuts,activeFuturePositions,conversionFrequency,alpha)
                r0Lazy,r1Lazy,vault0Lazy,vault1Lazy=vaultLazyConversionStrategy(r0Lazy,r1Lazy,price,vault0Lazy,vault1Lazy,block,conversionFrequency,alpha)
                
            vaultStrategyValueFuts=(r1Futs+netVault1Futs)*price + r0Futs+netVault0Futs
            vaultStrategyValueLazy=(r1Lazy+vault1Lazy)*price + r0Lazy+vault0Lazy
            
            results=results.append({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLazyConvert":vaultStrategyValueLazy,
                                       "vaultFutures":vaultStrategyValueFuts,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},ignore_index=True)



results["vaultLazyConvert"]=results["vaultLazyConvert"]/results["AMM"]
plt.figure(2)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=results["vaultLazyConvert"].loc[firstSet].values.tolist(),c="magenta",label="5%")
plt.scatter(x=results["finalPrice"].loc[secondSet].values.tolist(),y=results["vaultLazyConvert"].loc[secondSet].values.tolist(),c="orange",label="10%")
plt.scatter(x=results["finalPrice"].loc[thirdSet].values.tolist(),y=results["vaultLazyConvert"].loc[thirdSet].values.tolist(),c="green",label="15%")
plt.legend(loc="upper left")
plt.title("Expected Daily Price Move")
plt.ylabel("Diamond / CFMM")
plt.xlabel("final price")

 
plt.savefig('C:/Users/U176198/Documents/PhD/Projects/LVR/LVRVolComparison.png',dpi=500)


results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})

alpha=0.95
numDaysSimulation=365
"""dailyFeesVsK=0.0003 is equiv to 10% TVL trading in a 0.3% fee pool"""
dailyFeesVsK=0.0000

for dailyExpectedVol in [1.05]:
    for conversionFrequency in [numBlocksPerDay,numBlocksPerDay*7]:
        blocksForSim=numBlocksPerDay*numDaysSimulation
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            """Futures Strategy Variables"""
            netVault0Futs=0
            netVault1Futs=0
            r0Futs=r0start
            r1Futs=r1start
            kStartFuts=r0Futs*r1Futs
            
            """Lazy Conversion Strategy Variables"""
            r0Lazy=r0start
            r1Lazy=r1start
            vault0Lazy=0
            vault1Lazy=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=dailyExpectedVol**(1/numBlocksPerDay)
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1)) 
                r0Futs,r1Futs,netVault0Futs,netVault1Futs,kStartFuts,activeFuturePositions=vaultFuturesStrategy(r0Futs,r1Futs,price,netVault0Futs,netVault1Futs,block,kStartFuts,activeFuturePositions,conversionFrequency,alpha)
                r0Lazy,r1Lazy,vault0Lazy,vault1Lazy=vaultLazyConversionStrategy(r0Lazy,r1Lazy,price,vault0Lazy,vault1Lazy,block,conversionFrequency,alpha)
                
            
            vaultStrategyValueFuts=(r1Futs+netVault1Futs)*price + r0Futs+netVault0Futs
            vaultStrategyValueLazy=(r1Lazy+vault1Lazy)*price + r0Lazy+vault0Lazy
            
            results=results.append({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLazyConvert":vaultStrategyValueLazy,
                                       "vaultFutures":vaultStrategyValueFuts,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},ignore_index=True)


results["vaultLazyConvert"]=results["vaultLazyConvert"]/results["AMM"]
plt.figure(3)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=results["vaultLazyConvert"].loc[firstSet].values.tolist(),c="magenta",label="every day")
plt.scatter(x=results["finalPrice"].loc[secondSet].values.tolist(),y=results["vaultLazyConvert"].loc[secondSet].values.tolist(),c="orange",label="every week")
plt.legend(loc="upper left")
plt.title("Conversion Frequency")
plt.ylabel("Diamond / CFMM")
plt.xlabel("final price")
 
plt.savefig('C:/Users/U176198/Documents/PhD/Projects/LVR/LVRConvFreqComparison.png',dpi=500)

print("1 day mean",results["vaultLazyConvert"].loc[firstSet].describe())
print("1 week mean",results["vaultLazyConvert"].loc[secondSet].describe())

results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})

alpha=0.95
numDaysSimulation=365
conversionFrequency=numBlocksPerDay
"""dailyFeesVsK=0.0003 is equiv to 10% TVL trading in a 0.3% fee pool"""
conversionFrequency =numBlocksPerDay

for dailyExpectedVol in [1.05]:
    for dailyFeesVsK in [0,0.00003,0.0003]:
        blocksForSim=numBlocksPerDay*numDaysSimulation
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            """Futures Strategy Variables"""
            netVault0Futs=0
            netVault1Futs=0
            r0Futs=r0start
            r1Futs=r1start
            kStartFuts=r0Futs*r1Futs
            
            """Lazy Conversion Strategy Variables"""
            r0Lazy=r0start
            r1Lazy=r1start
            vault0Lazy=0
            vault1Lazy=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=dailyExpectedVol**(1/numBlocksPerDay)
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1)) 
                r0Futs,r1Futs,netVault0Futs,netVault1Futs,kStartFuts,activeFuturePositions=vaultFuturesStrategy(r0Futs,r1Futs,price,netVault0Futs,netVault1Futs,block,kStartFuts,activeFuturePositions,conversionFrequency,alpha)
                r0Lazy,r1Lazy,vault0Lazy,vault1Lazy=vaultLazyConversionStrategy(r0Lazy,r1Lazy,price,vault0Lazy,vault1Lazy,block,conversionFrequency,alpha)
                
                """add TxFees"""
                r0Lazy,r1Lazy=addTXFees(r0Lazy,r1Lazy,dailyFeesVsK/numBlocksPerDay)
                r0Futs,r1Futs=addTXFees(r0Futs,r1Futs,dailyFeesVsK/numBlocksPerDay)
            
            vaultStrategyValueFuts=(r1Futs+netVault1Futs)*price + r0Futs+netVault0Futs
            vaultStrategyValueLazy=(r1Lazy+vault1Lazy)*price + r0Lazy+vault0Lazy
            
            results=results.append({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLazyConvert":vaultStrategyValueLazy,
                                       "vaultFutures":vaultStrategyValueFuts,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},ignore_index=True)

a=results["vaultLazyConvert"]/results["AMM"]
b=results["vaultFutures"]/results["AMM"]
c=results["HODL"]/results["AMM"]
plt.figure(4)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=a.loc[firstSet].values.tolist(),c="magenta",label="fee = 0%")
plt.scatter(x=results["finalPrice"].loc[secondSet].values.tolist(),y=a.loc[secondSet].values.tolist(),c="orange",label="fee = 0.03%")
plt.scatter(x=results["finalPrice"].loc[thirdSet].values.tolist(),y=a.loc[thirdSet].values.tolist(),c="green",label="fee = 0.3%")
plt.legend(loc="upper left")
plt.title("Fees (Given 10% of pool TVL trades per day)")
plt.ylabel("Diamond / CFMM")
plt.xlabel("final price")
 
#plt.savefig('C:/Users/U176198/Documents/PhD/Projects/LVR/LVRFeeComparison.png',dpi=500)



plt.figure(5)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=a.loc[firstSet].values.tolist(),c="magenta",label="Periodic Conversion Auction")
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=b.loc[firstSet].values.tolist(),c="orange",label="Conversion vs. Futures")
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=c.loc[firstSet].values.tolist(),c="green",label="HODL")
plt.legend(loc="upper left")
plt.title("Fees")
plt.ylabel("Strategy / CFMM")
plt.xlabel("final price")
 
plt.savefig('C:/Users/U176198/Documents/PhD/Projects/LVR/HODL.png',dpi=500)

print("vaultLazyConvert",a.loc[firstSet].describe())
print("vaultFutures",b.loc[firstSet].describe())

