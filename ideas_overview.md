### Overview  
-------------------- 

#### Current AMMs: LVR is the devil. 

Traditional AMM LPs suffer from a cost which is becoming more formalized as LVR. Essentially it is the arbitrage the informed traders capture at the expense of the LPs of the AMM. The reason LVR exists is due to the AMM's inability to adjust its pricing on its own outside the constant function. Hence, with volatility the pricing of the AMM lags behind giving an opening to arbitraguers to come in and benefit from this mispricing to the detriment of the LPs. The paper below provides a formal definition and applies it to different trading functions in CFMMs. See:   
https://arxiv.org/abs/2208.06046  
https://a16zcrypto.com/lvr-quantifying-the-cost-of-providing-liquidity-to-automated-market-makers/    
Also these videos summarise the issue nicely and have helped me understand the lVR idea better:     
https://www.youtube.com/watch?v=G8qxxlqvMBk  
https://www.youtube.com/watch?v=q5vyJJb-Uyw&list=PLEGCF-WLh2RK2Cym4ZeEWDOSlmirXWtZO&index=34  

An interesting question is how does LVR relate to impermenant loss? And the short answer as I understand is they are not related. If the price moves up 20% and comes back then IL is 0. Whereas some LVR might have been realized and is indeed permenant. 

So how do we counteract this LVR? The solution is straightforward: provide a high frequency pricing oracle to the AMM that would allow it to adjust pricing quicker than arbitraguers are able to, thereby protecting the LP from losing money.   
https://anrg.usc.edu/www/papers/dynamicautomation.pdf

Another interesting mechanism is to adjust the fees in the CFMM formula. In CPMM this is: 

	(X+s*dx)(y-dy)= k          where s is the fees.  

The fees can be dynamic. Allowing them to be dependent on some form of volatility measure. The main advantage to dynamic fees is that you abstract the whole LVR story in one variable: the fees. No need to change the CFMM function. It also avoids the messy complications of choosing a suitable oracle. The main issue however, is that in some designs the user might not know in advance what fees they will get charged, because they dont know who else is trading in the same block and hence what impact on the fees might happen. There also isnt a straightforward way to measure volatility, thereby opening the space for creativity. This proposal finds an interesting mechanism that seems somewhat similar to how modern LBP pools launch new tokens.    
https://ethresear.ch/t/dynamic-mev-capturing-amm-dmcamm/13849
 

So in summary, the reason LVR exists is because AMMs cannot act on their own. Only users (swappers and arbitraguers) can. The first person to trade will capture this LVR opportunity. We can however eliminate the opportunity all together by designing an AMM with pricing oracles and/or dynamic fees. But what if we want to avoid these two solutions all together? There is a third way. 


If we auction the right to trade first, in order to capture this opportunity, then the AMM will have a direct mechanism of transferring this LVR captured by this "first user" to the AMM LPs. Thats because this user had to quickly assess the Expected Value of the LVR opportunity and bid in the auction with that figure in mind. Who is most able to take part in this auction and price the LVR? "professionals"? Market makers? Could this person be the block builder themselves? 


#### Block builders: Does LVR == MEV? 

Block builders are emerging as the key holders to transaction ordering in the block. This is the current reality and is likely to become even more so with PBS. Block builders are competing to produce the most profitable block. So what role does the block builder play in future versions of AMMs? Are they key players? The authors of these forum entries below think so. And they think so because being the first to trade on an AMM gets to capture the lVR. And since we move in blocks, the first to trade ordering needs to also be enforced at the block level. Block builders have the power to guarantee this. Hence the link to the block builder. The block builder needs to sit on the table.   
https://ethresear.ch/t/mev-capturing-amm-mcamm/13336/22  
https://ethresear.ch/t/mev-minimizing-amm-minmev-amm/13775
  

So if the right to first trade in the block gives you a chance to capture the LVR, isnt this the MEV too? (at least the MEV that comes from this prticular AMM?) Does LVR=MEV? Is it the same thing? The authors of the McAMMs seem to believe so. Which does make sense but still needs to be formally specified and formally proven. If LVR is indeed just MEV, then I think this is more significant than is currently refelcted. It would be the key thread that connects traditional AMMs and the emerging block building paradigm (PBS). 

The closest thing I have found to an application of this concept is this beautifully titled paper:    
https://arxiv.org/pdf/2210.10601.pdf 

They also adopt the right to first trade approach and value the block builder as the actor who is most able to take part in the auction. However, the main difference to the original McAMM ideas is that the LVR value to be transferred from the "first trader"  to the AMM does not need to be finalized upfront. It can be settled later through a futures contract mechanism. That is my understanding. Please correct me if you understood otherwise. 


#### Batch Auctions: UCP and the dream of eliminating MEV  

The main feature of a Batch auction is the Uniform Clearing Price (UCP). This means there is only one price per asset in the batch. Meaning that order of transactions within one batch does not matter. So even if you front run my order, we both get the same price. Current batch times in COW are 30 seconds, and eventually the batch time will drop to match the block time achievinng one block = one batch. Given we are still on around 25-30% capacity currently, it might be a while until we head towards this new reality (but hopefully not a long while). 

This is another example of batching & dreaming of MEV elimination:   
https://eprint.iacr.org/2022/155.pdf

It is a batched trade DEX using commit-reveal-settle cycles. The batching eliminates MEV.


#### Design Ideas & Questions

* There are three ways to capture LVR. 1) A high frequency price oracle reflecting the best price (for the LP) in the market. 2) Dynamic fees that take some measure of volatility as an input. 3) Auction the right to first trade. I am not sure if there are any other ideas out there. (Does anyone know or can think of any other innovative ways?)
 
* First, Could we substitute the high frequency pricing oracle and use the COW solvers best price as the oracle to eliminate LVR? I believe the answer is no. Using the COW solver price as a pricing oracle into a COW native AMM does not eliminate LVR because solvers compete to find the best pricing for the users not the LPs. So an oracle will simply reflect the worst (in the eyes of the LP) available pricing in the market. 
 
* 
