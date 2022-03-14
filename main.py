# Library
from functions import *

# Process
print("Start Process")
try:
    # Open Chrome with MM
    driver = load_chrome_with_mm(MetaMaskHome)
    driver.switch_to.window(driver.window_handles[0])

    # navigate within MM to get to account creation
    navigate_mm(driver, "new")

    # create account
    password, secret_key = create_account(driver)

    # close chrome browser
    driver.quit()

    # open browser
    driver = load_chrome_with_mm(PegaxyWebsite)

    # enable MM plugin
    pin_mm_plugin()
    MetaMaskTab = driver.window_handles[0]
    PegaxyTab = driver.window_handles[1]

    driver.switch_to.window(MetaMaskTab)

    # navigate within MM to get to import wallet
    navigate_mm(driver, "import")
    # import wallet
    import_mm(driver, secret_key, password)
    print("Close browser")
    driver.close()

    time.sleep(2)

    driver.switch_to.window(PegaxyTab)
    # connect to app
    pegaxy_network = connect_pegaxy_app(driver)

    # handle MetaMask
    switch_network_bool = DefaultNetwork in pegaxy_network
    time.sleep(5)

    driver.switch_to.window(driver.window_handles[1])
    approve_mm(driver, not switch_network_bool)

finally:
    # tear down
    print("End Process")
    driver.quit()





