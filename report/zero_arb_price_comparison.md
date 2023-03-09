# 3. COW Pricing vs the wider Crypto Markets. Zero-arb price assessment.


By definition, choosing the reference market, dictates which market the Feedlot AMM aims to minimize LVR with. Since this study is focused the use of COW pricing as the reference price, it is worth assessing the choice of the COW solver competition price and to what extent it eliminates arb with the wider market. 

It is fair to assume a lot of price discovery originates in off-chain trading avenues given the difference in volumes. (1) Add reference. However, we are particularly interested in on-chain trading. Users of an Ethereum native protocol like COW protocol are settling on-chain. With projects like Univ3 that allow the LP to be more active, very similar to how a market maker is active on a CEX, we believe these reduce the frictions between cex markets and dex markets allowing for better passthrough of off chain price discovery. However, the real area of interest here is the on-chain user. To them, trading on one venue ideally abstracts away all the CEX-DEX aand DEX-DEX discrepancies into one on-chain price. COW protocol has the potential to be this price that abstracts these away, and offers the best price that is non-arbitrageable. Or in short, the zero-arb price. (2) Add reference for zero-arb pricing. 

In order to assess this claim quantitatively, we compare 1) COW on-chain settlement prices with other on-chain pricing settlements and 2) COW to CEX pricing. 

The COW pricing mechanism through the batch auction, and solver competition, should always offer the best on-chain price, by design. The winning price should be the best price for the user. In practise, it is fair to assume there are other considerations. Because prices are registered on-chain through the block builder, it might not always be the case that the COW price is the best price in the block. Solvers do account for MEV, volatility, current mempool transaction in their solutions, but there might be other sources of block-related randomness that could happen. By comparing COW on-chain settlements, we are also shedding light on how good the solvers are at dealing and mitigating this block-related randomness. Where this study can be expanded to compare COW protocol with many other DEXs, we chose UNIV3 as an initial study. 

Where it might be unfair to compare COW pricing with CEX pricing, or perhaps any on-chain pricing with CEX in general because they are not the same markets. However, with UNIv3 protocols, and solvers perhaps mirroring CEX pricing on to the batches, and other market making activities, it is also of interest to make those comparisons. If CEX pricing was consistently much worse for the user for example, then users continued trading off-chain is economically justified. For this study we chose Binance as the target comparison market given that according to sources(3), they are doing the highest trading volumes. (whether you believe in the numbers or not). 

**On-Chain study: UNIv3 trade by trade** 

Given that we are only interested in true comparison, the dataset is filtered to only COW trades that have a corresponding UNIv3 trade in the same block, same buy token, same sell token, meaning we are only interested in trades that have the same direction too as it is not fair to compare sells with buys. This roughly reduces the dataset to around 2.7% of original dataset size. 
Another concern is that these trades that match the block, direction and token addresses, but might not be in comparable size brackets. This means we might be comparing a COW trade with volume of few hundreds with a UNIv3 trade that might in the hundreds of thousands. This is not fair for the UNIv3 pricing since the larger trades should have higher price impact. To deal with this concern, we construct the volume weighted average of the block when more than one trade is present. This levels the comparison. Moreover, we also compare the COW price with the best price in the block. 

The results for the following sample are as given as follows:

Starting Date:
Ending Date: 
Days: 
Number of COW trades: 
Number of matching trades: 

Total Volume of COW trades:
Volume of matching trades? 

% COW better than best block price: 
Average better: 
Average worse: 

% COW better than VWAP price: 
Average better:
Average worse: 

The results show that COW pricing is indeed better on the whole than other on-chain avenues. 

It is more curious however to explore why there are times when it is not. This however would make an excellent follow up extension to this study. 


**Off-chain study: COW vs Binance** 

