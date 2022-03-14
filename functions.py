# Library
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import random
import string

# Config Variables
MetaMaskExt = "./extension/metamask.crx"
MetaMaskHome = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#initialize/welcome"
PegaxyWebsite = "https://play.pegaxy.io/marketplace"
DefaultNetwork = "Ethereum"
wait_time = 15


def wait_and_click(driver, selector, value):
    wait = WebDriverWait(driver, wait_time)
    wait.until(EC.presence_of_element_located((selector, value)))
    driver.find_element(selector, value).click()


def check_element_exist(driver, selector, value):
    try:
        driver.find_element(selector, value)
    except NoSuchElementException:
        return False
    return True


def load_chrome_with_mm(url):
    # install driver
    s = Service(ChromeDriverManager().install())

    # attach MM ext
    browser_options = webdriver.ChromeOptions()
    browser_options.add_extension(MetaMaskExt)

    # launch chrome
    driver = webdriver.Chrome(service=s, options=browser_options)
    driver.get(url)
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)
    print("Opening chrome with MetaMask Plugin")

    return driver


def generate_password():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(12))
    print("generating Password")
    return password


def create_account(driver):
    print("creating MetaMask account")
    # create password page
    wait = WebDriverWait(driver, wait_time)
    password = generate_password()
    wait.until(EC.presence_of_element_located((By.ID, "create-password")))
    input_password = driver.find_element(By.ID, "create-password")
    input_password.send_keys(password)
    cfm_password = driver.find_element(By.ID, "confirm-password")
    cfm_password.send_keys(password)
    driver.find_element(By.CLASS_NAME, "first-time-flow__checkbox").click()
    driver.find_element(By.CLASS_NAME, "first-time-flow__button").click()

    # get secret phase
    wait_and_click(driver, By.XPATH, "//button[contains(., 'Next')]")

    wait_and_click(driver, By.CLASS_NAME, "reveal-seed-phrase__secret-blocker")

    secret_key = driver.find_element(By.CLASS_NAME, "notranslate")
    secret_key = secret_key.text
    driver.find_element(By.CLASS_NAME, "first-time-flow__button").click()

    print("MetaMask account created")
    return password, secret_key


def import_mm(driver, secret_key, password):
    print("importing MetaMask account")
    wait = WebDriverWait(driver, wait_time)
    wait.until((EC.presence_of_element_located((By.CLASS_NAME, "first-time-flow__import"))))

    # import secret key
    input_secretkey = driver.find_element(By.ID, "create-new-vault__srp")
    input_secretkey.send_keys(secret_key)

    # import password
    new_password = driver.find_element(By.ID, "password")
    new_password.send_keys(password)
    cfm_password = driver.find_element(By.ID, "confirm-password")
    cfm_password.send_keys(password)

    driver.find_element(By.ID, "create-new-vault__terms-checkbox").click()
    driver.find_element(By.CLASS_NAME, "create-new-vault__submit-button").click()

    # wait for confirmation of imported wallet
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "end-of-flow")))
    print("MetaMask account imported")


def navigate_mm(driver, nav):
    # first page
    wait_and_click(driver, By.CLASS_NAME, "first-time-flow__button")

    # choose between import/create new
    if nav == "new":
        wait_and_click(driver, By.XPATH, "//button[contains(., 'Create a Wallet')]")
    else:
        wait_and_click(driver, By.XPATH, "//button[contains(., 'Import wallet')]")

    # send report page
    wait_and_click(driver, By.CLASS_NAME, "page-container__footer-button")


def connect_pegaxy_app(driver):
    print("Connecting to Pegaxy")
    wait = WebDriverWait(driver, wait_time)

    # click on connect on the menu bar
    wait_and_click(driver, By.CLASS_NAME, "link-connect")

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "bx-login")))
    network = driver.find_element(By.CLASS_NAME, "login-header").text
    driver.find_element(By.XPATH, "//span[contains(., 'Connect Metamask')]").click()

    return network


def pin_mm_plugin():
    pyautogui.click(938, 83)
    time.sleep(1)
    pyautogui.click(888, 211)
    time.sleep(1)
    pyautogui.click(938, 83)


def approve_mm(driver, switch_network):
    wait_and_click(driver, By.CLASS_NAME, "btn-primary")

    wait_and_click(driver, By.XPATH, "//button[contains(., 'Connect')]")
    time.sleep(3)
    add_network = check_element_exist(driver, By.XPATH, "//button[contains(., 'Approve')]")
    if add_network:
        print("Adding network to MetaMask")
        add_network_mm(driver)

    if switch_network:
        print("Switching Network")
        switch_network_mm(driver)

    signature_mm(driver)


def switch_network_mm(driver):
    # switch network
    wait_and_click(driver, By.XPATH, "//button[contains(., 'Switch network')]")


def add_network_mm(driver):
    # add network to metamask
    wait_and_click(driver, By.XPATH, "//button[contains(., 'Approve')]")


def signature_mm(driver):
    wait = WebDriverWait(driver, wait_time)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[2])

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "request-signature__container")))
    print("Checking request origin", driver.find_element(By.CLASS_NAME, "request-signature__origin").text)
    if driver.find_element(By.CLASS_NAME, "request-signature__origin").text in PegaxyWebsite:
        print("requesting signature")
        driver.find_element(By.XPATH, "//button[contains(., 'Sign')]").click()
