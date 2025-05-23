from selenium import webdriver
from selenium.webdriver.common.by import By
from time import perf_counter

driver = webdriver.Chrome()
start_time = perf_counter() 
driver.get("http://localhost:8080")
end_time = perf_counter()

print(f"Page load time: {end_time - start_time:.3f}s")
driver.quit()