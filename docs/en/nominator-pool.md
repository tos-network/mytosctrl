# Nominator pool

## Running the validator in nominator pool mode

1. Prepare the hardware for the validator - 8 vCPUs, 64GB memory, 1TB SSD, Fixed IP address, 1Gb/s.

   To maintain network stability, it is recommended to distribute validator nodes in different locations around the world and not to concentrate them in one data center.

   > Your hardware must comply with the specified configuration or be higher. Do not run the validator on weak hardware - this negatively affects the network and you will be fined.

   > **Recommended providers:** [amazon](https://aws.amazon.com/), [digitalocean](https://www.digitalocean.com/), [linode](https://www.linode.com/), [alibaba cloud](https://alibabacloud.com/), [latitude](https://www.latitude.sh/).

2. Install and sync **mytosctrl** as described in https://github.com/tos-network/mytosctrl/blob/master/docs/en/manual-ubuntu.md **only** paragraph 1, 2 and 3.


3. Send 1 TOS to validator wallet address displayed in the list `wl`.

4. Type `aw` to activate validator wallet.

5. Create two pools (for even and odd validation round):
   ```
   new_pool p1 0 1 1000 300000
   new_pool p2 0 1 1001 300000
   ```
   where
    * `p1` is pool name;
    * `0` % is validator reward share (e.g. use 40 for 40%);
    * `1` is max nominators count in the pool (should be <= 40);
    * `1000` TOS is minimum validator stake (should be >= 1K TOS);
    * `300000` TOS is minimum nominator stake (should be >= 10K TOS);

   > (!) Pools configurations don't have to be identical, you can add 1 to the minimum stake of one pool to make them different.

6. Type `pools_list` to display pools addresses:

   ```
   pools_list
   Name  Status  Balance  Address
   p1    empty   0        0f98YhXA9wnr0d5XRXT-I2yH54nyQzn0tuAYC4FunT780qIT
   p2    empty   0        0f9qtmnzs2-PumMisKDmv6KNjNfOMDQG70mQdp-BcAhnV5jL
   ```

7. Send 1 TOS to each pool and activate the pools:
   ```
   mg validator_wallet_001 0f98YhXA9wnr0d5XRXT-I2yH54nyQzn0tuAYC4FunT780qIT 1
   mg validator_wallet_001 0f9qtmnzs2-PumMisKDmv6KNjNfOMDQG70mQdp-BcAhnV5jL 1
   activate_pool p1
   activate_pool p2
   ```

8. Type `pools_list` to display pools:
   ```
   pools_list
   Name  Status  Balance      Address
   p1    active  0.731199733  kf98YhXA9wnr0d5XRXT-I2yH54nyQzn0tuAYC4FunT780v_W
   p2    active  0.731199806  kf9qtmnzs2-PumMisKDmv6KNjNfOMDQG70mQdp-BcAhnV8UO
   ```

9. Open each pool by link "https://tosscan.org/nominator/<address_of_pool>" and verify pools configuration.

10. Make validator deposit to each pool:
    ```
    deposit_to_pool validator_wallet_001 <address_of_pool_1> 1005
    deposit_to_pool validator_wallet_001 <address_of_pool_2> 1005
    ```
    where `1005` TOS is deposit amount. Please note that 1 TOS will be debited by the pool for deposit processing.


11. Make nominator deposit to each pool:

    Go to the pool link (**9th step**) and click **ADD STAKE**.
    You can also make a deposit using **mytosctrl**, use the commands below to do so.

    ```
    mg nominator_wallet_001 <address_of_pool_1> 300001 -C d
    mg nominator_wallet_001 <address_of_pool_2> 300001 -C d
    ```

    > (!) The nominator wallet must be initialized in basechain (workchain 0).

    > (!) Keep in mind that the validator wallet and nominator wallet must be stored separately! Validator wallet is stored on the server with validator node, to ensure processing of all system transactions. The nominator wallet is stored on your cold cryptocurrency wallet.

    > To withdrawal a nominator deposit, send a transaction with the comment `w` to the pool address (1 TOS must be attached to process the transaction). You can also do this with **mytosctrl**.

13. Activate pool mode:
    ```
    set usePool true
    ```

14. Invite nominators to make deposits to your pools. Participation in validation will start automatically.
    > (!) You need to have at least 200 TOS/month on validator wallet for operation fees.

## Pools configuration

If you want to lend to yourself then use `new_pool p1 0 1 1000 300000` (1 nominator maximum, 0% validator share).

If you are creating a pool for many nominators then use something like this: `new_pool p1 40 40 10000 10000` (40 nominators maximum, 40% validator share, 10K TOS minimum participant stakes).

## Switching a regular validator to nominator pool mode

1. Type `set stake 0` to disable participation in elections.

2. Wait for both of your stakes to return from the elector.

3. Complete the "Running the validator in nominator pool mode" steps starting from the **4th** step.
