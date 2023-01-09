## Grant title
Surplus-capturing AMMs --- a feasibility study


## About the team

**Andrew** : Ph.D. Mathematics, 10+ years experience academic research at internationally leading pure research institutions. [MEV research](https://github.com/flashbots/mev-research/blob/main/FRPs/active/FRP-22.md) w/ Flashbots. [awmacpherson.com](https://awmacpherson.com/)  

**Evan**: Mathematician, Data Analyst, DeFi Mechanism Design researcher. Previous research includes bonding curve controller modeling, analysis of RMM-01 LP mechanics, analysis of MEV arbitrage mechanics on POL, and cross margin risk modeling. [evandekim.eth](https://mirror.xyz/evandekim.eth/kowg_VFD7lp5p12C4wcytc2rooVXgKnUwBd-KUKtndQ)

**Mohammed**: Electrical/Electronics Engineer. MSc Economics focus on Asset pricing and credit cycle modeling. 5+ years in TradFi derivatives trading. Currently researching and building digital asset focused algorithmic trading/market making algorithms, PBS research and post-merge ETH testnet development (Ephemery/Holesovice).  

## Grant category

Analytics and Integrations  

## Grant description

###  Background

The proposal builds on a [thread in the COW forum](https://forum.cow.fi/t/cow-native-amms-aka-surplus-capturing-amms-with-single-price-clearing/1219) about a CoW-specific form of [MEV-capturing AMM](https://ethresear.ch/t/mev-capturing-amm-mcamm/13336). The discussion surfaced exciting prospects for AMM designs that promise to take back control of "surplus" value ordinarily captured by arbitrageurs and MEV searchers. This value can then be deployed, for example, to achieve better prices for users and an improved overall return profile for LPs than the traditional CFMM.


### The surplus distribution problem

In the classic CFMM design, prices are updated by arbitrageurs who are paid for this service by capturing the price differential between the CFMM and external markets. Liquidity providers (LPs) effectively bear these costs of this by constantly having to accept trades at unfavourable prices, a phenomenon known to economists as adverse selection. Although these costs can be offset by trading fees, this approach to value allocation is limited in two ways:

- Linear trading fees equally impact arbitrageurs and “noise traders” who may be prepared to trade at prices favourable to LPs.
- Arbitrageurs compete only for positioning of their transactions in the block, and the proceeds of this competition goes to block producers rather than LPs. There is no room for a competitive market for updating prices.

The CoW batch auction provides a more flexible approach to delivering price information which distinguishes arbitrageurs (or “solvers”) from noise traders and permits new dimensions of competition on price discovery. On the other hand, the CoW protocol as it stands does not provide its own liquidity, and in practice most of the liquidity comes from standard CFMMs whos LPs suffer adverse selection by trading with the CoW solver.

The basic idea of this proposal is to evaluate the feasibility and impact of an approach to AMM design which custodies its own liquidity but uses the pricing discovered by CoW solvers. Such an AMM would be quite remarkable in that it would provide a way to earn yield for LPs from passive liquidity provision without exposure to adverse selection at the some time offer better pricing for CoW users. Given the power of this result, it is natural to expect that some challenges lie in its realisation.

In our view, a feasibility study is necessary because of apparent confusion about the nature of the value that could be captured by such an AMM, undefined aspects of its design, and the [security](https://samczsun.com/so-you-want-to-use-a-price-oracle/) [implications](https://jumpcrypto.com/so-you-still-want-to-use-a-price-oracle/) of using the CoW solution as a price oracle for an external protoocol. 


## References

-   Price volatility impact on LPs studied by Milionis et al. in LVR (paper titled: Automated Market Making and Loss-Versus-Rebalancing) ([https://arxiv.org/abs/2208.06046](https://arxiv.org/abs/2208.06046))
    
-   Presentations by authors discussing LVR further ([https://www.youtube.com/watch?v=G8qxxlqvMBk](https://www.youtube.com/watch?v=G8qxxlqvMBk)) ([https://www.youtube.com/watch?v=q5vyJJb-Uyw&list=PLEGCF-WLh2RK2Cym4ZeEWDOSlmirXWtZO&index=34](https://www.youtube.com/watch?v=q5vyJJb-Uyw&list=PLEGCF-WLh2RK2Cym4ZeEWDOSlmirXWtZO&index=34))
    
-   Surplus capturing AMM can be traced back to research proposal on MEV-capturing AMM designs ([https://ethresear.ch/t/mev-capturing-amm-mcamm/13336/22](https://ethresear.ch/t/mev-capturing-amm-mcamm/13336/22)) ([https://ethresear.ch/t/mev-minimizing-amm-minmev-amm/13775](https://ethresear.ch/t/mev-minimizing-amm-minmev-amm/13775))
    
-   Paper provides formal specification of implementation of MEV-capturing AMM ([https://arxiv.org/pdf/2210.10601.pdf](https://arxiv.org/pdf/2210.10601.pdf))
    
-   Paper details math behind using external price oracle in standard CPMM ([https://anrg.usc.edu/www/papers/dynamicautomation.pdf](https://anrg.usc.edu/www/papers/dynamicautomation.pdf))
    
-   Forum proposal continues ideas on McAMMs, using fees as main tool for capturing LVR for LPs ([https://ethresear.ch/t/dynamic-mev-capturing-amm-dmcamm/13849](https://ethresear.ch/t/dynamic-mev-capturing-amm-dmcamm/13849))


## Grant goals and impact 

- Propose high-level candidate architectures for “surplus-capturing” AMMs. In particular, address whether changes to CoW protocol itself are needed. Investigate security considerations, economic and otherwise, of the proposed architectures and discuss mitigation strategies.

- Develop a quantitative model of the additional value that could be captured and delivered to LPs and users and measure it through empirical studies and simulations.


**Deliverable** A technical report outlining relevant theoretical background, design considerations, metrics, and results of empirical studies. GitHub repository containing the code used for data studies.

**Impact** The study will provide evidence as to whether current COW tools such as the competitive solver pricing can be utilized to build a surplus-capturing AMM in practise. It will also analyze the kind of "surplus" it would capture, its size, and the extra value users and LPs expect to receive. Thus preparing the ground for detailed design implementation.  


## Milestones 

- Architecture. Specify candidate architectures (which will be used to define simulations and economic attacks). Discuss:

    - How prices are communicated from solver to AMM.

    - How LP portfolios are managed.
    - Block/batch synchronisation.


- Security. Study attack scenarios and propose mitigation strategies. Discuss fallbacks in case of a delayed or missing oracle update.

- Quantitative. Compare portfolio metrics of LPs in proposed designs with those of a traditional CFMM using historical market data. Clarify the relation of these quantities to LVR.

- Quantitative. Evaluate the use of COW solvers as an oracle for an arbitrage-free price by comparing the performance of COW solvers with other approaches to computing this price.

## Grant timeline

6--8 weeks 

## Budget breakdown 

Upfront: 15k XDAI

Upon completion: 6k XDAI / 150k COW (12month linear vesting)


 
## Gnosis chain Address 

To be disclosed to grants team


