PART 1: OVERVIEW 

1.1 Current AMMs: LVR is the devil. 

Traditional AMM LPs suffer from a cost which is becoming more formalized as LVR. Essentially it is the arbitrage the informed traders capture at the expense of the LPs of the AMM. The reason LVR exists is due to the AMM's inability to adjust its pricing on its own outside the constant function. Hence, with volatility the pricing of the AMM lags behind giving an opening to arbitraguers to come in and benefit from this mispricing to the detriment of the LPs. The paper below provides a formal definition and applies it to different trading functions in CFMMs. 

See https://arxiv.org/abs/2208.06046
https://a16zcrypto.com/lvr-quantifying-the-cost-of-providing-liquidity-to-automated-market-makers/
Also this video summarises the issue nicely and helped me understand it better: 
https://www.youtube.com/watch?v=G8qxxlqvMBk
https://www.youtube.com/watch?v=q5vyJJb-Uyw&list=PLEGCF-WLh2RK2Cym4ZeEWDOSlmirXWtZO&index=34

An interesting question is how does LVR relates to impermenant loss? And the short answer as I understand is they are not related. If the price moves up 20% and comes back then IL is 0. Whereas some LVR might have been realized and is indeed permenant. 

So how do we counteract this LVR? The solution is straightforward: provide a high frequency pricing oracle to the AMM that would allow it to adjust pricing quicker than arbitraguers are able to, thereby protecting the LP from losing money. 
https://anrg.usc.edu/www/papers/dynamicautomation.pdf


Another interesting mechanism is to adjust the fees in the CFMM formula. In CPMM this is: 

(X+dx)(y-sdx)= k where s is fees. 

The fees can be dynamic. Allowing them to be dependent on some form of volatility measure. Dynamic fees main advantage is that you avoid unnecessary complications around choosing oracles and can be more intrinsic. The main issues coming from dynamic fees is that in some designs the user might not know in advance what fees they will get charged (because they dont know who else is trading in the same block and hence what impact on the fees might happen). But its really hard finding a good way to measure volatility. But not impossible. This here finds an interesting mechanism that seems similar to modern LBP pools launching new tokens.
https://ethresear.ch/t/dynamic-mev-capturing-amm-dmcamm/13849
 

So in summary, the reason LVR exists is because of AMMs cannot act on their own. Only users (average swappers and arbitraguers) can. Moreover, who gets to grab this arb opportunity (the lvr) is a matter of transaction ordering. The first person to trade will get to capture this opportunity.  We can however eliminate the oppoortunity all together by designing an AMM with pricing oracles and dynamic fees. But if both these options are not available then transaction ordering to see who captures the opportunity first is the status quo. Maybe if we can have a competition around who gets to trade first, using an auction for example, then we could have a mechanism to capture the LVR from this auction without the oracles nor the dynamic fees. Who is most able to take part in this auction and price the LVR? "professionals" like market makers? Could this person be the block builder themselves? 


1.2 Block builders: Does LVR == MEV? 

Block builders are emerging as the key holders to transaction ordering in the block. This is the current reality and is likely to become even more so with PBS. Transaction ordering of course controls MEV and in turn is governed by economics of its own represented by the auction in MEV Boost. So block builders are competing to produce the most profitable block. So what role does the block builder play in future versions of AMMs? Are they key players? The authors of these forum entries think so. And they think so because being the first to trade on an AMM gets to capture the lVR. And since we Ethereum state moves in blocks, the first to trade needs to be ensured at the block level. (i.e. the first transaction in the block for that particular AMM. Hence we have the link to the block builder. The block builder needs to sit on the table. 

https://ethresear.ch/t/mev-capturing-amm-mcamm/13336/22
https://ethresear.ch/t/mev-minimizing-amm-minmev-amm/13775


The authors of these ideas are advocating the right to first trade approach to the lVR problem. In simple terms, the person who gets to trade first in a block is the person that gets to capture LVR. They also need to price this LVR and quantify it for them to bid in the auction. If the AMM creates a rule that you need to bid to the opportunity to trade first then the AMM would have created a mechanism whereby these professionals price the opportunity and then bid accordingly how much they think this opportunity is worth giving the AMM a chance to capture a decent chunk of this LVR. (if you are an econonomist, and you assume perfect competition, then maybe all the lVR?)  

So if the right to first trade in the block gives you a chance to capture the LVR, isnt this the MEV too? (at least the MEV that comes from this prticular AMM?) Does LVR == MEV? Is it the same thing? The authors of the MCAMMs seem to believe so. Which does make sense but I am still leaving room for skepticism and caution until conclusively proven. If this is true, then I think this is more significant than is currently refelcted. It would be the key thread that connects traditional AMMs and the emerging block building paradigm (PBS). 

The closest thing I have found to an application of this concept is this beautifully titled paper:
https://arxiv.org/pdf/2210.10601.pdf 

They also adopt the right to first trade approach and value the block builder as the actor with most ability to take part in the auction. Which makes sense and is in the same spirit of what a block builder already does in the MEV Boost context. However, the main difference to the original McAMM ideas is that they do not require the LVR to be paid upfront, it can be settles later. That is my understanding. Please correct me if you understood otherwise. 


1.3 Batch Auctions: UCP and the dream of eliminating MEV  

The main feature of a Batch auction is the Uniform Clearing Price (UCP). This means there is only one price per asset in the batch. Meaning that order of transactions within one batch does not matter. So even if you front run my order, we both get the same price. COW protocol offers a fully functioning batch auction guaranteeing UCP within the batch and is a layer on top of the SC layer. Current batch times are 30 seconds and eventually the batch time will drop to match the block time achievinng one block = one batch. Given we are still on around 25-30% capacity  currently it might be a while until we head towards this new reality (but hopefully not a long while). 

This here is an exampe of batching & dreaming of MEV elimination: 

https://eprint.iacr.org/2022/155.pdf

It is a batched trade DEX using commit-reveal-settle cycles. The batching seems to eliminate/reduce MEV. I do not understand the exact details of the settlement and where the fronr run protection comes from. 

 
