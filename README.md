# pyzeph
This repo showcases the functions used in Zephyr Protocol conversions, inspired by Djed.

pyzeph is a Python script designed to simulate and analyze the dynamics of Zephyr Protocol. 

The library provides functionality to create and execute various scenarios, giving the ablity to walkthrough how the Protocol is implemented in Zephyr.
It gives the ablity to simulate different network states and is used internally for reference.

### Features
- Construct and execute custom simulation scenarios involving minting and redeeming actions.
- Comprehensive analysis and reporting on the outcomes of scenarios.
- Gives insight on how core functions and calculations work
- Support for understanding the performance of the protocol in various market conditions.

### Usage
Get hands on and create your own scenario!
use `print_state()` to see the network state pre and post any actions.

### Actions
`mint_stable`

`redeem_stable`

`mint_reserve`

`redeem_reserve`

```
======= Network State =======
Price ZEPH:       spot$ 2
                  ma$ 1.8
Price ZephUSD     spot 0.5 ZEPH
                  ma 0.5555555555555556 ZEPH
Price ZephRSV     spot 0.5 ZEPH
                  ma 0.5 ZEPH
-----------------------------
Reserve:              1000 ZEPH
                    $ 2000
                  ma$ 1800.0
-----------------------------
Number Stable Coins:  0
Number Reserve Coins: 2000.0
Reserve Ratios(s/ma): (inf, inf)
==============================

2. stables are minted from 300 ZEPH
Called -> mint_stable_coins(300)
        r: 4.91307634164777
        r24: 4.421768707482993

sc_received:  529.2
equity called
        equity_spot 1035.4
        equity_ma 1006.0

======= Network State =======
Price ZEPH:       spot$ 2
                  ma$ 1.8
Price ZephUSD     spot 0.5 ZEPH
                  ma 0.5555555555555556 ZEPH
Price ZephRSV     spot 0.5177 ZEPH
                  ma 0.503 ZEPH
-----------------------------
Reserve:              1300 ZEPH
                    $ 2600
                  ma$ 2340.0
-----------------------------
Number Stable Coins:  529.2
Number Reserve Coins: 2000.0
Reserve Ratios(s/ma): (4.91307634164777, 4.421768707482993)
==============================
```
