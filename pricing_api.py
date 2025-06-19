# pricing_api.py

from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Your Existing Functions ===

def get_flipkart_price(product_url, driver_path):
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(product_url)
        time.sleep(2)
        try:
            close_button = driver.find_element(By.XPATH, '//button[contains(text(),"X")]')
            close_button.click()
        except:
            pass
        
        wait = WebDriverWait(driver, 10)
        price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"Nx9bqj")]')))
        
        price_text = price_element.text
        price_numeric = int(price_text.replace('₹', '').replace(',', ''))
        return price_numeric

    except Exception as e:
        print("Error extracting price:", e)
        return None
    finally:
        driver.quit()

def compute_purchase_probability(user_row, offered_price, competitor_price):
    base_prob = 0.35
    w1 = 0.025
    w2 = 0.01
    w3 = 0.15
    w4 = 0.2
    
    price_penalty = max(0, (offered_price - competitor_price) / 1000)
    cart_flag = 1 if (user_row['Added_to_Cart'] == 1 or user_row['Abandoned'] == 1) else 0
    
    p = base_prob + w1 * user_row['Viewed_Times'] + w2 * user_row['Total_Time_Spent(min)'] + w3 * cart_flag - w4 * price_penalty
    p = max(0, min(p, 1))
    return p

def calculate_final_price(row, optimal_price):
    discounts = []
    if row['Viewed_Times'] > 15:
        discounts.append(100)
    if row['Total_Time_Spent(min)'] > 10:
        discounts.append(150)
    if row['Added_to_Cart'] == 1 and row['Abandoned'] == 1:
        discounts.append(200)
    if row['Num_Sessions'] > 4:
        discounts.append(0)
    if row['Device_Type'] == 'Mobile':
        discounts.append(50)
    best_discount = max(discounts) if discounts else 0
    final_price = optimal_price - best_discount
    return final_price

# === FastAPI App ===

app = FastAPI()

# === Configuration ===

product_url = "https://www.flipkart.com/samsung-galaxy-f05-twilight-blue-64-gb/p/itm84a914081ab93"
driver_path = r"C:\WebDriver-2\chromedriver-win64\chromedriver.exe"

df_f05 = pd.read_excel(r'D:\Rishi\JINDAL Academics\ALP-2\GalaxyF05_UserBehavior_Dataset.xlsx')
df_leads = pd.read_excel(r'D:\Rishi\JINDAL Academics\ALP-2\GalaxyF05_UserLeads_Dataset.xlsx')

epsilon = 0.1

@app.get("/")
def read_root():
    return {"message": "Dynamic Pricing API is running ✅"}

# === Core Bandit Function ===
def run_bandit(flipkart_price):
    arm_1 = flipkart_price - 100
    arm_2 = flipkart_price - 150
    arm_3 = flipkart_price - 200
    price_arms = [arm_1, arm_2, arm_3]
    num_arms = len(price_arms)
    
    counts = [0] * num_arms
    rewards = [0] * num_arms
    
    # Warm start
    for i in range(num_arms):
        row = df_f05.iloc[i]
        chosen_arm = i
        offered_price = price_arms[chosen_arm]
        p_purchase = compute_purchase_probability(row, offered_price, flipkart_price)
        reward = 1 if random.random() < p_purchase else 0
        counts[chosen_arm] += 1
        rewards[chosen_arm] += reward
    
    # Main Bandit
    for index in range(num_arms, len(df_f05)):
        row = df_f05.iloc[index]
        if random.random() < epsilon:
            chosen_arm = random.randint(0, num_arms - 1)
        else:
            avg_rewards = [rewards[i] / counts[i] if counts[i] > 0 else 0 for i in range(num_arms)]
            chosen_arm = avg_rewards.index(max(avg_rewards))
        
        offered_price = price_arms[chosen_arm]
        p_purchase = compute_purchase_probability(row, offered_price, flipkart_price)
        reward = 1 if random.random() < p_purchase else 0
        counts[chosen_arm] += 1
        rewards[chosen_arm] += reward
    
    avg_rewards_pct = [ (rewards[i] / counts[i])*100 if counts[i]>0 else 0 for i in range(num_arms) ]
    best_arm_index = avg_rewards_pct.index( max(avg_rewards_pct) )
    optimal_price = price_arms[best_arm_index]
    
    return optimal_price

# === Endpoint 1: Existing Lead ===
@app.get("/get-price-existing")
def get_price_existing(user_id: str):
    flipkart_price = get_flipkart_price(product_url, driver_path)
    optimal_price = run_bandit(flipkart_price)
    
    user_row = df_leads[df_leads['UserID'] == user_id]
    if user_row.empty:
        return {"error": "User ID not found"}
    
    user_row = user_row.iloc[0]
    final_price = calculate_final_price(user_row, optimal_price)
    
    return {
        "user_id": user_id,
        "optimal_price": optimal_price,
        "final_price": final_price
    }

# === Endpoint 2: New Lead (POST) ===

class NewLead(BaseModel):
    Viewed_Times: int
    Total_Time_Spent_min: float
    Added_to_Cart: int
    Abandoned: int
    Num_Sessions: int
    Device_Type: str  # 'Mobile' or 'Desktop'

@app.post("/get-price-new")
def get_price_new(lead: NewLead):
    flipkart_price = get_flipkart_price(product_url, driver_path)
    optimal_price = run_bandit(flipkart_price)
    
    # Build pseudo-row from input
    discounts = []
    if lead.Viewed_Times > 15:
        discounts.append(100)
    if lead.Total_Time_Spent_min > 10:
        discounts.append(150)
    if lead.Added_to_Cart == 1 and lead.Abandoned == 1:
        discounts.append(200)
    if lead.Num_Sessions > 4:
        discounts.append(0)
    if lead.Device_Type == 'Mobile':
        discounts.append(50)
    best_discount = max(discounts) if discounts else 0
    final_price = optimal_price - best_discount
    
    return {
        "input_lead": lead.dict(),
        "optimal_price": optimal_price,
        "final_price": final_price
    }
