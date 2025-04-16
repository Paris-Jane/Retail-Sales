# LIBRARIES
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plot
# optional, but you could use them:
#   import openpyxl
#   from sqlalchemy.sql import text
import psycopg2


df = pd.read_excel('Retail_Sales_Data.xlsx')

username = 'postgres'
password = input("What is your postgres password? ")
host = 'localhost'
port = '5432' # CHECK YOUR OWN PORT
database = 'IS303'
# You had to manually create the is303 database
# Create the connection string to speak with the is303 database
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
# Establish the connection to the database and store to variable
conn = engine.connect()
# Overwrite the dataframe data to a table called sales
# Use the current database connection in conn
# # index=False says to NOT bring in the dataframe row number
df.to_sql('sale', conn, if_exists='replace', index=False)

while True:
    choice = input("If you want to import data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ")

    # PART 1
    if choice == '1' : 
        # Fix Name column
        split_names  = df["name"].str.split("_", expand = True)
        df.insert(1,"first_name",split_names[0])
        df.insert(2,"last_name",split_names[1])
        df.drop(columns=['name'], inplace=True)

        # Fix Category column
        productCategoriesDict = {
                'Camera': 'Technology',
                'Laptop': 'Technology',
                'Gloves': 'Apparel',
                'Smartphone': 'Technology',
                'Watch': 'Accessories',
                'Backpack': 'Accessories',
                'Water Bottle': 'Household Items',
                'T-shirt': 'Apparel',
                'Notebook': 'Stationery',
                'Sneakers': 'Apparel',
                'Dress': 'Apparel',
                'Scarf': 'Apparel',
                'Pen': 'Stationery',
                'Jeans': 'Apparel',
                'Desk Lamp': 'Household Items',
                'Umbrella': 'Accessories',
                'Sunglasses': 'Accessories',
                'Hat': 'Apparel',
                'Headphones': 'Technology',
                'Charger': 'Technology'}
        df["category"] = df["product"].map(productCategoriesDict)

        # INSERT STEP 4: Save the results as a table called ‘sale’ in your is303 postgres database.
        
        print("You've imported the excel file into your postgres database.")

    # PART 2
    elif choice == '2' : 
        # Step 1: Print out: “The following are all the categories that have been sold:” 
        print("The following are all the categories that have been sold:")
        # Step 2: Print out each of the categories stored in your database from the ‘sale’ table with a number preceding it. You can’t just hardcode the categories in, your program must read them from the database. It should look like this:
        
        query = "SELECT DISTINCT category FROM sale ORDER BY category;"
        
        categories_df = pd.read_sql( text(query), conn)

        lst_categories = []
        for iCount, category in enumerate(categories_df['category'], start=1):
            # Display the counter and the value for the category
            print(f"{iCount}: {category}")
            lst_categories.append(category)
            
            # 1: Technology
            # 2: Apparel
            # 3: Accessories
            # 4: Household Items
            # 5: Stationery
        # Step 3: Print out: “Please enter the number of the category you want to see summarized: “
        category_choice = int(input("Please enter the number of the category you want to see summarized: "))
        category_name = lst_categories[category_choice - 1]
        query = """
            SELECT product, SUM(total_price) AS total_sales, AVG(total_price) AS average_sales, SUM(quantity_sold) AS quantity_sold
            FROM sale
            WHERE category = :category
            GROUP BY product"""

        df = pd.read_sql( text(query), conn, params={"category": category_name})
        print(f"Sum of total sales: {round(df['total_sales'].sum(),2)}")
        print(f"Average sale amount: {round(df['average_sales'].mean(),2)}")
        print(f"Total units sold: {round(df['quantity_sold'].sum(),0)}")

            # Step 4: Then, for the entered category, calculate and display the sum of total sales, the average sale amount, and the total units sold.
            # Step 5: Then, display a bar chart with the x axis as the products in that category and the y axis as the sum of the total sales of that product.
                # a.	The title of the chart should be “Total Sales by Product in Category (but put the actual category name)
                # b.	The x label should be “Product”, the y label should be “Total Sales”
        
        # Using group by on the product to get one row for each product,
        # and then calculating the sum of total prices for each of those products

        # creating the chart
        df.plot(kind='bar')  # creates the chart
        plot.title(f"Total Sales in {df}")  # adds title to the top of the chart
        plot.xlabel("Product")  # label for the x-axis
        plot.ylabel("Total Sales")  # label for the y-axis
        plot.show()  # makes the chart pop up on the screen


    else : 
        print("Closing the program")
        break