PminRc = 0.5 #ZEPH
total_reserves = 0 # 0 ZEPH in reserve
number_stable_coins = 0 # 0 ZUSD in circulation
number_reserve_coins = 0 # 0 ZRSV in circulation
spot = 0
ma = 0
fee = 0.02

def print_state():
    sc_spot, sc_ma = get_stable_price()
    rc_spot, rc_ma = get_reserve_price()
    print('\n======= Network State =======')
    print('Price ZEPH:       spot$', spot)
    print('                  ma$', ma)
    print('Price ZephUSD     spot', sc_spot, 'ZEPH')
    print('                  ma', sc_ma, 'ZEPH')
    print('Price ZephRSV     spot', rc_spot, 'ZEPH')
    print('                  ma', rc_ma, 'ZEPH')  
    print('-----------------------------')
    print('Reserve:             ', total_reserves, 'ZEPH')
    print('                    $', total_reserves * spot)
    print('                  ma$', total_reserves * ma)
    print('-----------------------------')
    print('Number Stable Coins: ', number_stable_coins)
    print('Number Reserve Coins:', number_reserve_coins)
    print('Reserve Ratios(s/ma):', reserve_ratio())
    print('==============================\n')

def get_stable_price(): #in terms of ZEPH
    global spot
    global ma
    rr_spot, rr_ma = reserve_ratio()
    # When rr < 1 then use "worst case stable price (R/Nsc)"
    if number_stable_coins == 0:
        return 1/spot, 1/ma
    worst_case_stable_price = total_reserves / number_stable_coins
    if rr_spot >= 1 and rr_ma >= 1:
        return 1/spot, 1/ma
    elif rr_spot >= 1 and rr_ma < 1:
        return 1/spot, worst_case_stable_price
    elif rr_spot < 1 and rr_ma >= 1:
        return worst_case_stable_price, 1/ma
    else:
        return worst_case_stable_price, worst_case_stable_price

# mint_stable
def get_mint_stable_amount(tx_zeph_amount):
    sc_spot, sc_ma = get_stable_price()
    return tx_zeph_amount / max(sc_spot, sc_ma)

# redeem_stable
def get_redeem_stable_amount(tx_zusd_amount):
    sc_spot, sc_ma = get_stable_price()
    return tx_zusd_amount * min(sc_spot, sc_ma)

def get_reserve_price(): #in terms of ZEPH
    global spot
    global ma
    global PminRc
    equity_spot, equity_ma = equity()
    if number_reserve_coins == 0:
        return PminRc, PminRc
    rc_spot = max(equity_spot / number_reserve_coins, PminRc)
    rc_ma = max(equity_ma / number_reserve_coins, PminRc)

    return rc_spot, rc_ma

# mint_reserve
def get_mint_reserve_amount(tx_zeph_amount):
    rc_spot, rc_ma = get_reserve_price()
    return tx_zeph_amount / max(rc_spot, rc_ma)

# redeem_reserve
def get_redeem_reserve_amount(tx_zrsv_amount):
    rc_spot, rc_ma = get_reserve_price()
    return tx_zrsv_amount * min(rc_spot, rc_ma)

def reserve_ratio():
    global total_reserves
    global number_stable_coins
    if number_stable_coins != 0:
        rr_spot = total_reserves * spot / number_stable_coins
        rr_ma = total_reserves * ma / number_stable_coins
    else:
        rr_spot = rr_ma = float('inf')
    return rr_spot, rr_ma

def reserve_ratio_check(total_reserves, number_stable_coins):
    if number_stable_coins != 0:
        rr_spot = total_reserves * spot / number_stable_coins
        rr_ma = total_reserves * ma / number_stable_coins
    else:
        rr_spot = rr_ma = float('inf')
    return rr_spot, rr_ma

def equity():
    global total_reserves
    global number_stable_coins
    global spot
    global ma

    equity_spot = total_reserves - number_stable_coins / spot
    equity_ma = total_reserves - number_stable_coins / ma
    print("equity called")
    print('\tequity_spot', equity_spot)
    print('\tequity_ma', equity_ma)
    return equity_spot, equity_ma

def price_target_rc(tt):
    global number_reserve_coins
    try:
        return equity(tt) / number_reserve_coins
    except ZeroDivisionError:
        return None

def buying_price_rc(tt):
    global PminRc
    ptrc = price_target_rc(tt)
    if ptrc is None: #check if ptrc is undefined
        return PminRc
    else:
        return max(ptrc, PminRc)
    
    
def mint_stable_coins(tx_zeph_amount):
    global total_reserves
    global number_stable_coins

    new_total_reserves = total_reserves + tx_zeph_amount
    sc_received = get_mint_stable_amount(tx_zeph_amount) * (1-fee)
    new_number_stable_coins = number_stable_coins + sc_received

    rr_spot, rr_ma = reserve_ratio_check(new_total_reserves, new_number_stable_coins)
    print(f'Called -> mint_stable_coins({tx_zeph_amount})')
    print(f'        r: {rr_spot}')
    print(f'        r24: {rr_ma}')
    if rr_spot < 4 or rr_ma < 4:
        print('Action denied: Reserve ratios must be above 4.0 to mint stable coins.')
        return

    total_reserves = new_total_reserves
    number_stable_coins = new_number_stable_coins
    return sc_received

def redeem_stable_coins(tx_zusd_amount):
    global total_reserves
    global number_stable_coins

    zeph_received = get_redeem_stable_amount(tx_zusd_amount) * (1-fee)
    total_reserves -= zeph_received
    number_stable_coins -= tx_zusd_amount
    return zeph_received

def mint_reserve_coins(tx_zeph_amount):
    global total_reserves
    global number_reserve_coins

    new_total_reserves = total_reserves + tx_zeph_amount
    rc_received = get_mint_reserve_amount(tx_zeph_amount)
    new_number_reserve_coins = number_reserve_coins + rc_received

    rr_spot, rr_ma = reserve_ratio_check(new_total_reserves, number_stable_coins)
    print(f'Called -> mint_reserve_coins({tx_zeph_amount})')
    print(f'        r: {rr_spot}')
    print(f'        r24: {rr_ma}')
    if (rr_spot > 8 or rr_ma > 8) and (number_stable_coins != 0):
        print('Action denied: Reserve ratios must be below 8.0 to mint reserve coins.')
        return

    total_reserves = new_total_reserves
    number_reserve_coins = new_number_reserve_coins
    return rc_received

def redeem_reserve_coins(tx_zrs_amount):
    global total_reserves
    global number_reserve_coins
    global number_stable_coins
    zeph_received = get_redeem_reserve_amount(tx_zrs_amount)

    new_total_reserves = total_reserves - zeph_received
    new_number_reserve_coins = number_reserve_coins - tx_zrs_amount

    rr_spot, rr_ma = reserve_ratio_check(new_total_reserves, number_stable_coins)
    print(f'Called -> redeem_reserve_coins({tx_zrs_amount})')
    print(f'        r: {rr_spot}')
    print(f'        r24: {rr_ma}')
    if (rr_spot < 4 or rr_ma < 4) and number_stable_coins != 0:
        print('Action denied: Reserve ratios must be above 4.0 to redeem reserve coins.')
        return

    total_reserves = new_total_reserves
    number_reserve_coins = new_number_reserve_coins
    return zeph_received

### scenarios
def scenario_1():
    print('situation1 - Hardfork success and conversions are activated. Values initialized to 0')
    global total_reserves 
    global number_stable_coins
    global number_reserve_coins
    global spot
    global ma

    total_reserves = 0 # 0 ZEPH in reserve
    number_stable_coins = 0 # 0 ZUSD in circulation
    number_reserve_coins = 0 # 0 ZRSV in circulation
    spot = 2 # 1 ZEPH = $2
    ma = 1.5 # 1 ZEPH = $1.5

    #print starting values
    print_state()

    print('2. Mint 2000 ZRSV at price PminRC')

    tx_zeph_amount_spent = 1000
    rc_recevied = mint_reserve_coins(tx_zeph_amount_spent)
    print('rc_recevied: ', rc_recevied)

    print_state()

    print('3. Mint stable coins at the min of spot and MA.')

    tx_zeph_amount_spent = 300
    sc_received = mint_stable_coins(tx_zeph_amount_spent)
    print('sc_received: ', sc_received)

    print_state()

    print('4. Mint ZRSV for 200 ZEPH')

    tx_zeph_amount_spent = 200
    rc_recevied = mint_reserve_coins(tx_zeph_amount_spent)
    print('rc_recevied: ', rc_recevied)

    print_state()

    print('5. Redeem 200 reserve coins')

    tx_zrs_amount_spent = 200
    zeph_received = redeem_reserve_coins(tx_zrs_amount_spent)
    print('zeph_received: ', zeph_received)

    print_state()

    print('6. Redeem 250 stable coins')

    tx_zusd_amount_spent = 250
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('zeph_received: ', zeph_received)

    print_state()

    print('7. Redeem remaining stable coins')

    tx_zusd_amount_spent = number_stable_coins
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('zeph_received: ', zeph_received)

    print_state()

    print('8. Redeem remaining reserve coins')

    tx_zrs_amount_spent = number_reserve_coins
    zeph_received = redeem_reserve_coins(tx_zrs_amount_spent)
    print('zeph_received: ', zeph_received)

    print_state()


def scenario_2():
    #worst case - reserve ratio < 1
    print('1. init state')
    global total_reserves 
    global number_stable_coins
    global number_reserve_coins
    global spot
    global ma

    total_reserves = 1000 # 0 ZEPH in reserve
    number_stable_coins = 500 # 0 ZUSD in circulation
    number_reserve_coins = 1000 # 0 ZRSV in circulation
    spot = 2 # 1 ZEPH = $2
    ma = 1.5 # 1 ZEPH = $1.5

    print_state()

    print('1. 100 stables are redeemed - reserve ratios (5.0,3.75)')

    tx_zusd_amount_spent = 100
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('\nzeph_received: ', zeph_received)
    print('received_dollar_value_spot: $', round(zeph_received * spot,2))
    print('received_dollar_value_ma: $', round(zeph_received * ma,2))

    print_state()

    print('2. spot price suddenly drops to $30c - reserve ratio < 1')

    spot = .3

    print_state()

    print('3. redeem 100 stable - rr_spot <1 but MA unaffected')

    tx_zusd_amount_spent = 100
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('\nzeph_received: ', zeph_received)
    print('received_dollar_value_spot: $', round(zeph_received * spot,2))
    print('received_dollar_value_ma: $', round(zeph_received * ma,2))

    print_state()

    print('4. redeem 200 stable - MA affected and = Spot')

    ma = .3

    print_state()

    tx_zusd_amount_spent = 200
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('\nzeph_received: ', zeph_received)
    print('received_dollar_value_spot: $', round(zeph_received * spot,2))
    print('received_dollar_value_ma: $', round(zeph_received * ma,2))


    print('5. Spot price recovered but ma still low')

    spot = 1.5

    print_state()

    print('6. redeem 100 stables')

    tx_zusd_amount_spent = 100
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('\nzeph_received: ', zeph_received)
    print('received_dollar_value_spot: $', round(zeph_received * spot,2))
    print('received_dollar_value_ma: $', round(zeph_received * ma,2))

    print_state()

def scenario_3():
    #worst case - reserve ratio < 1
    print('1. init state scenario_3')
    global total_reserves 
    global number_stable_coins
    global number_reserve_coins
    global spot
    global ma

    total_reserves = 0 # 0 ZEPH in reserve
    number_stable_coins = 0 # 0 ZUSD in circulation
    number_reserve_coins = 0 # 0 ZRSV in circulation
    spot = 2 # 1 ZEPH = $2
    ma = 1.8 # 1 ZEPH = $1.5

    print_state()

    print('1. mint 1000 ZRSV at price PminRC')

    tx_zeph_amount_spent = 1000
    rc_received = mint_reserve_coins(tx_zeph_amount_spent)
    print('\nrc_received: ', rc_received)

    print_state()

    print('2. stables are minted from 300 ZEPH')

    tx_zeph_amount_spent = 300
    sc_received = mint_stable_coins(tx_zeph_amount_spent)
    print('\nsc_received: ', sc_received)

    print_state()

    print('3. spot and ma price increases')

    spot = 3
    ma = 2.5

    print_state()


    print('4. more stables are minted from 100 ZEPH after price increase')

    tx_zeph_amount_spent = 100
    sc_received = mint_stable_coins(tx_zeph_amount_spent)
    print('\nsc_received: ', sc_received)

    print_state()


    print('5. all stables are redeemed')

    tx_zusd_amount_spent = number_stable_coins
    zeph_received = redeem_stable_coins(tx_zusd_amount_spent)
    print('\nzeph_received: ', zeph_received)
    print('received_dollar_value_spot: $', round(zeph_received * spot,2))
    print('received_dollar_value_ma: $', round(zeph_received * ma,2))

    print_state()

    print('6. all reserve coins are redeemed')

    tx_zrs_amount_spent = number_reserve_coins
    zeph_received = redeem_reserve_coins(tx_zrs_amount_spent)
    print('\nzeph_received: ', zeph_received)
    print('received_dollar_value_spot: $', round(zeph_received * spot,2))
    print('received_dollar_value_ma: $', round(zeph_received * ma,2))

    print_state()


# scenario_1()
# scenario_2()
scenario_3()


