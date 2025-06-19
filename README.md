**# Dynamic-Pricing-Engine-for-based-on-Customer-Behavior-and-Compertitor-Scraping**
In this Project, I have built the Underlying Logic and Backend for  Dynamic Pricing Engine which takes into consideration User Interaction data with an E-commerce site, compares competitor price and optimises the price offered for the same product by me.

**Find all the resources, API code, Jupyter notebook code, datasets etc needed to verify and check functioning of project.**

**Contact me in case of any queries** via LinkedIN

**Project Sequence and Description**
1) I have assumed to have a Ecommerce platform and I sell a variety of products. My aim is to outsell my competition at every juncture and so I have build a Dynamic pricing engine which will offer customers a good price unique to them based on their behaviour and intrest level I gauge in the product and competitor Pricing for it.
2) Weights associated with P(Purchase) equation and function is assumed and can be altered.
3) I have created a 2 synthetic datasets. One has details of customers interacting with site and maybe purchasing the product. Other is dataset for new customers who are leads.
4) I am focussing this project and pricing engine for only one product **"SAMSUNG GALAXY F05 TWILIGHT BLUE"**

**Core Concepts Flow:**
1) I have taken "FlipKart" as my competitor. So I came up with a code which uses Selenium Chromedriver to simulate a user browsing experience on Chrome - Navigate to the product page and scrape especially and only the product's price there.
2) Then I use "Epsilon Greedy" Bandit Algorithm for the Optimal Price Choosing Strategy. I created 3 arms of price for this which are lesser than competitor and the Code/algorithm arrives at them most accepted Price based on success with Rewards( Expolre and Exploit of Bandit)-----------(I used 3 arms with lesser prices so that, the conversion rate will be high, we target higher sales revenue than profit , goodwill, site recognition and more. All this is okay, as it is hypothetical and evenin reality as long as profitability is not affected according to the Marketing and Sales Division)
3) From this price, I developed a Rule based Pricing system which analyses a lead's behaviour based on certain KPIs(column headers in the dataset) and offers neccessary changes and customised pricing for each lead till they are nudged to make a purhcase. Also a if timestamp is not recent(filtered with threshold) , a lead is no longer considered a lead.
4) 4 Finally this engine needs to run "Near Real Time", But I can't scrape Flipkart so many times without being banned. So I placed the entire pricing logic in a "While True" loop which will refresh and run the code every 30 minutes and dynamically change the price of the product for the leads based on any updates.
5) Finally, I Wrapped the pricing logic into a small web service (API) → so that other systems (like a website, app, or dashboard) can call it anytime and get back the latest price.-----------Using VScode
6) **To run API:**
----->To run API: python -m uvicorn pricing_api:app --reload

----->To check API: http://127.0.0.1:8000

----->To check particular lead: (Say lead45) - http://127.0.0.1:8000/get-price-existing?user_id=Lead045 


----->To check price offered for a totally New Lead: http://127.0.0.1:8000/get-price-new in PostmanAPI in JSON script
Eg) {
    "Viewed_Times": 20,
    "Total_Time_Spent_min": 12,
    "Added_to_Cart": 1,
    "Abandoned": 1,
    "Num_Sessions": 3,
    "Device_Type": "Mobile"
}

**IMPROVEMENTS**
1) I can run this engine and its logic( Scraping + Bandit + Rule based logic) as backend behind a UI made with FLASK or STREAMLIT and only vary the product URL -  This would work for any product on Flip-kart.
2) There are many things variable here: Probability weights, prices offered, Rules in the Rule based system etc to suit application needs.
