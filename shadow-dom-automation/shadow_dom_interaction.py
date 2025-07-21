from selenium import webdriver
from selenium.webdriver.common.by import By
import time


# def interact_with_dasoertliche(shadow_host_selector, shadow_element_selector):
#     driver = (
#         webdriver.Chrome()
#     )  # Initialize the WebDriver (make sure to have the correct driver installed)
#     driver.implicitly_wait(10)  # Set an implicit wait time
#     driver.get("https://example.com")  # Replace with the actual URL
#     # Locate the shadow host element
#     shadow_host = driver.find_element(By.CSS_SELECTOR, shadow_host_selector)

#     # Access the shadow root
#     shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

#     # Locate the shadow DOM element within the shadow root
#     shadow_element = shadow_root.find_element(By.CSS_SELECTOR, shadow_element_selector)

#     # Perform actions on the shadow DOM element (e.g., click, send keys)
#     shadow_element.click()

#     # Optionally, wait for a while to observe the interaction
#     time.sleep(2)


driver = (
    webdriver.Chrome()
)  # Initialize the WebDriver (make sure to have the correct driver installed)
driver.implicitly_wait(10)  # Set an implicit wait time
driver.get("https://www.dasoertliche.de/")  # Replace with the actual URL
time.sleep(5)  # Wait for the page to load
accept_button = driver.execute_script(
    'document.querySelector("#cmpwrapper").shadowRoot.querySelector("#cmpwelcomebtnyes > a")'
)
driver.execute_script("arguments[0].click();", accept_button)
# if accept_button:
#     accept_button.click()  # Click the accept button if it exists
#     time.sleep(2)  # Wait for the action to complete
